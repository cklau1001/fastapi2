import logging.config
from otel.otel_config import initialize_logger

def setup_logging():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                # "format": "%(asctime)s [%(levelname)s] %(name)s: %(module)s %(funcName)s %(lineno)d %(message)s"
                "format": "%(asctime)s [%(levelname)s] [%(module)s:%(lineno)d] [%(funcName)s]: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            },
            # "file": {
            #    "class": "logging.handlers.RotatingFileHandler",
            #    "formatter": "standard",
            #    "level": "INFO",
            #    "filename": "app.log",
            #    "maxBytes": 1048576, # 1MB
            #    "backupCount": 3,
            #},
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True
            },
        }
    }
    logging.config.dictConfig(config)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = initialize_logger()

    return logger
