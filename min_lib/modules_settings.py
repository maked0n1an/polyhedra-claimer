from min_lib.models.claimer import Claimer
from min_lib.utils.helpers import delay


async def check(account_info) -> bool:
    claimer = Claimer(account_info)

    amount = await claimer._check_eligible()

    return amount


async def claim_and_transfer(account_info) -> bool:
    claimer = Claimer(account_info)

    receipt, amount = await claimer.claim()
    if receipt:
        await delay(6, 15)
        receipt, amount = await claimer.transfer()
    return amount


async def claim(account_info) -> bool:
    claimer = Claimer(account_info)

    _, amount = await claimer.claim()
    return amount


async def transfer(account_info) -> bool:
    claimer = Claimer(account_info)

    _, amount = await claimer.transfer()
    return amount
