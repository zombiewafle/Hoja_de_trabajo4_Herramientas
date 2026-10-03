"""Provider de promptfoo: ejecuta el agente jerárquico (la arquitectura
elegida en la hoja anterior) y registra las herramientas que se ejecutaron,
para poder evaluar tool execution desde las aserciones.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agents import Runner

from agente_jerarquico import supervisor_global
from common import citas_service, faq_service, weather_service
from common.cli import MAX_INTENTOS

herramientas_llamadas = []


def _registrar(modulo, nombre_funcion):
    """Reemplaza la función del servicio por una que registra cada llamada."""
    original = getattr(modulo, nombre_funcion)

    def envoltura(*args, **kwargs):
        resultado = original(*args, **kwargs)
        herramientas_llamadas.append(
            {"nombre": nombre_funcion, "args": list(args), "kwargs": kwargs, "resultado": resultado}
        )
        return resultado

    setattr(modulo, nombre_funcion, envoltura)


_registrar(faq_service, "buscar_faq")
_registrar(weather_service, "consultar_clima")
_registrar(citas_service, "calendarizar_cita")


def call_api(prompt, options, context):
    ultimo_error = None
    for _ in range(MAX_INTENTOS):
        herramientas_llamadas.clear()
        try:
            resultado = Runner.run_sync(supervisor_global, prompt)
            return {
                "output": resultado.final_output,
                "metadata": {"herramientas": list(herramientas_llamadas)},
            }
        except Exception as error:
            ultimo_error = error
    return {"error": f"El agente falló tras {MAX_INTENTOS} intentos: {ultimo_error}"}
