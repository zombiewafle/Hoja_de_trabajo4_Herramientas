# Laboratorio 4 — Agente de atención al cliente (Parachute S.A.)

Agente conversacional con herramienta de búsqueda de FAQs sobre una base de conocimientos vectorial (pgvector), usando Groq como proveedor de LLM.

## Estructura del proyecto

| Ruta | Contenido |
| --- | --- |
| `src/` | Código fuente (agente y script de carga) |
| `data/` | Corpus de FAQs |
| `db/` | Esquema inicial de la base de datos (`init.sql`) |
| `demo/` | Video de demostración |
| `compose.yaml` | Definición de PostgreSQL + pgvector |

## Requisitos

- [uv](https://docs.astral.sh/uv/)
- Docker o Podman
- API Key de Groq

## Configuración

Crear un archivo `.env` en la raíz del proyecto utilizando, como referencia:

```env
GROQ_API_KEY=
DB_NAME=laboratorio4_agents
DB_USER=postgres
DB_PASSWORD=postgres
```

Levantar PostgreSQL + pgvector con Docker:

```sh
docker compose up -d
```

Instalar las dependencias del proyecto (`uv` crea el entorno virtual automáticamente):

```sh
uv sync
```

## Cargar la base de conocimientos

Con PostgreSQL activo:

```sh
uv run src/lab4_carga.py
```

## Ejecutar el agente

```sh
uv run src/lab4_agente.py
```

Para salir, escribir `Bye`.
