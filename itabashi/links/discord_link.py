import asyncio

from itabashi.link import RelayLink
from itabashi.event import Event, MessageEvent, EventType


class DiscordLink(RelayLink):
    def __init__(self, name: str, bot, config: dict):
        super().__init__(name, 'discord', bot, config)

    @asyncio.coroutine
    def connect(self):
        pass

    @asyncio.coroutine
    def message(self, event: Event, target: str):
        if isinstance(event, MessageEvent):
            self.logger.debug("[{!r}] >> {}".format(self, self.format_event(event)))

    def __repr__(self):
        return "Discord:{}".format(self.name)

    def format_event(self, event: MessageEvent):
        if event.type == EventType.action:
            return "*{chan}@{server!r}:{nick} {message}".format(chan=event.chan, nick=event.nick, message=event.message,
                                                                server=event.conn)
        elif event.type == EventType.message:
            return "<{chan}@{server!r}:{nick}> {message}".format(chan=event.chan, nick=event.nick, message=event.message,
                                                                 server=event.conn)
        else:
            raise ValueError('No format exists for event type: {!r}'.format(event.type))
