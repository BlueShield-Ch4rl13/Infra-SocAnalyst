# ============================================================
#  Nodo "CLEAN" — Shuffle (acción Execute Python)
#  Limpia la respuesta de Ollama para poder insertarla en el
#  JSON de creación de alerta de TheHive sin romperlo.
# ------------------------------------------------------------
#  Ajusta $ollama.response al nombre real de tu nodo Ollama
#  (si el nodo se llama "OLLAMA" -> $ollama.response).
#  Terminar SIEMPRE con print(json.dumps({...})).
# ============================================================
import json

raw = """$ollama.response"""     # texto generado por la IA local

# La IA puede devolver comillas y saltos de línea que rompen el
# JSON posterior: los neutralizamos a una sola línea segura.
texto = raw.strip().replace('"', "'").replace("\n", " ").replace("\r", " ")

# Recorte defensivo por si el modelo se extiende demasiado.
if len(texto) > 1500:
    texto = texto[:1500] + "..."

print(json.dumps({"analisis": texto}))
