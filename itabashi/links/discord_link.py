"""
RelayLink implementation for Discord
"""
import asyncio

import aiohttp
import discord
import websockets
from discord import Message

from itabashi.event import Event, MessageEvent, EventType
from itabashi.link import RelayLink
from italib import backoff

msg_fmt = "[{chan}@{server!r}] **<{nick}>** {message}"
act_fmt = "[{chan}@{server!r}] **\\* {nick}** {message}"

msg_fmt_raw = "[{chan}@{server!r}] <{nick}> {message}"
act_fmt_raw = "[{chan}@{server!r}] *{nick} {message}"


class DiscordLink(RelayLink):
    """
    Provides a Discord link to RelayBot
    """

    def __init__(self, name: str, bot, config: dict):
        super().__init__(name, 'discord', bot, config)
        self.discord_channels = {}
        self.client = discord.Client()

    @asyncio.coroutine
    def connect(self):
        """
        Connects to the Discord API and loads the channel list
        """
        # register the event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

        # guided by https://gist.github.com/Hornwitser/93aceb86533ed3538b6f
        # thanks Hornwitser!
        retry = backoff.ExponentialBackoff()

        # login to Discord
        while True:
            try:
                # if there is an oauth key in the config, us that instead, otherwise use the email and password
                if 'oauth' in self.config:
                    yield from self.client.login(self.config['oauth'])
                else:
                    yield from self.client.login(self.config['email'], self.config['password'])
            except (discord.HTTPException, aiohttp.ClientError):
                self.logger.exception("discord.py failed to login, waiting and retrying")
                yield from asyncio.sleep(retry.delay(), loop=self.loop)
            else:
                break

        # connect to Discord and reconnect when necessary
        while self.client.is_logged_in:
            if self.client.is_closed:
                self.client._closed.clear()
                self.client.http.recreate()

            try:
                yield from self.client.connect()

            except (discord.HTTPException, aiohttp.ClientError,
                    discord.GatewayNotFound, discord.ConnectionClosed,
                    websockets.InvalidHandshake,
                    websockets.WebSocketProtocolError) as e:
                if isinstance(e, discord.ConnectionClosed) and e.code == 4004:
                    raise  # Do not reconnect on authentication failure
                self.logger.exception("discord.py disconnected, waiting and reconnecting")
                yield from asyncio.sleep(retry.delay(), loop=self.loop)

    # retrieve channel objects we use to send messages
    @asyncio.coroutine
    def on_ready(self):
        """
        Handles when we have successfully connected to Discord
        """
        self.logger.debug('Discord -- Logged in as')
        self.logger.debug(self.client.user.name)
        self.logger.debug(self.client.user.id)
        self.logger.debug('------')

        # show all available channels and fill out our internal lists
        self.logger.debug('Available Discord Channels:')
        for channel in self.client.get_all_channels():
            self.logger.debug('#{chan.name} ({chan.id})'.format(chan=channel))
            self.discord_channels[channel.name] = channel

        self.logger.debug('------')

    # dispatching messages
    @asyncio.coroutine
    def on_message(self, message: Message):
        """
        Handles when we have received a message from the Discord API
        :param message: The message object received from the API
        """
        self.logger.debug('discord: raw 1')
        # self.logger.debug('discord: raw 2')
        # dispatch all but our own messages
        if str(message.author) != str(self.client.user):
            full_message = [message.clean_content]
            if not full_message[0]:
                full_message.pop(0)
            for attachment in message.attachments:
                full_message.append(attachment.get('url', 'No URL for attachment'))

            # Create an event corresponding to this message end pass it off to the bot to ahndle
            event = MessageEvent(bot=self.bot, conn=self, nick="{u.name}#{u.discriminator}".format(u=message.author),
                                 chan=str(message.channel.name), message=' '.join(full_message))
            self.logger.debug('discord: raw 2 - dispatching')
            yield from self.bot.handle_message(event)

    @asyncio.coroutine
    def message(self, event: Event, target: str):
        """
        Send a message out on this linmk
        :param event: The Event object to forward
        :param target: Where to send this message
        """
        if isinstance(event, MessageEvent):
            self.logger.debug("[{!r}] >> {}: {}".format(self, target, self.format_event(event, True)))
            assembled_message = self.format_event(event)
            asyncio.async(self.client.send_message(self.discord_channels[target], assembled_message), loop=self.loop)

    def __repr__(self):
        return "Discord:{}".format(self.name)

    def format_event(self, event: MessageEvent, raw: bool = False):
        """
        Format an event to be relayed out to the link
        :param event: The event to format
        :param raw: Should this be a raw or stylized output
        :return: The formatted string
        """
        # TODO(linuxdaemon) cleaner format
        if event.type == EventType.action:
            if raw:
                fmt = act_fmt_raw
            else:
                fmt = act_fmt
        elif event.type == EventType.message:
            if raw:
                fmt = msg_fmt_raw
            else:
                fmt = msg_fmt
        else:
            raise ValueError('No format exists for event type: {!r}'.format(event.type))

        return fmt.format(chan=event.chan, nick=event.nick, message=event.message, server=event.conn)
