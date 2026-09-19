import psycopg
from pgvector.psycopg import register_vector

from . import config


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(**config.DB_CONFIG)
    register_vector(conn)
    return conn
