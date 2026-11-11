from openai import BadRequestError

from src.agent import llm, prompts, tools

MAX_PASOS = 8
MENSAJE_FUERA_DE_ALCANCE = (
    "Solo puedo ayudarte con el análisis de café de Garden Coffee. "
    "Por ejemplo, puedes preguntarme qué mercados conviene priorizar."
)


def _bloqueado_por_filtro(error):
    return getattr(error, "code", None) == "content_filter" or "content management policy" in str(error)


class Agente:
    def __init__(self):
        self.mensajes = [{"role": "system", "content": prompts.SYSTEM_PROMPT}]

    def reiniciar(self):
        self.mensajes = self.mensajes[:1]

    def preguntar(self, pregunta):
        self.mensajes.append({"role": "user", "content": pregunta})
        registro = {"respuesta": "", "graficos": [], "consultas": [], "contexto": [], "pasos": 0, "tokens": 0, "bloqueado": False}
        for _ in range(MAX_PASOS):
            try:
                mensaje, uso = llm.completar(self.mensajes, tools.ESQUEMAS)
            except BadRequestError as error:
                if not _bloqueado_por_filtro(error):
                    raise
                self.mensajes.append({"role": "assistant", "content": MENSAJE_FUERA_DE_ALCANCE})
                registro["respuesta"] = MENSAJE_FUERA_DE_ALCANCE
                registro["bloqueado"] = True
                return registro
            registro["pasos"] += 1
            registro["tokens"] += getattr(uso, "total_tokens", 0) or 0
            asistente = {"role": "assistant", "content": mensaje.content or ""}
            if mensaje.tool_calls:
                asistente["tool_calls"] = [
                    {"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}}
                    for t in mensaje.tool_calls
                ]
            self.mensajes.append(asistente)
            if not mensaje.tool_calls:
                registro["respuesta"] = mensaje.content or ""
                return registro
            for llamada in mensaje.tool_calls:
                salida = tools.ejecutar(llamada.function.name, llamada.function.arguments, registro)
                self.mensajes.append({"role": "tool", "tool_call_id": llamada.id, "content": salida})
        registro["respuesta"] = "No pude completar la respuesta en el número máximo de pasos. Intenta con una pregunta más específica."
        return registro