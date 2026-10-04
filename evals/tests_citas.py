"""Casos de prueba de agendamiento de citas.

Se generan en Python porque las fechas deben ser relativas a hoy (Open-Meteo
solo pronostica 16 días) y porque el resultado esperado depende del
pronóstico real, que se consulta al generar los casos.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from common import weather_service
from common.citas_service import ESTADO_POR_VEREDICTO


def _fecha(dias: int) -> str:
    return (date.today() + timedelta(days=dias)).isoformat()


# Regex (determinística) que debe aparecer en la respuesta según el resultado.
REGEX_ESTADO = {
    "confirmada": "[Cc]onfirmad",
    "marginal": "[Mm]arginal",
    "rechazada": "[Rr]echazad[ao]|[Nn]o\s+(es\s+posible|se\s+puede|puedo|podemos|puede\s+confirmarse)",
}
REGEX_VEREDICTO = {
    "ideal": "[Ii]deal|[Aa]pt[oa]|[Bb]uen",
    "marginal": "[Mm]arginal",
    "no_seguro": "[Nn]o (es )?segur|[Pp]rohibid",
}


def _llamo(nombre: str, fecha: str) -> dict:
    return {"type": "javascript", "value": "file://herramientas.js:llamo", "config": {"nombre": nombre, "fecha": fecha}}


def _no_llamo(nombre: str) -> dict:
    return {"type": "javascript", "value": "file://herramientas.js:noLlamo", "config": {"nombre": nombre}}


def generate_tests(config=None):
    fecha_ok = _fecha(3)
    fecha_lejana = _fecha(30)
    fecha_pasada = _fecha(-1)
    fecha_clima = _fecha(5)

    pronostico_ok = weather_service.consultar_clima(fecha_ok)
    estado_ok = ESTADO_POR_VEREDICTO[pronostico_ok["veredicto"]]
    pronostico_clima = weather_service.consultar_clima(fecha_clima)

    # El clima siempre debe verificarse para la fecha pedida; solo se exige
    # agendar si el clima lo permite (si no, basta con rechazar).
    asserts_tool_ok = [_llamo("consultar_clima", fecha_ok)]
    if estado_ok != "rechazada":
        asserts_tool_ok.append(_llamo("calendarizar_cita", fecha_ok))

    return [
        {
            "description": "Citas - agendar dentro del rango de pronóstico",
            "vars": {"pregunta": f"Quiero agendar una cita de salto para el {fecha_ok}, mi nombre es Ana López."},
            "assert": [
                *asserts_tool_ok,
                {"type": "regex", "value": REGEX_ESTADO[estado_ok]},
                {
                    "type": "factuality",
                    "value": f"La cita de salto para el {fecha_ok} quedó en estado '{estado_ok}' según el clima previsto.",
                },
            ],
        },
        {
            "description": "Citas - fecha fuera del rango de 16 días",
            "vars": {"pregunta": f"Quiero agendar una cita de salto para el {fecha_lejana}."},
            "assert": [
                _llamo("consultar_clima", fecha_lejana),
                {"type": "contains", "value": "16"},
                {
                    "type": "factuality",
                    "value": (
                        f"No es posible agendar la cita para el {fecha_lejana} porque el pronóstico "
                        "del clima solo está disponible hasta 16 días."
                    ),
                },
            ],
        },
        {
            "description": "Citas - fecha en el pasado",
            "vars": {"pregunta": f"Agéndame una cita de salto para el {fecha_pasada}."},
            "assert": [
                _llamo("consultar_clima", fecha_pasada),
                {"type": "regex", "value": "pas(ó|o|ado|ada)|anterior|futur"},
                {
                    "type": "factuality",
                    "value": f"No se puede agendar la cita para el {fecha_pasada} porque esa fecha ya pasó.",
                },
            ],
        },
        {
            "description": "Citas - solo consultar clima (no debe agendar)",
            "vars": {"pregunta": f"¿El {fecha_clima} es un buen día para saltar? Solo quiero saber el clima, no agendar."},
            "assert": [
                _llamo("consultar_clima", fecha_clima),
                _no_llamo("calendarizar_cita"),
                {"type": "regex", "value": REGEX_VEREDICTO[pronostico_clima["veredicto"]]},
                {
                    "type": "factuality",
                    "value": (
                        f"El veredicto para saltar el {fecha_clima} es '{pronostico_clima['veredicto']}'. "
                        f"Razones: {' '.join(pronostico_clima['razones'])}"
                    ),
                },
            ],
        },
    ]
