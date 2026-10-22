# Workflow SOAR (Shuffle)

Documentación del workflow de respuesta automatizada. El **export `workflow-soc.json` debes generarlo desde tu propia instancia** (Shuffle → tu workflow → menú `⋯` → *Export*), porque contiene UUIDs e IDs internos específicos de tu despliegue. Aquí se documenta la estructura y se incluye el código de los nodos Python (`nodos/`) que sí es reproducible.

## Cadena de nodos

```
Webhook (Wazuh)
  → IOC PYTHON        (nodos/ioc_python.py — extrae IOCs + severidad)
  → MISP              (enriquecimiento de inteligencia de amenazas)
  → OLLAMA            (HTTP POST — análisis semántico con IA local)
  → CLEAN             (nodos/clean.py — normaliza la salida de la IA)
  → ALERT (TheHive)   (crea la alerta)
  → CASE (TheHive)    (promociona a caso)
  → Discord           (tarjeta con severidad, activo, IOC y enlace)
```

## Configuración por nodo

**Webhook** — recibe el JSON de la integración `custom-shuffle.py`. El cuerpo queda disponible como `$exec`.

**IOC PYTHON** (`nodos/ioc_python.py`) — nodo *Execute Python*. El nombre exacto importa: exporta como `$ioc_python.*`.

**MISP** — buscar/crear el observable (`$ioc_python.srcip`) y devolver reputación.

**OLLAMA** — acción HTTP `POST http://<HOST_SOC>:11434/api/generate` con body:
```
$ioc_python.ollama_body
```
El cuerpo lo construye `IOC PYTHON` con `json.dumps`, y el prompt lleva la regla, el nivel, las técnicas ATT&CK, el equipo, la IP y el log de la alerta. Antes el prompt era un texto fijo sin ningún dato de la alerta, así que "la IA analiza la alerta" no era cierto.
⚠️ No insertes objetos `$exec.*` directamente en el body: unas comillas en el log rompen el JSON.

**CLEAN** (`nodos/clean.py`) — nodo *Execute Python*; deja el análisis en una sola línea segura.

**ALERT (TheHive)** — acción *Create alert* (POST, no *Get alert*). Campos clave:
- `type`, `source` = `"Wazuh"` (no vacío)
- `sourceRef` único por alerta: `"$ioc_python.source_ref"` (el id de la alerta de Wazuh; si se repite, TheHive deduplica en silencio)
- `severity` = entero sin comillas (`$ioc_python.severity`, 1–4)
- `title` / `description` con `$ioc_python.rule_desc` y `$clean.analisis`

**CASE (TheHive)** — promociona la alerta a caso.

**Discord** — tarjeta con severidad, activo (`$ioc_python.agent`), IOC (`$ioc_python.ioc_list`) y enlace al caso.

## Guardado (importante)

Guardar en **dos pasos**: confirmar el editor del campo **y** guardar el workflow con el icono de disquete del lienzo. Si no, los cambios no persisten y los mismos errores reaparecen al re-testear.
