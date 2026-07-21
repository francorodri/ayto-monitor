"""
Configuración del monitor de citas.
Añade aquí nuevos servicios si quieres ampliar el seguimiento.
"""

SERVICIOS = [
    {
        "id": "padron_ayto",
        "nombre": "Padrón (Altas, Cambios, Modif, Renovación)",
        "centro": "Ayuntamiento de Fuenlabrada",
        "url": (
            "https://citaprevia.ayto-fuenlabrada.es/"
            "qsige.localizador/citaPrevia/"
            "disponible/centro/1/servicio/1/calendario"
        ),
        "enlace": "https://citaprevia.ayto-fuenlabrada.es/citaprevia/#/es/home?uuid=0242a-85e2-064a3-a1eb"
    },
    {
        "id": "padron_jmd_loranca",
        "nombre": "Padrón (Altas, Cambios, Modif, Renovación)",
        "centro": "JMD Loranca",
        "url": (
            "https://citaprevia.ayto-fuenlabrada.es/"
            "qsige.localizador/citaPrevia/"
            "disponible/centro/3/servicio/1/calendario"
        ),
        "enlace": "https://citaprevia.ayto-fuenlabrada.es/citaprevia/#/es/home?uuid=0242a-85e2-064a3-a1eb"
    },
    {
        "id": "padron_jmd_vivero",
        "nombre": "Padrón (Altas, Cambios, Modif, Renovación)",
        "centro": "JMD Vivero",
        "url": (
            "https://citaprevia.ayto-fuenlabrada.es/"
            "qsige.localizador/citaPrevia/"
            "disponible/centro/34/servicio/1/calendario"
        ),
        "enlace": "https://citaprevia.ayto-fuenlabrada.es/citaprevia/#/es/home?uuid=0242a-85e2-064a3-a1eb"
    },
]