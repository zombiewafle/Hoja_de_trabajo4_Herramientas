import os
import re
import json
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()

CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "Corpus_FAQs_Parachute_SA_2026.txt"

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


DB_CONFIG = {
    "dbname": "laboratorio4_agents",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}


def parsing():
    with open(CORPUS_PATH, "r", encoding="utf-8") as file:
        contenido  = file.read();
        
        bloques = contenido.split("------------------------------------------------------------")
        conn = psycopg.connect(**DB_CONFIG)
        register_vector(conn)

        cur = conn.cursor() 


        for bloque in bloques: 

            id_text = None
            categoria = None
            pregunta = None
            respuesta = None
            metadata = None

            # faq = {}

            lineas = bloque.strip().splitlines()

            for linea in lineas:
                if linea.startswith("ID: "):
                    id_text = linea.split(":", 1)[1].strip()

                elif linea.startswith("CATEGORÍA"):
                    categoria = linea.split(":", 1)[1].strip()
                
                elif linea.startswith("PREGUNTA"):
                    pregunta = linea.split(":", 1)[1].strip()

                elif linea.startswith("RESPUESTA"):
                    respuesta = linea.split(":", 1)[1].strip()

                elif linea.startswith("METADATA"):
                    metadata = json.loads(
                        linea.split(":", 1)[1].strip()
                    )

            if id_text is None: 
                continue
            else: 
                # texto_embedding = pregunta + " " + respuesta
                texto_embedding = pregunta
                # print(f"Procesando: {id_text}")
                # print(f"Procesando: {categoria}")
                # print(f"Procesando: {pregunta}")
                # print(f"Procesando: {respuesta}")
                # print(f"Procesando: {Jsonb(metadata)}")
                embeddings = model.encode(texto_embedding)
                
                print(embeddings.shape)

                # similaridad = model.similarity(embeddings, embeddings)
                # print(similaridad)

                cur.execute("""
                INSERT INTO faqs (id, categoria, pregunta, respuesta, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (id_text, categoria, pregunta, respuesta, Jsonb(metadata), embeddings))
                # print (id_text, categoria, pregunta, respuesta, Jsonb(metadata), embeddings)

    conn.commit()
    print("carga completada!")

    cur.close()
    conn.close()


parsing()