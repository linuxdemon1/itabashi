import asyncio

from itabashi.link import RelayLink


class DiscordLink(RelayLink):
    def __init__(self, name: str, bot, config: dict):
        super().__init__(name, 'discord', bot, config)

    @asyncio.coroutine
    def connect(self):
        pass

    def message(self, text: str):
        pass

    def __repr__(self):
        return "Discord:{}".format(self.name)
