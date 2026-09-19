"""Arquitectura jerárquica: un supervisor global delega en especialistas
usando Agent.as_tool(), y uno de esos especialistas (Operaciones) es a su vez
un supervisor de otros dos agentes (Clima y Citas). Hay varios niveles de
autoridad, a diferencia de la arquitectura centralizada (un solo nivel).
"""

from agents import Agent, ModelSettings

from common import agent_tools
from common.cli import run_cli
from common.groq_model import MODEL

agente_atencion_cliente = Agent(
    name="AgenteAtencionCliente",
    instructions="""
Eres un especialista en preguntas frecuentes de Parachute S.A.
Responde únicamente usando la herramienta buscar_faq_tool, nunca con
conocimiento propio. Si no se encuentra información, indícalo claramente.
Responde en español, de forma clara y breve.
""",
    tools=[agent_tools.buscar_faq_tool],
    model=MODEL,
    model_settings=ModelSettings(tool_choice="required"),
)

agente_clima = Agent(
    name="AgenteClima",
    instructions="""
Eres un especialista en evaluar si una fecha es apta para saltar en
Parachute S.A. Responde únicamente usando la herramienta
consultar_clima_tool. Explica el veredicto y las razones que reporta la
herramienta. Responde en español, de forma clara y breve.
""",
    tools=[agent_tools.consultar_clima_tool],
    model=MODEL,
    model_settings=ModelSettings(tool_choice="required"),
)

agente_citas = Agent(
    name="AgenteCitas",
    instructions="""
Eres un especialista en agendar citas de salto en Parachute S.A. Responde
únicamente usando la herramienta calendarizar_cita_tool, que ya valida el
clima automáticamente. Explica si la cita quedó confirmada, marginal o
rechazada, y por qué. Responde en español, de forma clara y breve.
""",
    tools=[agent_tools.calendarizar_cita_tool],
    model=MODEL,
    model_settings=ModelSettings(tool_choice="required"),
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

supervisor_global = Agent(
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


def main() -> None:
    run_cli(supervisor_global)


if __name__ == "__main__":
    main()
