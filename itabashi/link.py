import abc
import asyncio


class RelayLink(metaclass=abc.ABCMeta):
    def __init__(self, name: str, _type: str, bot, config: dict):
        """
        :param _type: The type of link, eg irc/discord
        :param name: The name of this connection
        :param bot: The bot this connection is running under
        :param config: The config for this connection
        """
        self.config = config
        self.__name = name
        self.__type = _type
        self.__bot = bot
        self.__loop = bot.loop
        self.channels = []
        self.connected = False
        self.logger = bot.logger

    def set_channels(self, chans: list):
        if isinstance(chans, str):
            chans = [chans]
        self.channels = chans

    def add_channel(self, chan: str):
        self.channels.append(chan)

    @asyncio.coroutine
    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def message(self, text: str):
        pass

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> str:
        return self.__type

    @property
    def bot(self):
        return self.__bot

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self.__loop

    @abc.abstractmethod
    def __repr__(self) -> str:
        return "Unknown"
