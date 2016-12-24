import asyncio
import ssl
from _ssl import PROTOCOL_SSLv23
from ssl import SSLContext

import girc
from girc.formatting import escape, remove_formatting_codes

import itabashi
from bot import RelayBot
from itabashi.event import MessageEvent, ActionEvent
from itabashi.link import RelayLink


class IrcLink(RelayLink):
    def __init__(self, name: str, bot: RelayBot, config: dict):
        super().__init__(name, 'irc', bot, config)
        self.server = self.config['server']
        self.port = self.config['port']
        self.use_ssl = self.config['tls']
        self.verify_ssl = self.config['tls_verify']
        self.nick = self.config['nickname']
        self.ident = self.config.get('user', 'ita')
        self.gecos = self.config.get('realname', 'itabashi relay bot')
        self.link = None
        self.reactor = None

        if self.use_ssl:
            self.ssl_context = SSLContext(PROTOCOL_SSLv23)
            if not self.verify_ssl:
                self.ssl_context.verify_mode = ssl.CERT_NONE
            else:
                self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            self.ssl_context = None

    @asyncio.coroutine
    def connect(self):
        self.reactor = girc.Reactor()
        self.reactor.register_event('in', 'raw', self.handle_reactor_raw_in, priority=1)
        self.reactor.register_event('out', 'raw', self.handle_reactor_raw_out, priority=1)
        self.reactor.register_event('in', 'ctcp', self.handle_reactor_ctcp)
        self.reactor.register_event('in', 'pubmsg', self.handle_reactor_pubmsgs)
        self.reactor.register_event('in', 'pubaction', self.handle_reactor_pubactions)

        self.link = self.reactor.create_server('ita')
        self.link.set_user_info(self.nick, self.ident, self.gecos)
        self.link.join_channels(*self.channels)
        if 'nickserv_password' in self.config:
            self.link.nickserv_identify(self.config['nickserv_password'])

        self.link.connect(self.server, self.port, ssl=self.ssl_context)

        self.logger.info('irc: Started and connected to {}/{}'.format(self.server, self.port))

    def message(self, text: str):
        pass

    # display
    def handle_reactor_raw_in(self, event: dict):
        try:
            self.logger.debug('raw irc: {}  -> {}'.format(event['server'].name, escape(event['data'])))
        except (UnicodeDecodeError, UnicodeEncodeError):
            self.logger.debug('raw irc: {}  -> {}'.format(event['server'].name, 'Data coule not be displayed'))

    def handle_reactor_raw_out(self, event: dict):
        try:
            self.logger.debug('raw irc: {} <-  {}'.format(event['server'].name, escape(event['data'])))
        except (UnicodeDecodeError, UnicodeEncodeError):
            self.logger.debug('raw irc: {} <-  {}'.format(event['server'].name, 'Data could not be displayed'))

    # VERSION and such
    def handle_reactor_ctcp(self, event: dict):
        if event['ctcp_verb'] == 'version':
            event['source'].ctcp_reply('VERSION', 'Itabashi (板橋)/{}'.format(itabashi.__version__))
        elif event['ctcp_verb'] == 'source':
            event['source'].ctcp_reply('SOURCE', 'https://github.com/bibanon/itabashi')
        elif event['ctcp_verb'] == 'clientinfo':
            event['source'].ctcp_reply('CLIENTINFO', 'ACTION CLIENTINFO SOURCE VERSION')

    # dispatching messages
    def handle_reactor_pubmsgs(self, event: dict):
        self.message_received(event, 'message')

    def handle_reactor_pubactions(self, event: dict):
        self.message_received(event, 'action')

    def message_received(self, info: dict, _type: str):
        if info['source'].is_me:
            return

        if _type == 'message':
            event = MessageEvent(nick=info['source'].nick, chan=info['channel'].name, link=self,
                                 message=remove_formatting_codes(info['message']))
        elif _type == 'action':
            event = ActionEvent(nick=info['source'].nick, chan=info['channel'].name, link=self,
                                message=remove_formatting_codes(info['message']))
        else:
            raise ValueError('Invalid value for parameter _type: {}'.format(_type))

        self.bot.handle_message(event)

    def __repr__(self) -> str:
        return "IRC:{}".format(self.name)
