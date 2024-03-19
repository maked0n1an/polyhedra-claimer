from min_lib.models.accounts import AccountInfo
from min_lib.models.claimer import Claimer
from min_lib.utils.helpers import delay
        
        
async def claim_and_transfer(account_info: AccountInfo) -> bool:   
    claimer = Claimer(account_info)
        
    if await claimer.claim():
        await delay(6, 20)
        await claimer.transfer() 
        
        
async def claim(account_info: AccountInfo) -> bool:   
    claimer = Claimer(account_info)
        
    return await claimer.claim()  

async def transfer(account_info: AccountInfo) -> bool:
    claimer = Claimer(account_info)
        
    return await claimer.transfer()  
        
        
    
     