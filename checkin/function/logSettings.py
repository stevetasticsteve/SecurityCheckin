import logging
import logging.handlers

log_format = ('[%(asctime)s] %(levelname)-3s %(filename)s:%(lineno)-8d '
              '%(message)-3s')
logFile = 'checkin_app.log'
logLevel = logging.ERROR


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logLevel)
    handler = logging.handlers.RotatingFileHandler(logFile)
    handler.setLevel(logLevel)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def close_logging(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
    logging.shutdown()
    del logger
