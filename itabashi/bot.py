"""
The main bot to handle all the links and relays
"""
import asyncio
import json
from logging import Logger

import italib
from itabashi.event import Event, MessageEvent, ActionEvent
from itabashi.links.discord_link import DiscordLink
from itabashi.links.irc_link import IrcLink

get_link_by_type = {
    'irc': IrcLink,
    'discord': DiscordLink
}

msg_log_fmt = "[{server!r}] <{nick}:{chan}> {msg}"
action_log_fmt = "[{server!r}] *{nick}:{chan} {msg}"


class RelayBot:
    """
    Bot to handle relaying messages between links
    """

    def __init__(self, logger: Logger, *, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.stopped_future = asyncio.Future()
        self.loop = loop
        self.connections = {}
        self.links = {}
        with open('config.json') as f:
            self.config = json.loads(f.read())

        self.links = self.config["links"]
        self.logger = logger

    def run(self) -> bool:
        """
        Runs the bot
        :return: Returns whether or not the bot should be restarted
        """
        # TODO(linuxdaemon): implement the restart functionality
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
        """
        Initiate the outgoing links
        """
        for connection in self.config['connections']:
            self.connections[connection['name']] = get_link_by_type[connection['type']](connection['name'], self,
                                                                                        connection)

        for name in self.links:
            for chan in self.links[name]['channels']:
                if chan["connection"] not in self.connections:
                    raise ValueError(
                        'Connection {} not defined in configuration but is expected by link {}'.format(link_name, name))
                for c in chan["channels"]:
                    self.connections[chan["connection"]].add_channel(c)

        yield from asyncio.gather(*[conn.connect() for conn in self.connections.values()], loop=self.loop)

    @asyncio.coroutine
    def handle_message(self, event: Event):
        """
        Handle a message form one of our links
        :param event: The event corresponding to the message to handle
        """
        # TODO handle more events
        if isinstance(event, ActionEvent):
            self.logger.info(action_log_fmt.format(chan=event.chan, nick=event.nick, msg=event.message,
                                                   server=event.conn))
        elif isinstance(event, MessageEvent):
            self.logger.info(msg_log_fmt.format(chan=event.chan, nick=event.nick, msg=event.message,
                                                server=event.conn))
        else:
            self.logger.info("Unknown event received: {!r}".format(event))

        if isinstance(event, MessageEvent):
            links = self.get_links_to_send_to(event)
            conns = [(self.connections[name.lower()], chans) for name, chans in links]
            tasks = []
            for conn, chans in conns:
                for chan in chans:
                    tasks.append(conn.message(event=event, target=chan))
            yield from asyncio.gather(*tasks, loop=self.loop)

    def get_links_to_send_to(self, event: Event) -> list:
        """
        Get what links a message should be relayed to
        :param event: The event corresponding to the message
        :return: The list of links to relay to
        """
        links = {}
        chans = {}
        # TODO(linuxdaemon): clean up this mess
        for name, link in self.links.items():
            for chan in link['channels']:
                if event.conn.name.lower() == chan['connection'].lower() \
                        and event.chan.lower() in chan['channels']:
                    links[name] = link
                    break
        for name, link in links.items():
            for chan in link['channels']:
                chans.setdefault(chan['connection'], []).extend(chan['channels'])
        chans[event.conn.name.lower()].remove(event.chan.lower())
        return list(chans.items())
