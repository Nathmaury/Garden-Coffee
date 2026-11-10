import sys
import time

from src import config
from src.agent.loop import Agente


def responder(agente, pregunta):
    resultado = agente.preguntar(pregunta)
    for sql in resultado["consultas"]:
        print(f"\n[SQL]\n{sql}")
    for i, fig in enumerate(resultado["graficos"], 1):
        ruta = config.DATA_PROCESSED / f"grafico_{int(time.time())}_{i}.html"
        fig.write_html(ruta)
        print(f"\n[Gráfico] {ruta}")
    print(f"\nAgente: {resultado['respuesta']}")
    print(f"\n({resultado['pasos']} pasos, {resultado['tokens']} tokens)")


def main():
    agente = Agente()
    if len(sys.argv) > 1:
        responder(agente, " ".join(sys.argv[1:]))
        return
    print("Agente Garden Coffee. Escribe 'salir' para terminar.")
    while True:
        pregunta = input("\nTú: ").strip()
        if pregunta.lower() in {"salir", "exit"}:
            break
        if pregunta:
            responder(agente, pregunta)


if __name__ == "__main__":
    main()