from functools import lru_cache
from openai import OpenAI
from src import config


@lru_cache(maxsize=1)
def cliente():
    if not (config.AZURE_OPENAI_ENDPOINT and config.AZURE_OPENAI_API_KEY and config.LLM_MODEL):
        raise RuntimeError("Faltan variables en .env: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY o LLM_MODEL")
    return OpenAI(
        api_key=config.AZURE_OPENAI_API_KEY,
        base_url=config.azure_base_url(),
        max_retries=5,
        timeout=60,
    )


def completar(mensajes, herramientas):
    respuesta = cliente().chat.completions.create(
        model=config.LLM_MODEL,
        messages=mensajes,
        tools=herramientas,
    )
    return respuesta.choices[0].message, respuesta.usage