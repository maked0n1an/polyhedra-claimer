# Do you want to use wallet names or generate ID's by program?
#   Use own names: True
#   Generate IDs: False
IS_ACCOUNT_NAMES = False

# Нужно ли мешать кошельки? | Да - 1, Нет - 0
IS_SHUFFLE_WALLETS = True

AMOUNT_WALLETS_IN_BATCH = 1

DELAY_FROM: int = 20
DELAY_TO: int = 30

AUTH_MESSAGE = ''

TOKEN_CONTRACT = '0xC71B5F631354BE6853eFe9C3Ab6b9590F8302e81'

ETH_CLAIM_ADDRESS = ''
BSC_CLAIM_ADDRESS = ''

YOUR_RPC: dict[str, dict[str, str]] = {
    'ethereum': [
        'https://mainnet.infura.io/v3/5a38002f5097422f915463007e2a3cdf',
        'https://rpc.ankr.com/eth/0ea9694513176ac3ac87e9a5c9c16663b119804f6b8283f923c62c923a98b644',
        'https://rpc.ankr.com/eth/84b4a7faad0df9bf76db0aca528ff21d1c5457d37af0445bf806df3a8de9a062',
        'https://rpc.ankr.com/eth/00e8ed9715664ae8868453878715c9e3c8a15193b1b02df6e65e722d999536aa',
    ],
    'bsc': [
        'https://rpc.ankr.com/bsc/0ea9694513176ac3ac87e9a5c9c16663b119804f6b8283f923c62c923a98b644',
        'https://rpc.ankr.com/bsc/84b4a7faad0df9bf76db0aca528ff21d1c5457d37af0445bf806df3a8de9a062',
        'https://rpc.ankr.com/bsc/00e8ed9715664ae8868453878715c9e3c8a15193b1b02df6e65e722d999536aa',
        'https://rpc.ankr.com/bsc/f4e57e2e7cefa90226b56cea4c994115927c8cf3dc044a65ef694045d139939d'
    ]
}

RETRY_COUNT = 3