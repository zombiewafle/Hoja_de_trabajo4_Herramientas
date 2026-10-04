import os

from dotenv import load_dotenv

load_dotenv()

MODEL_LLM = "openai/gpt-oss-20b"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": os.getenv("DB_PORT", "5433"),
}

UMBRAL_SIMILITUD = 0.50

# Coordenadas del lugar de aterrizaje de Parachute S.A.
COORD_LAT = 14.013722
COORD_LON = -90.771611

MAX_DIAS_PRONOSTICO = 16
