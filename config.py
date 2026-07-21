"""
Configuración del monitor de citas.
Añade aquí nuevos servicios si quieres ampliar el seguimiento.
"""

SERVICIOS = [
    {
        "id": "padron",
        "nombre": "Padrón",
        "centro": "Ayuntamiento de Fuenlabrada",
        "url": (
            "https://citaprevia.ayto-fuenlabrada.es/"
            "qsige.localizador/citaPrevia/"
            "disponible/centro/1/servicio/1/calendario"
        ),
        "enlace": "https://citaprevia.ayto-fuenlabrada.es/"
    },
    {
        "id": "volantes_padron",
        "nombre": "Volantes Padrón",
        "centro": "Ayuntamiento de Fuenlabrada",
        "url": (
            "https://citaprevia.ayto-fuenlabrada.es/"
            "qsige.localizador/citaPrevia/"
            "disponible/centro/1/servicio/2/calendario"
        ),
        "enlace": "https://citaprevia.ayto-fuenlabrada.es/"
    }
]