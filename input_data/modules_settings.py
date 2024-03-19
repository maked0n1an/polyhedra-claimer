from min_lib.models.accounts import AccountInfo
from min_lib.models.claimer import Claimer
from min_lib.utils.helpers import delay
        
        
async def claim_and_transfer(account_info: AccountInfo) -> bool:   
    claimer = Claimer(account_info)
        
    receipt, amount = await claimer.claim()
    if receipt: 
        await delay(6, 20)
        receipt, amount = await claimer.transfer()        
    return amount
        
        
async def claim(account_info: AccountInfo) -> bool:   
    claimer = Claimer(account_info)
        
    _, amount = await claimer.claim()
    return amount

async def transfer(account_info: AccountInfo) -> bool:
    claimer = Claimer(account_info)
        
    _, amount = await claimer.transfer()  
    return amount
        
        
    
     