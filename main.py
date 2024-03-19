import asyncio
import random
import sys
import time

from questionary import (
    questionary,
    Choice
)

from input_data.settings import IS_ACCOUNT_NAMES, IS_SHUFFLE_WALLETS
from min_lib.models.accounts import AccountInfo
from min_lib.models.logger import Logger
from min_lib.utils.helpers import (
    center_output,
    format_input
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


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Claim $ZK and transfer to receivers",
                   [claim_and_transfer, ]),
            Choice("2) Claim $ZK", [claim_and_transfer, ]),
            Choice("3) Transfer $ZK to receivers", ),
            Choice("3) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        exit_label = "========= It's all! ========="
        center_output(exit_label)
        sys.exit()
    return result


async def prepare_task(module, account_model: AccountInfo):
    if isinstance(module, list):
        module_function = module[0]
        return module_function(account_model, *module[1:])
    elif callable(module):
        return module(account_model)
    else:
        raise ValueError("Invalid module format")


def measure_time_for_all_work(start_time: float):
    end_time = round(time.time() - start_time, 2)
    seconds = round(end_time % 60, 2)
    minutes = int(end_time // 60) if end_time > 60 else 0
    hours = int(end_time // 3600) if end_time > 3600 else 0

    logger.info(
        f"Spent time: "
        f"{hours} hours {minutes} minutes {seconds} seconds"
    )


async def main(module):
    accounts = get_accounts()

    if IS_SHUFFLE_WALLETS:
        random.shuffle(accounts)

    tasks = []
    for account in accounts:
        account_model = AccountInfo(
            account_name=account['name'],
            private_key=account['private_key'],
            receiver_wallet=account['receiver']
        )

        task = prepare_task(module, account_model)
        task = fetch_data(site, params, account['proxy'], cookies, headers)
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    for account, result in zip(accounts, results):
        id = str(account['name'])
        cookies = str(account['cookies'])

        volume = fee = 0
        if result is None:
            continue

        for fill_order in result:
            if fill_order["symbol"] != "USDT_USDC":
                volume += float(fill_order["quantity"]) * \
                    float(fill_order["price"])

                if fill_order['side'] == "Bid":
                    fee += float(fill_order["fee"]) * \
                        float(fill_order['price'])
                else:
                    fee += float(fill_order['fee'])
        floated_volume = round(volume, 2)
        floated_fee = round(fee, 2)

if __name__ == "__main__":
    greetings()
    logger = setup_bot_to_start()
    if not logger:
        end_of_work()

    module = get_module()

    start_time = time.time()
    logger.info(
        "The bot started to measure time for all work"
    )

    asyncio.run(main(module))
    measure_time_for_all_work(start_time)
    end_of_work()
