// Aserciones de tool execution. provider.py devuelve en metadata.herramientas
// cada función de servicio que se ejecutó: { nombre, args, kwargs, resultado }.
// Parámetros (vía `config` de la aserción): nombre y, opcionalmente, fecha.

const llamadas = (context) => context.providerResponse?.metadata?.herramientas || [];

const coincide = (h, { nombre, fecha }) =>
  h.nombre === nombre && (!fecha || [...h.args, ...Object.values(h.kwargs)].includes(fecha));

const resumen = (context) =>
  llamadas(context).map((h) => `${h.nombre}(${JSON.stringify(h.args)})`).join(', ') || 'ninguna';

const resultado = (pass, reason) => ({ pass, score: pass ? 1 : 0, reason });

// La herramienta se ejecutó (con la fecha indicada, si se pasa).
module.exports.llamo = (output, context) =>
  resultado(
    llamadas(context).some((h) => coincide(h, context.config)),
    `Se esperaba ${context.config.nombre} ${context.config.fecha || ''}. Llamadas: ${resumen(context)}`,
  );

// La herramienta NO se ejecutó.
module.exports.noLlamo = (output, context) =>
  resultado(
    !llamadas(context).some((h) => h.nombre === context.config.nombre),
    `No se esperaba ${context.config.nombre}. Llamadas: ${resumen(context)}`,
  );
