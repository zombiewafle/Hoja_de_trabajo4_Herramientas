import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime

from . import config

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _fetch(params: dict, intentos: int = 3) -> dict:
    # Open-Meteo a veces se queda colgado en el handshake TLS de forma
    # intermitente; reintentar con un timeout corto lo resuelve.
    url = f"{OPEN_METEO_URL}?{urllib.parse.urlencode(params)}"
    for intento in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError):
            if intento == intentos - 1:
                raise


def _peor_veredicto(*veredictos: str) -> str:
    orden = {"ideal": 0, "marginal": 1, "no_seguro": 2}
    return max(veredictos, key=lambda v: orden[v])


def _evaluar(velocidad_viento: float, rafaga: float, precipitacion: float, nubosidad: float) -> dict:
    razones = []

    if velocidad_viento > 28:
        v_viento = "no_seguro"
        razones.append(
            f"Velocidad de viento en superficie {velocidad_viento} km/h supera 28 km/h (no seguro / prohibido)."
        )
    elif velocidad_viento >= 20:
        v_viento = "marginal"
        razones.append(
            f"Velocidad de viento en superficie {velocidad_viento} km/h en rango marginal "
            "(20-28 km/h, solo tándem experimentado)."
        )
    else:
        v_viento = "ideal"

    if rafaga > 35:
        v_rafaga = "no_seguro"
        razones.append(f"Ráfaga de viento {rafaga} km/h supera 35 km/h (no seguro / prohibido).")
    else:
        v_rafaga = "ideal"

    if precipitacion > 0.0:
        v_precipitacion = "no_seguro"
        razones.append(f"Precipitación de {precipitacion} mm (no seguro / prohibido, cualquier lluvia).")
    else:
        v_precipitacion = "ideal"

    if nubosidad > 75:
        v_nubosidad = "no_seguro"
        razones.append(f"Cobertura de nubes {nubosidad}% supera 75% (no seguro / prohibido).")
    elif nubosidad >= 30:
        v_nubosidad = "marginal"
        razones.append(f"Cobertura de nubes {nubosidad}% en rango marginal (30-75%, nubes dispersas).")
    else:
        v_nubosidad = "ideal"

    veredicto = _peor_veredicto(v_viento, v_rafaga, v_precipitacion, v_nubosidad)

    if veredicto == "ideal":
        razones.append("Todas las condiciones están dentro de los rangos ideales para saltar.")

    return {"veredicto": veredicto, "razones": razones}


def consultar_clima(fecha: str) -> dict:
    """Consulta el pronóstico para la fecha dada y evalúa si es apta para saltar."""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return {"error": f"Formato de fecha inválido: '{fecha}'. Usa el formato YYYY-MM-DD."}

    hoy = date.today()
    dias_diferencia = (fecha_dt - hoy).days

    if dias_diferencia < 0:
        return {"error": f"La fecha {fecha} ya pasó, no se puede calendarizar una cita en el pasado."}

    if dias_diferencia > config.MAX_DIAS_PRONOSTICO:
        return {
            "error": (
                f"No es posible calendarizar para {fecha}: Open-Meteo únicamente provee "
                f"pronóstico hasta {config.MAX_DIAS_PRONOSTICO} días. Por favor elige una fecha "
                f"dentro de ese rango."
            )
        }

    if dias_diferencia == 0:
        datos = _fetch(
            {
                "latitude": config.COORD_LAT,
                "longitude": config.COORD_LON,
                "current": "temperature_2m,precipitation,cloud_cover,wind_speed_10m,wind_gusts_10m",
                "timezone": "auto",
            }
        )
        actual = datos["current"]
        fuente = "current"
        temperatura = actual["temperature_2m"]
        precipitacion = actual["precipitation"]
        nubosidad = actual["cloud_cover"]
        velocidad_viento = actual["wind_speed_10m"]
        rafaga = actual["wind_gusts_10m"]
    else:
        datos = _fetch(
            {
                "latitude": config.COORD_LAT,
                "longitude": config.COORD_LON,
                "daily": (
                    "temperature_2m_max,precipitation_sum,cloud_cover_max,"
                    "wind_speed_10m_max,wind_gusts_10m_max"
                ),
                "timezone": "auto",
                "start_date": fecha,
                "end_date": fecha,
            }
        )
        diario = datos["daily"]
        fuente = "daily"
        temperatura = diario["temperature_2m_max"][0]
        precipitacion = diario["precipitation_sum"][0]
        nubosidad = diario["cloud_cover_max"][0]
        velocidad_viento = diario["wind_speed_10m_max"][0]
        rafaga = diario["wind_gusts_10m_max"][0]

    evaluacion = _evaluar(velocidad_viento, rafaga, precipitacion, nubosidad)

    return {
        "fecha": fecha,
        "fuente": fuente,
        "temperatura_2m": temperatura,
        "precipitacion": precipitacion,
        "cobertura_nubes": nubosidad,
        "velocidad_viento_10m": velocidad_viento,
        "rafaga_viento_10m": rafaga,
        **evaluacion,
    }
