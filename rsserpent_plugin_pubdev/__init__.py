from rsserpent.models import Persona, Plugin

from . import route


plugin = Plugin(
    name="rsserpent-plugin-pubdev",
    author=Persona(
        name="Ekko",
        link="https://github.com/EkkoG",
        email="beijiu572@gmail.com",
    ),
    prefix="/pubdev/update",
    repository="https://github.com/EkkoG/rsserpent-plugin-pubdev",
    routers={
        route.path: route.provider,
    },
)
