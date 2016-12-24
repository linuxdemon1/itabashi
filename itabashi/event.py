from link import RelayLink


class Event:
    def __init__(self, _type: str, nick: str, chan: str, conn: RelayLink):
        self.type = _type
        self.nick = nick
        self.chan = chan
        self.conn = conn


class MessageEvent(Event):
    def __init__(self, nick: str, chan: str, conn: RelayLink, message: str, *, _type: str = "message"):
        super().__init__(_type, nick, chan, conn)
        self.message = message


class ActionEvent(MessageEvent):
    def __init__(self, nick: str, chan: str, conn: RelayLink, message: str):
        super().__init__(nick, chan, conn, message, _type="action")
