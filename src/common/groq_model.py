from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

from . import config

# No contamos con una API key de OpenAI; el tracing por defecto del SDK
# intenta subir trazas a la API de OpenAI, así que se desactiva.
set_tracing_disabled(True)

_client = AsyncOpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)

MODEL = OpenAIChatCompletionsModel(model=config.MODEL_LLM, openai_client=_client)
