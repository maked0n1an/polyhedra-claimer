import sys

from loguru import logger

from min_lib.models.constant_models import Status


class Logger:
    def __init__(self, id: str, address: str, network: str):
        self.id = id
        self.address = address[:6] + "..." + address[-4:]
        self.network = network.capitalize()
        self.logger = logger

    def log_message(self, status: str, message: str):
        self.logger.log(
            status, f"{self.id: <8} | {self.address} | {self.network} | {message}"
        )

    @classmethod
    def setup_logger_for_output(cls):
        logger.remove()
        logger.add(
            sys.stderr,
            format="<white>{time: DD/MM/YYYY HH:mm:ss}</white> | <level>"
            "{level: <8}</level> | <white>{message}</white>"
        )
        logger.add(
            "main.log",
            format="<white>{time: DD/MM/YYYY HH:mm:ss}</white> | <level>"
            "{level: <8}</level> | <white>{message}</white>"
        )
        logger.level(Status.CLAIMED, no=253, color="<green>")
        logger.level(Status.FAILED, no=253, color="<red>")
        logger.level(Status.RETRY, no=261, color="<yellow>")
        logger.level(Status.DELAY, no=262, color="<yellow>")

        return logger
