"""Servidor A2A: expone el sistema multiagente jerárquico de Parachute S.A.
como un solo agente A2A, con una skill por funcionalidad (FAQs, clima y
citas). Los especialistas usan las herramientas del servidor MCP
(src/servidor_mcp.py), que debe estar corriendo antes de iniciar este.

Cada mensaje recibido se procesa como una Task: submitted -> working ->
completed (con la respuesta como artifact) o failed. El historial de la
conversación se conserva por context_id.
"""

import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from a2a.helpers import new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import DEFAULT_RPC_URL, TransportProtocol
from agents import Agent, RunHooks, Runner
from agents.mcp import MCPServerStreamableHttp
from starlette.applications import Starlette

from agente_jerarquico import crear_supervisor_global, filtrar_herramientas_mcp
from common.cli import MAX_INTENTOS

A2A_HOST = os.getenv("A2A_HOST", "127.0.0.1")
A2A_PORT = int(os.getenv("A2A_PORT", "9999"))
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8001/mcp")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("ParachuteA2A")


class HooksDeLog(RunHooks):
    """Registra en el log las delegaciones del supervisor global."""

    async def on_agent_start(self, context, agent: Agent) -> None:
        logger.info("Agente iniciado: %s", agent.name)

    async def on_tool_start(self, context, agent: Agent, tool) -> None:
        logger.info("%s delega en: %s", agent.name, tool.name)

    async def on_tool_end(self, context, agent: Agent, tool, result) -> None:
        logger.info("%s recibió respuesta de: %s", agent.name, tool.name)


class ParachuteAgentExecutor(AgentExecutor):
    """Envuelve el sistema multiagente para que responda peticiones A2A."""

    def __init__(self, agente: Agent):
        self.agente = agente
        self.historiales: dict[str, list] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        pregunta = context.get_user_input()

        tarea = context.current_task
        if tarea is None:
            tarea = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(tarea)

        logger.info(
            "Task %s recibida (context %s): %r", tarea.id, tarea.context_id, pregunta
        )

        updater = TaskUpdater(event_queue, tarea.id, tarea.context_id)
        await updater.start_work(
            new_text_message(
                "Procesando consulta...",
                context_id=tarea.context_id,
                task_id=tarea.id,
            )
        )

        historial = self.historiales.get(tarea.context_id, [])
        entrada = historial + [{"role": "user", "content": pregunta}]

        # Mismo esquema de reintentos que el CLI (ver common/cli.py).
        inicio = time.perf_counter()
        ultimo_error = None
        for intento in range(1, MAX_INTENTOS + 1):
            try:
                resultado = await Runner.run(self.agente, entrada, hooks=HooksDeLog())
                break
            except Exception as error:
                ultimo_error = error
                logger.warning(
                    "Task %s: intento %d/%d falló: %s",
                    tarea.id, intento, MAX_INTENTOS, error,
                )
        else:
            logger.error("Task %s falló: %s", tarea.id, ultimo_error)
            await updater.failed(
                new_text_message(
                    f"Error: {ultimo_error}",
                    context_id=tarea.context_id,
                    task_id=tarea.id,
                )
            )
            return

        respuesta = str(resultado.final_output)
        self.historiales[tarea.context_id] = resultado.to_input_list()

        await updater.add_artifact([new_text_part(respuesta)], name="respuesta")
        await updater.complete()
        logger.info(
            "Task %s completada en %.2f s", tarea.id, time.perf_counter() - inicio
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        logger.info("Task %s cancelada", context.task_id)
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel()


agent_card = AgentCard(
    name="Parachute S.A.",
    description=(
        "Agente de atención al cliente de Parachute S.A.: responde preguntas "
        "frecuentes, evalúa si el clima de una fecha es apto para saltar y "
        "agenda citas de salto."
    ),
    version="1.0.0",
    supported_interfaces=[
        AgentInterface(
            url=f"http://{A2A_HOST}:{A2A_PORT}{DEFAULT_RPC_URL}",
            protocol_binding=TransportProtocol.JSONRPC,
        )
    ],
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="preguntas_frecuentes",
            name="Preguntas frecuentes",
            description=(
                "Responde preguntas frecuentes sobre Parachute S.A. usando su "
                "base de conocimientos."
            ),
            tags=["faq", "atencion al cliente"],
            examples=["¿Cuál es el peso máximo permitido para saltar?"],
        ),
        AgentSkill(
            id="consultar_clima",
            name="Consultar clima",
            description=(
                "Evalúa si el pronóstico del clima de una fecha es apto para "
                "saltar según los criterios de seguridad de la empresa."
            ),
            tags=["clima", "pronostico"],
            examples=["¿El 25 de octubre es un buen día para saltar?"],
        ),
        AgentSkill(
            id="agendar_cita",
            name="Agendar cita",
            description=(
                "Agenda una cita de salto en la fecha solicitada, verificando "
                "antes que el clima sea seguro."
            ),
            tags=["citas", "agendamiento"],
            examples=["Quiero agendar un salto para el 25 de octubre a nombre de Ana."],
        ),
    ],
)

servidor_mcp = MCPServerStreamableHttp(
    name="ParachuteMCP",
    params={"url": MCP_URL},
    cache_tools_list=True,
    tool_filter=filtrar_herramientas_mcp,
    # La primera búsqueda de FAQs carga el modelo de embeddings en el servidor MCP.
    client_session_timeout_seconds=60,
)

request_handler = DefaultRequestHandler(
    agent_executor=ParachuteAgentExecutor(crear_supervisor_global(servidor_mcp)),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)


@asynccontextmanager
async def lifespan(app: Starlette):
    logger.info("Conectando al servidor MCP en %s", MCP_URL)
    async with servidor_mcp:
        logger.info("Conectado al servidor MCP")
        yield
    logger.info("Desconectado del servidor MCP")


app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(request_handler, rpc_url=DEFAULT_RPC_URL),
    ],
    lifespan=lifespan,
)


if __name__ == "__main__":
    logger.info("Iniciando servidor A2A en http://%s:%d", A2A_HOST, A2A_PORT)
    uvicorn.run(app, host=A2A_HOST, port=A2A_PORT)
