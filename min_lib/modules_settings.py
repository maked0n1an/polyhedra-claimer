from min_lib.models.claimer import Claimer
from min_lib.utils.helpers import delay


async def check(account_info) -> bool:
    claimer = Claimer(account_info)

    result = await claimer._check_eligible()

    if not result:
        return 0
    else:
        _, amount, _ = result
        
    return amount.Ether
        


async def claim_and_transfer(account_info) -> bool:
    claimer = Claimer(account_info)

    result = await claimer.claim()
    if not result:        
        return result        
        
    await delay(10, 20)
    receipt_status, amount = await claimer.transfer()
    
    return amount if receipt_status else 0
    


async def claim(account_info) -> bool:
    receipt_status, amount = await Claimer(account_info).claim()
    
    return amount if receipt_status else 0


async def transfer(account_info) -> bool:
    receipt_status, amount = await Claimer(account_info).transfer()
    
    return amount if receipt_status else 0
