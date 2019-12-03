import logging
import logging.config

dictLogConfig = {
    "version": 1,
    "handlers": {
        "fileHandler": {
            "class": "logging.FileHandler",
            "formatter": "myFormatter",
            "filename": "config2.log"
        },
        "streamHandler": {
            "class": "logging.StreamHandler",
            "formatter": "myFormatter",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "fileGenApp": {
            "handlers": ["fileHandler"],
            "level": "INFO",
        },
        "": {
            "handlers": ["streamHandler"],
            "level": "INFO",
        }
    },
    "formatters": {
        "myFormatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%d-%b-%y %H:%M:%S"
        }
    }
}

logging.config.dictConfig(dictLogConfig)
LOGGER = logging.getLogger("fileGenApp")