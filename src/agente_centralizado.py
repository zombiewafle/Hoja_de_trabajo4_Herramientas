"""Arquitectura centralizada: un único agente controla directamente las 3
herramientas (FAQ, clima, citas). No existe ningún tipo de delegación entre
agentes: toda la lógica de decisión está en un solo punto de control.
"""

from agents import Agent, ModelSettings

from common import agent_tools
from common.cli import run_cli
from common.groq_model import MODEL

INSTRUCCIONES = """
Eres el agente de atención al cliente de Parachute S.A.

Cuentas con tres herramientas:
- buscar_faq_tool: para responder preguntas frecuentes.
- consultar_clima_tool: para evaluar si una fecha es apta para saltar.
- calendarizar_cita_tool: para agendar una cita (verifica el clima automáticamente).

Para responder, siempre debes usar la herramienta que corresponda al tipo de
consulta del usuario. No respondas utilizando conocimiento propio ni inventes
información.

Después de recibir el resultado de una herramienta:
- utiliza únicamente esa información;
- si la herramienta indica que no encontró información o que hay un error,
  indícalo claramente al usuario;
- responde en español de forma clara y breve.
"""

agente = Agent(
    name="AgenteParachute",
    instructions=INSTRUCCIONES,
    tools=[
        agent_tools.buscar_faq_tool,
        agent_tools.consultar_clima_tool,
        agent_tools.calendarizar_cita_tool,
    ],
    model=MODEL,
    model_settings=ModelSettings(tool_choice="required"),
)


def main() -> None:
    run_cli(agente)


if __name__ == "__main__":
    main()
