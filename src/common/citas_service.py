from psycopg.types.json import Jsonb

from . import weather_service
from .db import get_connection

ESTADO_POR_VEREDICTO = {
    "ideal": "confirmada",
    "marginal": "marginal",
    "no_seguro": "rechazada",
}


def calendarizar_cita(fecha: str, nombre_cliente: str = "Cliente") -> dict:
    """Calendariza una cita de salto, verificando primero el clima para la fecha solicitada."""
    evaluacion = weather_service.consultar_clima(fecha)

    if "error" in evaluacion:
        return {"reservada": False, **evaluacion}

    estado = ESTADO_POR_VEREDICTO[evaluacion["veredicto"]]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO citas (fecha, cliente, estado, evaluacion)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (fecha, nombre_cliente, estado, Jsonb(evaluacion)),
            )
            cita_id = cur.fetchone()[0]
        conn.commit()

    return {
        "reservada": estado != "rechazada",
        "cita_id": cita_id,
        "estado": estado,
        "evaluacion": evaluacion,
    }
