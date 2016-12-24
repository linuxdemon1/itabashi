class Event:
    def __init__(self, _type, nick, chan, link):
        self.type = _type
        self.nick = nick
        self.chan = chan
        self.link = link


class MessageEvent(Event):
    def __init__(self, nick, chan, link, message, *, _type="message"):
        super().__init__(_type, nick, chan, link)
        self.message = message


class ActionEvent(MessageEvent):
    def __init__(self, nick, chan, link, message):
        super().__init__(nick, chan, link, message, _type="action")