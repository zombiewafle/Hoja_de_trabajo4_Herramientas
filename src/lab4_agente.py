import os
import re
import json
import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer
from groq import Groq

load_dotenv()

MODEL_LLM = "openai/gpt-oss-20b"

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

UMBRAL_SIMILITUD = 0.50
cliente = Groq()

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_faq",
            "description": (
                "Busca información relevante en la base de conocimientos "
                "de preguntas frecuentes de Parachute S.A."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pregunta": {
                        "type": "string",
                        "description": (
                            "La pregunta del usuario que debe buscarse "
                            "en la base de conocimientos."
                        )
                    }
                },
                "required": ["pregunta"]
            }
        }
    }
]

def buscar_faq(pregunta):
    embedding_pregunta = model.encode(pregunta)

    with psycopg.connect(**DB_CONFIG) as conn:
        register_vector(conn)

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
                (embedding_pregunta, embedding_pregunta)
            )

            resultados = cur.fetchall()

    if not resultados:
        return {
            "encontrado": False,
            "resultados": []
        }

    mejorSolicitud = float(resultados[0][3])

    if mejorSolicitud < UMBRAL_SIMILITUD:
        return {
            "encontrado": False,
            "similitud_maxima": mejorSolicitud,
            "resultados": []
        }

    if respuesta_es_generica(resultados[0][2]):
        return {
            "encontrado": False,
            "resultados": []
        }

    faqs = []

    for id_faq, pregunta, respuesta, similitud in resultados:
        faqs.append({
            "id": id_faq,
            "pregunta": pregunta,
            "respuesta": respuesta,
            "similitud": float(similitud)
        })

    return {
        "encontrado": True,
        "resultados": faqs
    }

def respuesta_es_generica(respuesta):
    frases_genericas = [
        "Respuesta detallada para la consulta",
        "Para más detalles específicos",
        "consulte directamente con la central de atención"
    ]

    return any(
        frase.lower() in respuesta.lower()
        for frase in frases_genericas
    )

def agente(pregunta):
    messages = [
        {
            "role": "system",
            "content": """
    Eres un agente de atención al cliente de Parachute S.A.

    Para responder la pregunta actual debes consultar la herramienta buscar_faq.

    No respondas utilizando conocimiento propio.
    No inventes información.

    Después de recibir el resultado de buscar_faq:
    - utiliza únicamente esa información;
    - si "encontrado" es false, indica que no puedes responder con la información disponible;
    - responde en español de forma clara y breve.
    """
        },
        {
            "role": "user",
            "content": pregunta
        }
    ]

    messages.append({
        "role": "user",
        "content": pregunta
    })

    respuesta = cliente.chat.completions.create(
        model=MODEL_LLM,
        messages=messages,
        tools=TOOLS,
        tool_choice={
            "type": "function",
            "function": {
                "name": "buscar_faq"
            }
        },
        temperature=0
    )

    mensaje_modelo = respuesta.choices[0].message

    messages.append(mensaje_modelo)

    tool_calls = mensaje_modelo.tool_calls

    if not tool_calls:
        return "No fue posible consultar la base de conocimientos."

    for tool_call in tool_calls:
        print(f"[TOOL] buscar_faq: {pregunta}")
        nombre_funcion = tool_call.function.name

        argumentos = json.loads(
            tool_call.function.arguments
        )


        if nombre_funcion == "buscar_faq":
            resultadoTool = buscar_faq(
                argumentos["pregunta"]
                
            )
        else:
            resultadoTool = {
                "error": "Herramienta desconocida"
            }

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": nombre_funcion,
            "content": json.dumps(
                resultadoTool,
                ensure_ascii=False
            )
        })

    respuestaFinalAgente = cliente.chat.completions.create(
        model=MODEL_LLM,
        messages=messages,
        temperature=0
    )

    contenido = respuestaFinalAgente.choices[0].message.content

    messages.append({
        "role": "assistant",
        "content": contenido
    })

    return contenido


def main():
    while True:

        pregunta = input("> ")

        if pregunta.lower() == "bye":
            break

        if not pregunta.strip():
            print("Por favor, escribe una pregunta.")
            continue

        try:
            respuesta = agente(pregunta)
            print(respuesta)

        except Exception as error:
            print("Error:", error)


if __name__ == "__main__":
    main()