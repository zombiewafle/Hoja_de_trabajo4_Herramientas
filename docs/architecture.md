# Arquitecturas de orquestación multiagente

Las tres arquitecturas resuelven el mismo problema (FAQs, consulta de clima
y agendamiento de citas de salto) reutilizando la misma lógica de
integración (`src/common/`); únicamente cambia cómo se organizan y se
comunican los agentes.

## 1. Centralizada (`src/agente_centralizado.py`)

Un único agente controla directamente las tres herramientas. No existe
ningún tipo de delegación entre agentes.

```mermaid
graph TD
    Usuario([Usuario]) --> A[AgenteParachute]
    A --> T1[[buscar_faq_tool]]
    A --> T2[[consultar_clima_tool]]
    A --> T3[[calendarizar_cita_tool]]
```

## 2. Jerárquica (`src/agente_jerarquico.py`)

Un supervisor global delega en especialistas mediante `Agent.as_tool()`.
Uno de esos especialistas (Operaciones) es a su vez un supervisor de otros
dos agentes. Hay varios niveles de autoridad: el supervisor global nunca
llama las herramientas directamente, siempre delega.

```mermaid
graph TD
    Usuario([Usuario]) --> SG[SupervisorGlobal]
    SG -->|as_tool| AC[AgenteAtencionCliente]
    SG -->|as_tool| SO[SupervisorOperaciones]
    AC --> T1[[buscar_faq_tool]]
    SO -->|as_tool| CL[AgenteClima]
    SO -->|as_tool| CI[AgenteCitas]
    CL --> T2[[consultar_clima_tool]]
    CI --> T3[[calendarizar_cita_tool]]
```

## 3. Decentralizada (`src/agente_decentralizado.py`)

Agentes pares se transfieren la conversación entre sí mediante `handoff()`.
Ningún agente retiene el control central de toda la conversación: quien la
tiene en un momento dado decide a quién transferirla a continuación.

```mermaid
graph TD
    Usuario([Usuario]) --> R[Recepcion]
    R <-->|handoff| F[AgenteFAQ]
    R <-->|handoff| C[AgenteClima]
    R <-->|handoff| Ci[AgenteCitas]
    F <-->|handoff| C
    F <-->|handoff| Ci
    C <-->|handoff| Ci
    F --> T1[[buscar_faq_tool]]
    C --> T2[[consultar_clima_tool]]
    Ci --> T3[[calendarizar_cita_tool]]
```
