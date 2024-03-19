import asyncio
import random
import sys
import time

from questionary import (
    questionary,
    Choice
)
from min_lib.modules_settings import (
    claim,
    check,
    claim_and_transfer, 
    transfer
)
from input_data.settings import AMOUNT_WALLETS_IN_BATCH, IS_ACCOUNT_NAMES, IS_SHUFFLE_WALLETS
from min_lib.models.account_info import AccountInfo
from min_lib.models.logger import Logger
from min_lib.models.networks import Networks
from min_lib.utils.helpers import (
    center_output
)
from min_lib.utils.config import (
    ACCOUNT_NAMES,
    PRIVATE_KEYS,
    RECEIVERS
)


def get_accounts():
    if IS_ACCOUNT_NAMES:
        accounts = [
            {
                "name": account_name,
                "key": private_key,
                "receiver": receiver
            } for account_name, private_key, receiver in zip(ACCOUNT_NAMES, PRIVATE_KEYS, RECEIVERS)
        ]
    else:
        accounts = [
            {
                "name": _id,
                "key": private_key,
                "receiver": receiver
            } for _id, (private_key, receiver) in enumerate(zip(PRIVATE_KEYS, RECEIVERS), start=1)
        ]

    return accounts


def greetings():
    name_label = "========= Polyhedra Claimer ========="
    brand_label = "========== Author: M A K E D 0 N 1 A N =========="
    telegram = "======== https://t.me/crypto_maked0n1an ========"

    print("")
    center_output(name_label)
    center_output(brand_label)
    center_output(telegram)


def measure_time_for_all_work(start_time: float):
    end_time = round(time.time() - start_time, 2)
    seconds = round(end_time % 60, 2)
    minutes = int(end_time // 60) if end_time > 60 else 0
    hours = int(end_time // 3600) if end_time > 3600 else 0

    logger.info(
        f"Spent time: "
        f"{hours} hours {minutes} minutes {seconds} seconds"
    )


def end_of_work():
    exit_label = "========= The bot has ended it's work! ========="
    center_output(exit_label)
    sys.exit()


def setup_bot_to_start():
    logger = Logger.setup_logger_for_output()
    end_bot = False

    if len(PRIVATE_KEYS) == 0:
        logger.error("Don't imported PRIVATE_KEYS in 'private_keys.txt'!")
        return end_bot
    if len(PRIVATE_KEYS) != len(RECEIVERS):
        logger.error("The accounts' amount must be equal to receivers' amount")
        return end_bot
    if len(ACCOUNT_NAMES) == 0 and IS_ACCOUNT_NAMES:
        logger.error("Please insert names into account_names.txt")
        return end_bot
    if len(PRIVATE_KEYS) != len(ACCOUNT_NAMES) and IS_ACCOUNT_NAMES:
        logger.error(
            "The account names' amount must be equal to cookies' amount"
        )
        return end_bot

    return logger


def get_network():
    result = questionary.select(
        "Select a network to get started",
        choices=[
            Choice("1) Binance Smart Chain (BSC)", Networks.BSC),
            Choice("2) Ethereum (ETH)", Networks.Ethereum)
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        exit_label = "========= It's all! ========="
        center_output(exit_label)
        sys.exit()
    return result


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Check $ZK for claim", check),
            Choice("1) Claim $ZK and transfer to receivers",
                   claim_and_transfer),
            Choice("2) Claim $ZK", claim),
            Choice("3) Transfer $ZK to receivers", transfer),
            Choice("4) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        exit_label = "========= It's all! ========="
        center_output(exit_label)
        sys.exit()
    return result


def prepare_task(module, account_model: AccountInfo):
    if callable(module):
        return module(account_model)
    else:
        raise ValueError("Invalid module format")


async def main(module, network):
    accounts = get_accounts()

    if IS_SHUFFLE_WALLETS:
        random.shuffle(accounts)

    amount_of_accounts = len(accounts)
    logger.info(f'Started work on {amount_of_accounts} accounts')
    batches = [accounts[i:i + AMOUNT_WALLETS_IN_BATCH]
               for i in range(0, amount_of_accounts, AMOUNT_WALLETS_IN_BATCH)]
    tasks = []

    total_gotten_tokens = 0
    for batch in batches:
        for account in batch:
            account_model = AccountInfo(
                account_name=account['name'],
                private_key=account['key'],
                receiver_wallet=account['receiver'],
                network=network
            )
            task = prepare_task(module, account_model)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        for result in results:
            total_gotten_tokens += result

        tasks = []

    logger.success(
        f'Successfully done for {amount_of_accounts} accounts | claimed: {total_gotten_tokens}')

if __name__ == "__main__":
    greetings()
    logger = setup_bot_to_start()
    if not logger:
        end_of_work()

    network = get_network()
    module = get_module()

    start_time = time.time()
    logger.info(
        "The bot started to measure time for all work"
    )

    asyncio.run(main(module, network))
    measure_time_for_all_work(start_time)
    end_of_work()
