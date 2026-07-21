import json
import os
import requests
from pathlib import Path

URL = "https://citaprevia.ayto-fuenlabrada.es/qsige.localizador/citaPrevia/disponible/centro/1/servicio/1/calendario"
NTFY_TOPIC = os.environ["NTFY_TOPIC"]

ESTADO_FILE = Path("estado.json")

# Leer estado anterior
if ESTADO_FILE.exists():
    estado_anterior = json.loads(ESTADO_FILE.read_text())
else:
    estado_anterior = {"hay_disponibilidad": False}

# Consultar API
r = requests.get(URL, timeout=20)
r.raise_for_status()
data = r.json()

disponibles = [
    d["dia"]
    for d in data["dias"]
    if d["estado"] == 0
]

hay_ahora = len(disponibles) > 0
habia_antes = estado_anterior.get("hay_disponibilidad", False)

# Solo avisar cuando pasamos de False -> True
if hay_ahora and not habia_antes:

    mensaje = (
        "✅ Hay citas disponibles para el padrón en Fuenlabrada.\n\n"
        + "\n".join(disponibles)
    )

    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=mensaje.encode("utf-8"),
        headers={
            "Title": "Cita Ayuntamiento",
            "Priority": "5"
        }
    )

    print("Notificación enviada")

elif hay_ahora:
    print("Ya había disponibilidad; no se envía aviso")

else:
    print("Sin citas disponibles")

# Guardar nuevo estado
ESTADO_FILE.write_text(
    json.dumps({"hay_disponibilidad": hay_ahora})
)
