import enum


@enum.unique
class EventType(enum.Enum):
    message = 0
    action = 1
    other = 6


class Event:
    def __init__(self, *, bot=None, conn=None, base_event=None,
                 event_type: EventType = EventType.other, nick: str = None, chan: str = None):
        self.bot = bot
        self.conn = conn
        if base_event is not None:
            if self.bot is None and base_event.bot is not None:
                self.bot = base_event.bot
            if self.conn is None and base_event.conn is not None:
                self.conn = base_event.conn
            self.type = base_event.type
            self.nick = base_event.nick
            self.chan = base_event.chan
        else:
            self.type = event_type
            self.nick = nick
            self.chan = chan


class MessageEvent(Event):
    def __init__(self, *, bot=None, conn=None, base_event=None, nick: str = None,
                 chan: str = None, message: str = None):
        super().__init__(bot=bot, conn=conn, base_event=base_event, event_type=EventType.message, nick=nick, chan=chan)
        self.message = message


class ActionEvent(Event):
    def __init__(self, *, bot=None, conn=None, base_event=None, nick: str = None,
                 chan: str = None, message: str = None):
        super().__init__(bot=bot, conn=conn, base_event=base_event, event_type=EventType.action, nick=nick, chan=chan)
        self.message = message
