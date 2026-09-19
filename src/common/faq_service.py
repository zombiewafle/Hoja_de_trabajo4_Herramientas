from sentence_transformers import SentenceTransformer

from . import config
from .db import get_connection

_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

FRASES_GENERICAS = [
    "Respuesta detallada para la consulta",
    "Para más detalles específicos",
    "consulte directamente con la central de atención",
]


def _respuesta_es_generica(respuesta: str) -> bool:
    return any(
        frase.lower() in respuesta.lower()
        for frase in FRASES_GENERICAS
    )


def buscar_faq(pregunta: str) -> dict:
    embedding_pregunta = _model.encode(pregunta)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    pregunta,
                    respuesta,
                    1 - (embedding <=> %s) AS similitud
                FROM faqs
                ORDER BY embedding <=> %s
                LIMIT 3;
                """,
                (embedding_pregunta, embedding_pregunta),
            )

            resultados = cur.fetchall()

    if not resultados:
        return {"encontrado": False, "resultados": []}

    mejor_similitud = float(resultados[0][3])

    if mejor_similitud < config.UMBRAL_SIMILITUD:
        return {
            "encontrado": False,
            "similitud_maxima": mejor_similitud,
            "resultados": [],
        }

    if _respuesta_es_generica(resultados[0][2]):
        return {"encontrado": False, "resultados": []}

    faqs = [
        {
            "id": id_faq,
            "pregunta": pregunta_faq,
            "respuesta": respuesta,
            "similitud": float(similitud),
        }
        for id_faq, pregunta_faq, respuesta, similitud in resultados
    ]

    return {"encontrado": True, "resultados": faqs}
