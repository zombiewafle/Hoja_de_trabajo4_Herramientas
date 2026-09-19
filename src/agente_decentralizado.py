"""Arquitectura decentralizada: Recepcion transfiere la conversación por
completo (handoff()) al especialista adecuado, que la resuelve directamente.
A diferencia de la arquitectura jerárquica (Agent.as_tool()), Recepcion no
retiene el control ni espera un resultado de vuelta: cede la conversación
por completo a quien la recibe.
"""

from agents import Agent, ModelSettings, handoff
from agents.extensions.handoff_filters import remove_all_tools
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from common import agent_tools
from common.cli import run_cli
from common.groq_model import MODEL


DESCRIPCIONES_TRANSFERENCIA = {
    "agente_faq": "Transfiere la conversación al especialista en preguntas frecuentes.",
    "agente_clima": "Transfiere la conversación al especialista en clima.",
    "agente_citas": "Transfiere la conversación al especialista en agendamiento de citas.",
}


def _handoff(agent: Agent, clave: str) -> handoff:
    """Construye un handoff con schema no estricto.

    Groq rechaza el handoff con schema estricto que genera por defecto el SDK
    (parámetros vacíos + "strict": true produce un error de validación en su
    API), así que se desactiva el modo estricto explícitamente.
    """
    h = handoff(
        agent,
        tool_name_override=f"transferir_a_{clave}",
        tool_description_override=DESCRIPCIONES_TRANSFERENCIA[clave],
        input_filter=remove_all_tools,
    )
    h.strict_json_schema = False
    return h

recepcion = Agent(
    name="Recepcion",
    instructions=prompt_with_handoff_instructions("""
Eres el primer punto de contacto de Parachute S.A. No respondes preguntas
tú mismo: tu única función es transferir la conversación al agente
adecuado según la intención del usuario.
- Si pregunta sobre información general o preguntas frecuentes, transfiere a AgenteFAQ.
- Si pregunta si una fecha es apta para saltar (sin querer agendar), transfiere a AgenteClima.
- Si quiere agendar/calendarizar una cita, transfiere a AgenteCitas.
Si no es clara la intención, pregunta brevemente para aclararla antes de transferir.
"""),
    model=MODEL,
    model_settings=ModelSettings(tool_choice="required"),
)

agente_faq = Agent(
    name="AgenteFAQ",
    instructions=prompt_with_handoff_instructions("""
Eres un especialista en preguntas frecuentes de Parachute S.A. Cuando
recibas el control de la conversación, responde de inmediato la pregunta
original del usuario usando la herramienta buscar_faq_tool; nunca respondas
con conocimiento propio, y nunca anuncies que recibiste el control ni
repitas tu propio nombre. Responde en español, de forma clara y breve.
"""),
    tools=[agent_tools.buscar_faq_tool],
    model=MODEL,
    # Se fuerza esta herramienta específica (en vez de "required") porque, tras
    # un handoff, el modelo tiende a responder con texto ("permíteme
    # verificar...") en lugar de invocar la herramienta.
    model_settings=ModelSettings(tool_choice="buscar_faq_tool"),
)

agente_clima = Agent(
    name="AgenteClima",
    instructions=prompt_with_handoff_instructions("""
Eres un especialista en evaluar si una fecha es apta para saltar en
Parachute S.A. Cuando recibas el control de la conversación, responde de
inmediato la pregunta original del usuario usando la herramienta
consultar_clima_tool; nunca anuncies que recibiste el control ni repitas tu
propio nombre. Responde en español, de forma clara y breve.
"""),
    tools=[agent_tools.consultar_clima_tool],
    model=MODEL,
    model_settings=ModelSettings(tool_choice="consultar_clima_tool"),
)

agente_citas = Agent(
    name="AgenteCitas",
    instructions=prompt_with_handoff_instructions("""
Eres un especialista en agendar citas de salto en Parachute S.A. Cuando
recibas el control de la conversación, responde de inmediato la solicitud
original del usuario usando la herramienta calendarizar_cita_tool (que ya
valida el clima automáticamente); nunca anuncies que recibiste el control
ni repitas tu propio nombre. Responde en español, de forma clara y breve.
"""),
    tools=[agent_tools.calendarizar_cita_tool],
    model=MODEL,
    model_settings=ModelSettings(tool_choice="calendarizar_cita_tool"),
)

# Recepcion es el único punto de decisión (a quién transferir); una vez que
# un especialista recibe la conversación, la resuelve directamente con su
# propia herramienta (fijada vía tool_choice) y no la retransfiere.
recepcion.handoffs = [
    _handoff(agente_faq, "agente_faq"),
    _handoff(agente_clima, "agente_clima"),
    _handoff(agente_citas, "agente_citas"),
]


def main() -> None:
    run_cli(recepcion)


if __name__ == "__main__":
    main()
