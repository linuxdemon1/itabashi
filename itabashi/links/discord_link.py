import asyncio

from itabashi.link import RelayLink


class DiscordLink(RelayLink):
    def __init__(self, name, bot, config):
        super().__init__(name, 'discord', bot, config)

    @asyncio.coroutine
    def connect(self):
        pass

    def message(self, text):
        pass

    def __repr__(self):
        return "Discord:{}".format(self.name)
