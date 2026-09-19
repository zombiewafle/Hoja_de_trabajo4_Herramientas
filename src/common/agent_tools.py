from agents import function_tool

from . import citas_service, faq_service, weather_service


@function_tool
def buscar_faq_tool(pregunta: str) -> dict:
    """Busca información relevante en la base de conocimientos de preguntas
    frecuentes de Parachute S.A.

    Args:
        pregunta: La pregunta del usuario que debe buscarse en la base de conocimientos.
    """
    return faq_service.buscar_faq(pregunta)


@function_tool
def consultar_clima_tool(fecha: str) -> dict:
    """Consulta el pronóstico del clima en la zona de aterrizaje de Parachute S.A.
    para una fecha dada y evalúa si es apta para saltar, según los criterios de
    seguridad de la empresa.

    Args:
        fecha: Fecha a consultar, en formato YYYY-MM-DD.
    """
    return weather_service.consultar_clima(fecha)


@function_tool
def calendarizar_cita_tool(fecha: str, nombre_cliente: str = "Cliente") -> dict:
    """Calendariza una cita de salto para el cliente en la fecha solicitada.
    Antes de confirmar, verifica automáticamente el clima previsto para esa
    fecha y rechaza la cita si las condiciones no son seguras.

    Args:
        fecha: Fecha deseada para la cita, en formato YYYY-MM-DD.
        nombre_cliente: Nombre del cliente que solicita la cita.
    """
    return citas_service.calendarizar_cita(fecha, nombre_cliente)
