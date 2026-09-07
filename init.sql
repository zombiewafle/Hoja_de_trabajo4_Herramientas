CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS faqs (
    id VARCHAR(20) PRIMARY KEY,
    categoria TEXT,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(384)
);