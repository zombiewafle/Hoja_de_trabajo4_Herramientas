# Objetivos
Familiarizarse con los protocolos para herramientas, prompts y recursos (MCP) y para comunicación entre agentes (A2A).

# Instrucciones
Utilizando el código que han venido trabajando del agente para la empresa Parachute S,A. Abstraiga las herramientas de sus agentes en un solo servidor MCP, y exponga su multi agent system  como un solo agente con sus skills utilizando A2A .

Para realizar su propio servidor MCP:

- Pueden consultar https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server
- Si utilizan el SDK de Open AI Agents, este ya provee la opción para integrarse como cliente fácilmente, en este link pueden ver la guía del SDK de python:
  - https://openai.github.io/openai-agents-python/mcp/
Deben de utilizar como transporte Stremeable HTTP.

Para hacer su agente compatible con A2A:

- Tienen que crear un servidor A2A que envuelva su Multi Agent System
  - Pueden explorar como hacerlo en la página oficial del protocolo

- Deberán modificar su interfaz de terminal para que se comporte como un A2A Client. Los SDK de A2A ya proveen código para crear clientes A2A, pueden ver una guía básica de su uso con el SDK de python aquí:
  - https://a2a-protocol.org/latest/tutorials/python/6-interact-with-server/#understanding-the-client-code
 

Debe de entregar el código de su implementación en un repositorio y un video en donde se vea lo siguiente:

- El servidor MCP siendo ejecutado y emitiendo logs por cada ejecución de  herramientas
- El servidor A2A siendo ejecutado y emitiendo logs
- Su aplicación de terminal interactúando ya con con su servidor A2A
