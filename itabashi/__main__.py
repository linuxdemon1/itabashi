"""itabashi - Itabashi Discord-IRC linker.

Usage:
    itabashi connect [--log=<log>]
    itabashi --version
    itabashi (-h | --help)

Options:
    connect        Connect to the Discord and IRC channels.
    --log=<log>    Log to the specified filename [default: itabashi.log].
    --version      Show the running version of Itabashi.
    (-h | --help)  Show this message.
"""
import logging

from docopt import docopt

import itabashi
from itabashi.bot import RelayBot


def main():
    arguments = docopt(__doc__, version=itabashi.__version__)
    if arguments['connect']:
        # logging.basicConfig(filename=arguments['--log'], level=logging.DEBUG)
        logger = logging.getLogger('itabashi')
        logger.info('Logger started')

        _bot = RelayBot(logger)
        restart = _bot.run()
    else:
        print('No valid arguments specified')
        exit(1)

if __name__ == "__main__":
    main()
