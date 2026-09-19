CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS faqs (
    id VARCHAR(20) PRIMARY KEY,
    categoria TEXT,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(384)
);

CREATE TABLE IF NOT EXISTS citas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    cliente TEXT NOT NULL DEFAULT 'Cliente',
    estado VARCHAR(20) NOT NULL,
    evaluacion JSONB,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);