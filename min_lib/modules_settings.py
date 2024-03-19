from min_lib.models.claimer import Claimer
from min_lib.models.constant_models import Status
from min_lib.utils.helpers import delay


async def check(account_info) -> bool:
    claimer = Claimer(account_info)

    result = await claimer._check_eligible()

    if result:
        _, amount, _ = result
        
        return amount.Ether
    else:
        return 0


async def claim_and_transfer(account_info) -> bool:
    claimer = Claimer(account_info)

    result = await claimer.claim()
    if receipt:        
        receipt, amount = result
        await delay(10, 20)
        (receipt, amount) = await claimer.transfer()
    return amount


async def claim(account_info) -> bool:
    claimer = Claimer(account_info)

    result = await claimer.claim()
    if result:
        _, amount = result
    
    return amount or 0


async def transfer(account_info) -> bool:
    claimer = Claimer(account_info)

    _, amount = await claimer.transfer()
    return amount
