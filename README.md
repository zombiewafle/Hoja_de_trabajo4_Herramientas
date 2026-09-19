# Laboratorio 4 — Agentes de atención al cliente (Parachute S.A.)

Agentes conversacionales con búsqueda de FAQs sobre una base de conocimientos vectorial (pgvector), consulta de clima (Open-Meteo) y agendamiento de citas de salto, usando Groq como proveedor de LLM. Incluye tres arquitecturas de orquestación multiagente (centralizada, jerárquica, decentralizada) construidas con el [`openai-agents` SDK](https://openai.github.io/openai-agents-python/) apuntando al endpoint compatible con OpenAI de Groq.

## Estructura del proyecto

| Ruta | Contenido |
| --- | --- |
| `src/` | Código fuente: agentes y `common/` (lógica de integración compartida) |
| `data/` | Corpus de FAQs |
| `db/` | Esquema inicial de la base de datos (`init.sql`) |
| `docs/` | Diagramas de arquitectura y PDF de respuestas |
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

## Ejecutar el agente (FAQs)

```sh
uv run src/lab4_agente.py
```

Para salir, escribir `Bye`.

## Ejecutar los agentes multiagente (FAQs + clima + citas)

Cada programa resuelve el mismo problema (FAQs, consulta de clima y agendamiento de citas) con una arquitectura de orquestación distinta. Ver `docs/architecture.md` para el diagrama de cada una y `docs/respuestas.pdf` para el análisis comparativo.

```sh
uv run src/agente_centralizado.py
uv run src/agente_jerarquico.py
uv run src/agente_decentralizado.py
```

Para salir, escribir `Bye`.
