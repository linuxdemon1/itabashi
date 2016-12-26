"""
The base link to be inherited by other link  classes
"""
import abc
import asyncio

from itabashi.event import Event


class RelayLink(metaclass=abc.ABCMeta):
    """
    An abstract class representing the basic structure of an outgoing link
    """

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
        """
        Set what chjannels this link should be connected to
        :param chans: The list to set
        """
        if isinstance(chans, str):
            chans = [chans]
        self.channels = chans

    def add_channel(self, chan: str):
        """
        Add a channel to the links list of channels to connect to
        :param chan: The channel to add
        """
        self.channels.append(chan)

    @asyncio.coroutine
    @abc.abstractmethod
    def connect(self):
        """
        An abstract method that should be overridden and be used to connect the link to the external server
        """
        raise NotImplementedError

    @asyncio.coroutine
    @abc.abstractmethod
    def message(self, event: Event, target: str):
        """
        An abstract method to be used to send a message to this link
        :param event: The event that should be relayed
        :param target: Where to send the message
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        A property representing the name of this connection
        :return: The name
        """
        return self.__name

    @property
    def type(self) -> str:
        """
        A property representing the type of connection
        :return: The type
        """
        return self.__type

    @property
    def bot(self):
        """
        A property representing the bot this link is launched from
        :return: The bot reference
        """
        return self.__bot

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """
        A property representing the event loop this link is using
        :return: The event loop reference
        """
        return self.__loop

    @abc.abstractmethod
    def __repr__(self) -> str:
        return "Unknown"
