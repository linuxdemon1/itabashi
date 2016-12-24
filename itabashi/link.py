import abc
import asyncio


class RelayLink(metaclass=abc.ABCMeta):
    def __init__(self, name, _type, bot, config):
        """
        :type name: str
        :type type: str
        :type bot: RelayBot
        :type config: dict
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

    def set_channels(self, chans):
        if isinstance(chans, str):
            chans = [chans]
        self.channels = chans

    def add_channel(self, chan):
        self.channels.append(chan)

    @asyncio.coroutine
    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def message(self, text):
        pass

    @property
    def name(self):
        return self.__name

    @property
    def type(self):
        return self.__type

    @property
    def bot(self):
        return self.__bot

    @property
    def loop(self):
        return self.__loop
