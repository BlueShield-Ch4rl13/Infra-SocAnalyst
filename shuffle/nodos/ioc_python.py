# ============================================================
#  Nodo "IOC PYTHON" — Shuffle (acción Execute Python)
#  Parsea el webhook de Wazuh, extrae IOCs y calcula severidad.
# ------------------------------------------------------------
#  REGLAS DE ORO (aprendidas a base de iteraciones):
#   - Terminar SIEMPRE con print(json.dumps({...})).
#     NO usar return ni exit(json.dumps(...)).
#   - El nombre del nodo debe ser exactamente "IOC PYTHON"
#     para que aguas abajo resuelva como $ioc_python.*
#   - Leer el cuerpo como string entre triples comillas evita
#     conflictos con el builtin exit().
# ============================================================
import json

raw = """$exec"""            # el cuerpo del webhook llega como texto

try:
    alert = json.loads(raw)
except Exception:
    alert = {}

rule = alert.get("rule", {})
data = alert.get("data", {})

level = int(rule.get("level", 0) or 0)
srcip = data.get("srcip", "")

# IOCs detectados en la alerta
iocs = []
if srcip:
    iocs.append(srcip)

# Mapear nivel Wazuh (0-15) -> severidad TheHive (1-4)
if level >= 12:
    severity = 4
elif level >= 10:
    severity = 3
elif level >= 7:
    severity = 2
else:
    severity = 1

salida = {
    "severity": severity,
    "srcip": srcip,
    "ioc_list": ", ".join(iocs) if iocs else "N/A",
    "rule_level": level,
    "rule_desc": rule.get("description", ""),
    "agent": alert.get("agent", {}).get("name", "desconocido"),
    "wazuh_id": alert.get("id", ""),
}

print(json.dumps(salida))
