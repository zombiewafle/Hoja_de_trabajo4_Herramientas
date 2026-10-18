"""Interfaz de terminal como cliente A2A: obtiene la Agent Card del servidor
A2A (src/servidor_a2a.py), muestra sus skills y envía cada pregunta como un
mensaje A2A. Todas las preguntas de la sesión comparten el mismo context_id,
así el agente recuerda la conversación.
"""

import asyncio
import os
import uuid

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

A2A_URL = os.getenv("A2A_URL", "http://127.0.0.1:9999")

# El sistema multiagente puede tardar varios segundos en responder.
TIMEOUT_SEGUNDOS = 180


def _imprimir_respuesta(respuesta) -> None:
    """Imprime un evento (message, task, status o artifact) recibido del servidor."""
    if respuesta.HasField("message"):
        print(get_message_text(respuesta.message))

    if respuesta.HasField("artifact_update"):
        print(get_artifact_text(respuesta.artifact_update.artifact))

    if respuesta.HasField("status_update"):
        estado = respuesta.status_update.status
        if estado.state == TaskState.TASK_STATE_FAILED:
            mensaje = get_message_text(estado.message) if estado.HasField("message") else ""
            print(mensaje or "Error: el agente no pudo responder.")
        elif estado.HasField("message"):
            print(f"[{TaskState.Name(estado.state)}] {get_message_text(estado.message)}")


async def main() -> None:
    async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as cliente_http:
        card = await A2ACardResolver(cliente_http, A2A_URL).get_agent_card()

        print(f"Conectado a {card.name}: {card.description}")
        print("Skills disponibles:")
        for skill in card.skills:
            print(f"- {skill.name}: {skill.description}")
        print("Para salir, escribe Bye.\n")

        cliente = await create_client(
            card, ClientConfig(httpx_client=cliente_http, streaming=True)
        )
        context_id = str(uuid.uuid4())

        async with cliente:
            while True:
                pregunta = await asyncio.to_thread(input, "> ")

                if pregunta.lower() == "bye":
                    break

                if not pregunta.strip():
                    print("Por favor, escribe una pregunta.")
                    continue

                mensaje = new_text_message(
                    pregunta, context_id=context_id, role=Role.ROLE_USER
                )

                try:
                    async for respuesta in cliente.send_message(
                        SendMessageRequest(message=mensaje)
                    ):
                        _imprimir_respuesta(respuesta)
                except Exception as error:
                    print("Error de comunicación con el servidor A2A:", error)


if __name__ == "__main__":
    asyncio.run(main())
