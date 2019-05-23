import logging

log_format = ('[%(asctime)s] %(levelname)-3s %(filename)s:%(lineno)-8d '
             '%(message)-3s')
logFile = 'log.log'
logLevel = logging.DEBUG


def createLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logLevel)
    handler = logging.FileHandler(logFile)
    handler.setLevel(logLevel)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def closeLogging(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
    logging.shutdown()
    del logger
