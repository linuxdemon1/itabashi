from link import RelayLink


class Event:
    def __init__(self, _type: str, nick: str, chan: str, link: RelayLink):
        self.type = _type
        self.nick = nick
        self.chan = chan
        self.link = link


class MessageEvent(Event):
    def __init__(self, nick: str, chan: str, link: RelayLink, message: str, *, _type: str = "message"):
        super().__init__(_type, nick, chan, link)
        self.message = message


class ActionEvent(MessageEvent):
    def __init__(self, nick: str, chan: str, link: RelayLink, message: str):
        super().__init__(nick, chan, link, message, _type="action")
