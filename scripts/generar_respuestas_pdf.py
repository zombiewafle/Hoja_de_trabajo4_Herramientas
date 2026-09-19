"""Genera docs/respuestas.pdf con las respuestas a las preguntas del
enunciado (instructions.md). Se ejecuta una sola vez; el PDF resultante se
versiona en el repositorio.
"""

from pathlib import Path

from fpdf import FPDF

SALIDA = Path(__file__).resolve().parent.parent / "docs" / "respuestas.pdf"

PREGUNTA_1 = "¿Qué arquitectura/arquitecturas resuelven mejor este problema? ¿Por qué?"

RESPUESTA_1 = """La arquitectura jerárquica es la que mejor resuelve este problema, y lo \
seguirá haciendo a medida que Parachute S.A. cumpla su advertencia de \
incrementar los requerimientos funcionales.

Con solo dos dominios (FAQs, y clima/citas) la diferencia con la \
arquitectura centralizada todavía no es grande. Pero la jerárquica ya \
separa cada responsabilidad en su propio agente especialista, y agrupa los \
especialistas relacionados bajo un supervisor intermedio (Operaciones). \
Esto tiene dos ventajas concretas para este caso:

1. Extensibilidad ordenada: un nuevo requerimiento (por ejemplo, cancelar \
citas, o consultar el estado del equipo) se agrega como un nuevo \
especialista bajo el supervisor que corresponda, sin tocar el prompt ni la \
lógica de los demás agentes. En la arquitectura centralizada, cada nueva \
herramienta se suma al mismo agente, y su instructivo y lista de \
herramientas crecen sin límite, lo que degrada la precisión del modelo \
para elegir la herramienta correcta.

2. Control y trazabilidad: el supervisor global siempre sabe qué \
especialista atendió cada consulta, porque él mantiene el control de la \
conversación (Agent.as_tool no cede el control, solo pide un resultado \
puntual). Esto es valioso en un dominio con implicaciones de seguridad \
(saltar en condiciones climáticas no seguras), donde interesa poder \
explicar y auditar exactamente qué lógica decidió qué.

La arquitectura decentralizada (handoffs) es la más difícil de mantener \
predecible a medida que crecen los requerimientos: cada nuevo agente debe \
saber a cuáles otros puede transferir la conversación, y el número de \
transferencias posibles crece rápidamente (grafo completo), lo que hace \
más difícil garantizar que el usuario termine con la respuesta correcta. \
Es la mejor opción solo si se espera que las conversaciones cambien de \
tema con frecuencia y de forma impredecible, algo que no es el caso aquí: \
el flujo de este problema (pregunta frecuente, o clima seguido de \
agendar) es bastante predecible."""

PREGUNTA_2 = "¿Considera que es necesario utilizar un sistema multiagente en este caso? ¿Por qué?"

RESPUESTA_2 = """No es estrictamente necesario para el alcance actual del problema. Con \
tres herramientas (buscar FAQ, consultar clima, calendarizar cita) un solo \
agente bien instruido -la arquitectura centralizada- es perfectamente \
capaz de elegir la herramienta correcta y responder con la información que \
esta devuelve. Un sistema multiagente añade llamadas adicionales al modelo \
(cada delegación es una llamada extra), lo cual incrementa latencia y \
costo sin aportar una capacidad que un solo agente no tenga ya.

Sin embargo, el enunciado deja claro que Parachute S.A. va a seguir \
incrementando los requerimientos funcionales. Esa afirmación es la que \
justifica invertir en una arquitectura multiagente desde ahora: no porque \
el problema actual lo exija, sino porque el costo de dividir \
responsabilidades en agentes especialistas es bajo hoy, y evita una \
reescritura más costosa el día en que el agente centralizado se vuelva \
difícil de mantener por la cantidad de herramientas e instrucciones que \
acumule. En ese sentido, el sistema multiagente no es una necesidad \
funcional del problema, sino una decisión de diseño orientada al \
crecimiento esperado del sistema."""


def _agregar_seccion(pdf: FPDF, titulo: str, pregunta: str, respuesta: str) -> None:
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 8, titulo)
    pdf.ln(2)

    pdf.set_font("Helvetica", "BI", 12)
    pdf.multi_cell(0, 7, pregunta)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, respuesta)
    pdf.ln(8)


def main() -> None:
    pdf = FPDF(format="Letter")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, "Hoja de trabajo 4 - Respuestas")
    pdf.ln(4)

    _agregar_seccion(pdf, "Pregunta 1", PREGUNTA_1, RESPUESTA_1)
    _agregar_seccion(pdf, "Pregunta 2", PREGUNTA_2, RESPUESTA_2)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(SALIDA))
    print(f"PDF generado en {SALIDA}")


if __name__ == "__main__":
    main()
