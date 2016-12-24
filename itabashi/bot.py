import asyncio
import json

from itabashi.links.discord_link import DiscordLink
from itabashi.links.irc_link import IrcLink

get_link_by_type = {
    'irc': IrcLink,
    'discord': DiscordLink
}


class RelayBot:
    def __init__(self, logger, *, loop=asyncio.get_event_loop()):
        self.loop = loop
        self.modules = {}
        self.links = {}
        with open('config.json') as f:
            self.config = json.loads(f.read())[0]

        self.links = self.config["links"]
        self.logger = logger

    @asyncio.coroutine
    def link(self):
        for connection in self.config['connections']:
            self.modules[connection['name']] = get_link_by_type[connection['type']](connection['name'], self,
                                                                                    connection, loop=self.loop)

        for name in self.links:
            for link_name, chan in self.links[name]['channels'].items():
                if link_name not in self.modules:
                    raise ValueError(
                        'Connection {} not defined in configuration but is expected by link {}'.format(link_name, name))
                self.modules[link_name].add_channel(chan)

        yield from asyncio.gather(*[conn.connect() for conn in self.modules.values()], loop=self.loop)

    def handle_message(self, event):
        pass
