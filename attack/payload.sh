#!/usr/bin/env bash
# ============================================================
#  payload.sh — PAYLOAD SIMULADO E INOFENSIVO (solo demo)
# ------------------------------------------------------------
#  No realiza NINGUNA acción dañina. Solo deja una marca con la
#  fecha para evidenciar que la "transferencia + ejecución" del
#  paso T1105 se ha producido y ha sido detectada por el SOC.
#  Sin red, sin cifrado, sin persistencia real, sin daño.
# ============================================================
echo "[demo-soc] payload simulado ejecutado: $(date -Is)" >> /tmp/soc-demo-payload.log
exit 0
