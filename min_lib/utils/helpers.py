import asyncio
import json
import random
from pathlib import Path

from min_lib.models.logger import logger
from input_data.settings import (
    DELAY_FROM,
    DELAY_TO,
    RETRY_COUNT
)
from min_lib.models.constant_models import Status


def center_output(message: str):
    print(f"| {message:^59}|")


def format_input(message: str) -> str:
    print(f"| {message:^59}|", end='\n| ', flush=True)
    value = input()

    return value


def read_txt(filepath: Path | str):
    with open(filepath, 'r') as file:
        return [row.strip() for row in file]


def load_json(filepath: Path | str):
    with open(filepath, 'r') as file:
        return json.load(file)


def retry(func):
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries <= RETRY_COUNT:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error | {e}")
                await delay(3, 5, f"One more retry: {retries}/{RETRY_COUNT}")
                retries += 1

    return wrapper


async def delay(
    sleep_from:
    int = DELAY_FROM,
    sleep_to: int = DELAY_TO,
    message: str = ""
) -> None:
    delay_secs = random.randint(sleep_from, sleep_to)
    logger.log(Status.DELAY, f"{message} - waiting for {delay_secs}")
    await asyncio.sleep(delay_secs)
