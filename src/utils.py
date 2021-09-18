import logging


def get_logger() -> logging.Logger:
    """
    Function that will return an instance of logger

    Returns:
        logging.Logger - instance
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    return logger
