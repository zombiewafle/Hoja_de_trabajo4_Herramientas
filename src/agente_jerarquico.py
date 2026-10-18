"""Arquitectura jerárquica: un supervisor global delega en especialistas
usando Agent.as_tool(), y uno de esos especialistas (Operaciones) es a su vez
un supervisor de otros dos agentes (Clima y Citas). Hay varios niveles de
autoridad, a diferencia de la arquitectura centralizada (un solo nivel).

Las herramientas de los especialistas pueden venir de dos fuentes:
- Locales (function_tool de common.agent_tools), usadas por el CLI y los evals.
- Un servidor MCP (src/servidor_mcp.py), usadas por el servidor A2A. En ese
  caso cada especialista solo ve su herramienta gracias a
  filtrar_herramientas_mcp.
"""

from agents import Agent, ModelSettings
from agents.mcp import MCPServer, ToolFilterContext

from common import agent_tools
from common.cli import run_cli
from common.groq_model import MODEL

# Herramienta MCP que puede usar cada especialista.
HERRAMIENTAS_MCP_POR_AGENTE = {
    "AgenteAtencionCliente": "buscar_faq",
    "AgenteClima": "consultar_clima",
    "AgenteCitas": "calendarizar_cita",
}


def filtrar_herramientas_mcp(contexto: ToolFilterContext, herramienta) -> bool:
    """Filtro dinámico del servidor MCP: cada agente solo ve su herramienta."""
    return HERRAMIENTAS_MCP_POR_AGENTE.get(contexto.agent.name) == herramienta.name


def _especialista(
    nombre: str,
    instrucciones: str,
    herramienta_local,
    servidor_mcp: MCPServer | None,
) -> Agent:
    if servidor_mcp is None:
        nombre_herramienta = herramienta_local.name
        fuente = {"tools": [herramienta_local]}
    else:
        nombre_herramienta = HERRAMIENTAS_MCP_POR_AGENTE[nombre]
        fuente = {"mcp_servers": [servidor_mcp]}

    return Agent(
        name=nombre,
        instructions=instrucciones.format(herramienta=nombre_herramienta),
        model=MODEL,
        model_settings=ModelSettings(tool_choice="required"),
        **fuente,
    )


def crear_supervisor_global(servidor_mcp: MCPServer | None = None) -> Agent:
    """Construye la jerarquía de agentes. Si se recibe servidor_mcp, los
    especialistas usan las herramientas expuestas por ese servidor; si no,
    usan las herramientas locales.
    """
    agente_atencion_cliente = _especialista(
        "AgenteAtencionCliente",
        """
Eres un especialista en preguntas frecuentes de Parachute S.A.
Responde únicamente usando la herramienta {herramienta}, nunca con
conocimiento propio. Si no se encuentra información, indícalo claramente.
Responde en español, de forma clara y breve.
""",
        agent_tools.buscar_faq_tool,
        servidor_mcp,
    )

    agente_clima = _especialista(
        "AgenteClima",
        """
Eres un especialista en evaluar si una fecha es apta para saltar en
Parachute S.A. Responde únicamente usando la herramienta
{herramienta}. Explica el veredicto y las razones que reporta la
herramienta. Responde en español, de forma clara y breve.
""",
        agent_tools.consultar_clima_tool,
        servidor_mcp,
    )

    agente_citas = _especialista(
        "AgenteCitas",
        """
Eres un especialista en agendar citas de salto en Parachute S.A. Responde
únicamente usando la herramienta {herramienta}, que ya valida el
clima automáticamente. Explica si la cita quedó confirmada, marginal o
rechazada, y por qué. Responde en español, de forma clara y breve.
""",
        agent_tools.calendarizar_cita_tool,
        servidor_mcp,
    )

    supervisor_operaciones = Agent(
        name="SupervisorOperaciones",
        instructions="""
Eres el supervisor de operaciones de Parachute S.A. No respondes preguntas
directamente: delegas en tus especialistas según la consulta del usuario.
- Usa consultar_clima_especialista si el usuario solo quiere saber si una
  fecha es apta para saltar.
- Usa agendar_cita_especialista si el usuario quiere agendar una cita.
Puedes usar ambos si la consulta lo requiere. Responde en español, de forma
clara y breve, basándote únicamente en lo que reportan tus especialistas.
""",
        tools=[
            agente_clima.as_tool(
                tool_name="consultar_clima_especialista",
                tool_description=(
                    "Consulta al especialista en clima si una fecha es apta para saltar."
                ),
            ),
            agente_citas.as_tool(
                tool_name="agendar_cita_especialista",
                tool_description=(
                    "Pide al especialista en citas que agende una cita de salto "
                    "(verifica el clima automáticamente)."
                ),
            ),
        ],
        model=MODEL,
    )

    return Agent(
        name="SupervisorGlobal",
        instructions="""
Eres el supervisor de atención al cliente de Parachute S.A. No respondes
preguntas directamente: delegas en tus especialistas según la consulta del
usuario.
- Usa consultar_atencion_cliente para preguntas frecuentes.
- Usa consultar_operaciones para temas de clima y agendamiento de citas.
Responde en español, de forma clara y breve, basándote únicamente en lo que
reportan tus especialistas. No inventes información.
""",
        tools=[
            agente_atencion_cliente.as_tool(
                tool_name="consultar_atencion_cliente",
                tool_description=(
                    "Consulta al especialista en preguntas frecuentes de Parachute S.A."
                ),
            ),
            supervisor_operaciones.as_tool(
                tool_name="consultar_operaciones",
                tool_description=(
                    "Consulta al supervisor de operaciones para temas de clima y "
                    "agendamiento de citas de salto."
                ),
            ),
        ],
        model=MODEL,
    )


# Jerarquía con herramientas locales (usada por el CLI y por los evals).
supervisor_global = crear_supervisor_global()


def main() -> None:
    run_cli(supervisor_global)


if __name__ == "__main__":
    main()
