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
import json
import os
import sys
import time
from urllib.parse import urlsplit

try:
    import requests
except ImportError:
    # El Python embebido de Wazuh incluye requests.
    requests = None

# Verificacion TLS del webhook de Shuffle:
#   SHUFFLE_CA=/ruta/ca-shuffle.pem   -> verifica contra esa CA (recomendado)
#   SHUFFLE_INSECURE_TLS=1             -> sin verificar, SOLO laboratorio
#   (nada)                             -> verificacion normal del sistema
# Antes iba siempre con verify=False: cualquiera en el camino podia leer las
# alertas o hacerse pasar por Shuffle.
if os.environ.get("SHUFFLE_INSECURE_TLS") == "1":
    VERIFICAR = False
    if requests is not None:
        requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
else:
    VERIFICAR = os.environ.get("SHUFFLE_CA") or True


def sin_secreto(texto, hook_url):
    """El webhook lleva su identificador en la ruta, y quien lo tiene puede
    lanzar el workflow: al log solo va el servidor, nunca la URL completa."""
    servidor = urlsplit(hook_url).netloc or "?"
    return str(texto).replace(hook_url, "https://%s/api/v1/hooks/<oculto>" % servidor)


def log(msg):
    """Deja rastro en stderr y en el integrations.log que el README manda mirar."""
    linea = "%s custom-shuffle: %s\n" % (time.strftime("%Y/%m/%d %H:%M:%S"), msg)
    sys.stderr.write(linea)
    try:
        with open("/var/ossec/logs/integrations.log", "a") as f:
            f.write(linea)
    except OSError:
        pass

# Grupos de los sensores cuyas alertas queremos enviar al SOAR.
SENSOR_GROUPS = {"falco", "tetragon", "suricata", "ids"}


def main():
    if len(sys.argv) < 4:
        log("faltan argumentos (uso: <alerta.json> <api_key> <hook_url>)")
        sys.exit(1)

    alert_file = sys.argv[1]
    hook_url = sys.argv[3]

    try:
        with open(alert_file, "r") as f:
            alert = json.load(f)
    except Exception as e:
        log("no se pudo leer la alerta %s: %s" % (alert_file, e))
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
        log("requests no disponible en este Python")
        sys.exit(1)

    try:
        resp = requests.post(hook_url, json=payload, verify=VERIFICAR, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        # Antes se tragaba el error y el script salia 0 "con exito": un webhook
        # mal configurado o un 4xx/5xx pasaba inadvertido.
        log("fallo al reenviar a Shuffle (%s): %s" % (urlsplit(hook_url).netloc, sin_secreto(e, hook_url)))
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
