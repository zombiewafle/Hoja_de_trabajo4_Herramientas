from mcp.server import MCPServer
import logging
from common import faq_service, weather_service, citas_service


mcp = MCPServer("ParachuteMCP")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ParachuteMCP")


# Los docstrings de cada herramienta se publican como su descripción en MCP,
# que es lo que ve el LLM para decidir cómo llamarla.

@mcp.tool()
def buscar_faq(pregunta: str) -> dict:
    """Busca información relevante en la base de conocimientos de preguntas
    frecuentes de Parachute S.A.

    Args:
        pregunta: La pregunta del usuario que debe buscarse en la base de conocimientos.
    """
    logger.info("Ejecutando herramienta: buscar_faq (pregunta=%r)", pregunta)

    try:
        resultado = faq_service.buscar_faq(pregunta)
        logger.info("Finalizó herramienta: buscar_faq")
        return resultado

    except Exception:
        logger.exception("Error en buscar_faq")
        raise


@mcp.tool()
def consultar_clima(fecha: str) -> dict:
    """Consulta el pronóstico del clima en la zona de aterrizaje de Parachute S.A.
    para una fecha dada y evalúa si es apta para saltar, según los criterios de
    seguridad de la empresa.

    Args:
        fecha: Fecha a consultar, en formato YYYY-MM-DD.
    """
    logger.info("Ejecutando herramienta: consultar_clima (fecha=%r)", fecha)

    try:
        resultado = weather_service.consultar_clima(fecha)
        logger.info("Finalizó herramienta: consultar_clima")
        return resultado

    except Exception:
        logger.exception("Error en consultar_clima")
        raise


@mcp.tool()
def calendarizar_cita(fecha: str, nombre_cliente: str = "Cliente") -> dict:
    """Calendariza una cita de salto para el cliente en la fecha solicitada.
    Antes de confirmar, verifica automáticamente el clima previsto para esa
    fecha y rechaza la cita si las condiciones no son seguras.

    Args:
        fecha: Fecha deseada para la cita, en formato YYYY-MM-DD.
        nombre_cliente: Nombre del cliente que solicita la cita.
    """
    logger.info(
        "Ejecutando herramienta: calendarizar_cita (fecha=%r, nombre_cliente=%r)",
        fecha, nombre_cliente,
    )

    try:
        resultado = citas_service.calendarizar_cita(fecha, nombre_cliente)
        logger.info("Finalizó herramienta: calendarizar_cita")
        return resultado

    except Exception:
        logger.exception("Error en calendarizar_cita")
        raise


if __name__ == "__main__":
    logger.info("Iniciando servidor MCP")

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
        stateless_http=True,
        json_response=True,
    )
