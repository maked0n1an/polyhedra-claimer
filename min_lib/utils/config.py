from min_lib.utils.helpers import (
    read_txt,
    load_json
)


PRIVATE_KEYS = read_txt('input_data/private_keys.txt') 
ACCOUNT_NAMES = read_txt('input_data/account_names.txt')
RECEIVERS = read_txt('input_data/receivers.txt')
    
CLAIM_ABI = load_json('data/claim_abi.json')
TOKEN_ABI = load_json('data/token_abi.json')
