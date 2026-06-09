#!/usr/bin/env python3
# ============================================================
#  custom-shuffle.py — Integración Wazuh -> Shuffle (SOAR)
#  Reenvía al webhook de Shuffle solo las alertas de los
#  sensores del SOC (Falco, Tetragon, Suricata, IDS).
# ------------------------------------------------------------
#  Ubicación:  /var/ossec/integrations/custom-shuffle.py
#  Permisos:   chmod 750 ; chown root:wazuh
#  Tras editar: systemctl restart wazuh-manager
#
#  El integrator invoca el script con:
#    argv[1] = ruta al fichero JSON de la alerta
#    argv[2] = api_key (no usado aquí)
#    argv[3] = hook_url (webhook de Shuffle)
# ============================================================
import sys
import json

try:
    import requests
except ImportError:
    # El Python embebido de Wazuh incluye requests.
    requests = None

# Grupos de los sensores cuyas alertas queremos enviar al SOAR.
SENSOR_GROUPS = {"falco", "tetragon", "suricata", "ids"}


def main():
    if len(sys.argv) < 4:
        sys.exit(1)

    alert_file = sys.argv[1]
    hook_url = sys.argv[3]

    try:
        with open(alert_file, "r") as f:
            alert = json.load(f)
    except Exception:
        sys.exit(1)

    rule = alert.get("rule", {})
    groups = set(rule.get("groups", []) or [])

    # Filtro: solo seguimos si la alerta pertenece a un sensor del SOC.
    if not SENSOR_GROUPS.intersection(groups):
        sys.exit(0)

    # Reenviamos la alerta completa preservando la estructura
    # para que en Shuffle resuelvan rutas como:
    #   $exec.rule.level   $exec.rule.description   $exec.data.srcip
    payload = dict(alert)
    payload["source"] = "Wazuh"           # TheHive exige source no vacío
    payload["wazuh_id"] = alert.get("id", "")

    if requests is None:
        sys.exit(1)

    try:
        # verify=False -> equivalente a curl -k (cert autofirmado de Shuffle)
        requests.post(hook_url, json=payload, verify=False, timeout=10)
    except Exception:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
