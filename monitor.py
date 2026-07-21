import json
import logging
import os
import sys
from datetime import datetime

import requests

from config import SERVICIOS


# -----------------------------
# Configuración
# -----------------------------

ESTADO_FILE = "estado.json"

NTFY_TOPIC = os.getenv("NTFY_TOPIC")

if not NTFY_TOPIC:
    print("ERROR: falta la variable NTFY_TOPIC")
    sys.exit(1)


# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# -----------------------------
# Funciones auxiliares
# -----------------------------


def cargar_estado():
    """
    Carga el estado anterior.
    Permite saber si ya avisamos antes.
    """

    if not os.path.exists(ESTADO_FILE):
        return {}

    with open(ESTADO_FILE, "r") as fichero:
        return json.load(fichero)



def guardar_estado(estado):
    """
    Guarda el estado actual.
    """

    with open(ESTADO_FILE, "w") as fichero:
        json.dump(
            estado,
            fichero,
            indent=2,
            ensure_ascii=False
        )



def formatear_fecha(fecha):
    """
    Convierte:
    2026-07-22

    en:
    miércoles 22/07
    """

    dias = [
        "lunes",
        "martes",
        "miércoles",
        "jueves",
        "viernes",
        "sábado",
        "domingo"
    ]

    fecha_obj = datetime.strptime(
        fecha,
        "%Y-%m-%d"
    )

    return (
        f"{dias[fecha_obj.weekday()]} "
        f"{fecha_obj.strftime('%d/%m')}"
    )



def consultar(servicio):
    """
    Consulta un servicio concreto.
    Devuelve las fechas disponibles.
    """

    try:

        logging.info(
            "Consultando %s",
            servicio["nombre"]
        )

        respuesta = requests.get(
            servicio["url"],
            timeout=20
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        disponibles = [
            dia["dia"]
            for dia in datos.get("dias", [])
            if dia.get("estado") == 0
        ]

        return disponibles


    except requests.RequestException as error:

        logging.error(
            "Error HTTP en %s: %s",
            servicio["nombre"],
            error
        )

        return []


    except Exception as error:

        logging.error(
            "Error procesando %s: %s",
            servicio["nombre"],
            error
        )

        return []



def enviar_ntfy(mensaje):
    """
    Envía una notificación push.
    """

    try:

        respuesta = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=mensaje.encode("utf-8"),
            headers={
                "Title": "🟢 Citas disponibles",
                "Priority": "5",
                "Tags": "calendar"
            },
            timeout=10
        )

        respuesta.raise_for_status()

        logging.info(
            "Notificación enviada"
        )

    except Exception as error:

        logging.error(
            "Error enviando ntfy: %s",
            error
        )



# -----------------------------
# Programa principal
# -----------------------------


def main():

    estado_anterior = cargar_estado()

    estado_actual = {}

    avisos = []


    for servicio in SERVICIOS:

        fechas = consultar(servicio)

        tiene_citas = len(fechas) > 0

        estado_actual[servicio["id"]] = tiene_citas


        # Avisamos solamente cuando aparece algo nuevo
        if tiene_citas and not estado_anterior.get(
            servicio["id"],
            False
        ):

            texto_fechas = "\n".join(
                [
                    f"• {formatear_fecha(f)}"
                    for f in fechas
                ]
            )


            avisos.append(
                "\n".join(
                    [
                        f"📍 {servicio['centro']}",
                        f"📝 {servicio['nombre']}",
                        "",
                        "📅 Fechas:",
                        texto_fechas,
                        "",
                        f"🔗 {servicio['enlace']}"
                    ]
                )
            )


    if avisos:

        mensaje = (
            "🟢 ¡Hay citas disponibles!\n\n"
            +
            "\n\n".join(avisos)
        )

        enviar_ntfy(mensaje)


    else:

        logging.info(
            "Sin novedades"
        )


    guardar_estado(
        estado_actual
    )


if __name__ == "__main__":
    main()