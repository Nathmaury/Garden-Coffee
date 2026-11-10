from src.agent import llm, prompts, tools

MAX_PASOS = 8


class Agente:
    def __init__(self):
        self.mensajes = [{"role": "system", "content": prompts.SYSTEM_PROMPT}]

    def reiniciar(self):
        self.mensajes = self.mensajes[:1]

    def preguntar(self, pregunta):
        self.mensajes.append({"role": "user", "content": pregunta})
        registro = {"respuesta": "", "graficos": [], "consultas": [], "contexto": [], "pasos": 0, "tokens": 0}
        for _ in range(MAX_PASOS):
            mensaje, uso = llm.completar(self.mensajes, tools.ESQUEMAS)
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