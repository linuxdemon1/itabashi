import asyncio
import json
from logging import Logger

import italib
from itabashi.links.discord_link import DiscordLink
from itabashi.links.irc_link import IrcLink
from itabashi.event import Event, MessageEvent, ActionEvent

get_link_by_type = {
    'irc': IrcLink,
    'discord': DiscordLink
}

msg_log_fmt = "[{server!r}] <{nick}:{chan}> {msg}"
action_log_fmt = "[{server!r}] *{nick}:{chan} {msg}"


class RelayBot:
    def __init__(self, logger: Logger, *, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.stopped_future = asyncio.Future()
        self.loop = loop
        self.modules = {}
        self.links = {}
        with open('config.json') as f:
            self.config = json.loads(f.read())

        self.links = self.config["links"]
        self.logger = logger

    def run(self) -> bool:
        # check config version
        if self.config.get('version', 0) < italib.CURRENT_CONFIG_VERSION:
            # TODO(dan): automagic config file updating
            self.logger.fatal('Config format is too old, please update it.')
            print('Config format is too old, please update it.')
            exit(1)

        self.logger.info('Creating links')
        self.loop.run_until_complete(self.link())
        restart = self.loop.run_until_complete(self.stopped_future)
        self.loop.close()
        return restart

    @asyncio.coroutine
    def link(self):
        for connection in self.config['connections']:
            self.modules[connection['name']] = get_link_by_type[connection['type']](connection['name'], self,
                                                                                    connection)

        for name in self.links:
            for link_name, chan in self.links[name]['channels'].items():
                if link_name not in self.modules:
                    raise ValueError(
                        'Connection {} not defined in configuration but is expected by link {}'.format(link_name, name))
                self.modules[link_name].add_channel(chan)

        yield from asyncio.gather(*[conn.connect() for conn in self.modules.values()], loop=self.loop)

    def handle_message(self, event: Event):
        # TODO handle more events
        if isinstance(event, ActionEvent):
            self.logger.info(action_log_fmt.format(chan=event.chan, nick=event.nick, msg=event.message,
                                                   server=event.link))
        elif isinstance(event, MessageEvent):
            self.logger.info(msg_log_fmt.format(chan=event.chan, nick=event.nick, msg=event.message,
                                                server=event.link))
        else:
            self.logger.info("Unknown event received: {!r}".format(event))
