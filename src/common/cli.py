from agents import Agent, Runner

MAX_INTENTOS = 5

# Con tool_choice forzado (usado para evitar que el modelo invente
# información), el modelo (openai/gpt-oss-20b vía Groq) falla de forma
# intermitente al generar la llamada a herramienta: a veces responde con
# texto plano, y a veces corrompe el nombre de la herramienta con tokens de
# formato internos del modelo. Son fallos transitorios de generación, no de
# la lógica de integración, así que se reintenta antes de mostrar un error.


def run_cli(entry_agent: Agent) -> None:
    while True:
        pregunta = input("> ")

        if pregunta.lower() == "bye":
            break

        if not pregunta.strip():
            print("Por favor, escribe una pregunta.")
            continue

        ultimo_error = None
        for _ in range(MAX_INTENTOS):
            try:
                resultado = Runner.run_sync(entry_agent, pregunta)
                print(resultado.final_output)
                break
            except Exception as error:
                ultimo_error = error
        else:
            print("Error:", ultimo_error)
