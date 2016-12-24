import json
import os

import logging
import logging.config

__version__ = '0.2.0'

__all__ = ['bot', 'link', 'logging_dir', 'links']

logging_dir = ""


def _setup():
    if os.path.exists(os.path.abspath("config.json")):
        with open(os.path.abspath("config.json")) as config_file:
            json_conf = json.load(config_file)
        logging_config = json_conf.get("logging", {})
    else:
        logging_config = {}

    global logging_dir
    logging_dir = os.path.join(os.path.abspath(os.path.curdir), "logs")

    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)

    logging.captureWarnings(True)

    dict_config = {
        "version": 1,
        "formatters": {
            "brief": {
                "format": "[%(asctime)s] [%(levelname)s] %(message)s",
                "datefmt": "%H:%M:%S"
            },
            "full": {
                "format": "[%(asctime)s] [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d][%H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1000000,
                "backupCount": 5,
                "formatter": "full",
                "level": "INFO",
                "encoding": "utf-8",
                "filename": os.path.join(logging_dir, "bot.log")
            }
        },
        "loggers": {
            "itabashi": {
                "level": "DEBUG",
                "handlers": ["console", "file"]
            }
        }
    }

    if logging_config.get("console_debug", False):
        dict_config["handlers"]["console"]["level"] = "DEBUG"
        dict_config["loggers"]["asyncio"] = {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        }

    if logging_config.get("file_debug", True):
        dict_config["handlers"]["debug_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1000000,
            "backupCount": 5,
            "formatter": "full",
            "encoding": "utf-8",
            "level": "DEBUG",
            "filename": os.path.join(logging_dir, "debug.log")
        }
        dict_config["loggers"]["itabashi"]["handlers"].append("debug_file")

    logging.config.dictConfig(dict_config)

_setup()
