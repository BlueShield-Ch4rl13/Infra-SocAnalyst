# ============================================================
#  Nodo "IOC PYTHON" — Shuffle (acción Execute Python)
#  Parsea el webhook de Wazuh, extrae IOCs, calcula la
#  severidad y prepara la petición a Ollama CON los datos de
#  la alerta.
# ------------------------------------------------------------
#  REGLAS DE ORO (aprendidas a base de iteraciones):
#   - Terminar con UN SOLO print(json.dumps({...})): si se
#     imprime algo más antes, $ioc_python.severity no resuelve.
#   - El nombre del nodo debe ser exactamente "IOC PYTHON"
#     para que aguas abajo resuelva como $ioc_python.*
#   - Leer el cuerpo como string RAW entre triples comillas
#     (r"..."): sin la r, una ruta de Windows del JSON
#     ("C:\\Windows") rompe json.loads.
#
#  Por qué el prompt se construye aquí: Shuffle sustituye
#  $exec.* como texto dentro del JSON del nodo HTTP, y unas
#  comillas en full_log lo rompen. Aquí se serializa con
#  json.dumps y el nodo de Ollama recibe el cuerpo ya válido
#  en $ioc_python.ollama_body. Antes el prompt era un texto
#  fijo sin ningún dato de la alerta.
# ============================================================
import json
import uuid

raw = r"""$exec"""            # el cuerpo del webhook llega como texto

try:
    alert = json.loads(raw)
except Exception:
    alert = {}

rule = alert.get("rule", {}) or {}
data = alert.get("data", {}) or {}
agente = (alert.get("agent", {}) or {}).get("name", "desconocido")

try:
    level = int(rule.get("level", 0) or 0)
except (TypeError, ValueError):
    level = 0
srcip = data.get("srcip", "") or data.get("src_ip", "")

# IOCs detectados en la alerta
iocs = [srcip] if srcip else []

# Mapear nivel Wazuh (0-15) -> severidad TheHive (1-4)
if level >= 12:
    severity, etiqueta = 4, "Critica"
elif level >= 10:
    severity, etiqueta = 3, "Alta"
elif level >= 7:
    severity, etiqueta = 2, "Media"
else:
    severity, etiqueta = 1, "Baja"

tecnicas = ", ".join((rule.get("mitre", {}) or {}).get("id", []) or []) or "sin tecnica"
log_original = (alert.get("full_log", "") or "")[:800]

prompt = (
    "Eres un analista SOC. Analiza esta alerta y responde en espanol en un parrafo "
    "de maximo 4 frases, sin markdown ni comillas: que ha pasado, por que importa "
    "y el primer paso de respuesta.\n"
    f"Regla: {rule.get('description', '')} (id {rule.get('id', '')}, nivel {level}/15)\n"
    f"Tecnicas ATT&CK: {tecnicas}\n"
    f"Equipo: {agente}\n"
    f"IP de origen: {srcip or 'no consta'}\n"
    f"Log: {log_original}"
)

salida = {
    "severity": severity,
    "severity_label": etiqueta,
    "srcip": srcip,
    "ioc_list": ", ".join(iocs) if iocs else "N/A",
    "rule_level": level,
    "rule_desc": rule.get("description", ""),
    "agent": agente,
    "wazuh_id": alert.get("id", ""),
    # sourceRef unico: si se repite, TheHive deduplica la alerta en silencio
    "source_ref": "wazuh-" + (alert.get("id") or str(uuid.uuid4())),
    # cuerpo completo para el nodo HTTP de Ollama, ya serializado
    "ollama_body": json.dumps({
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 400, "temperature": 0.3},
    }),
}

print(json.dumps(salida))
