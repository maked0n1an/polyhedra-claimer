from typing import List
from web3 import Web3

from input_data.settings import YOUR_RPC
from min_lib.models.common import Singleton
from min_lib.models.constant_models import TokenSymbol


class Network:
    TxPath: str = "/tx/"
    ContractPath: str = "/contract/"
    AddressPath: str = "/address/"

    def __init__(
        self,
        name: str,
        rpc: str | List[str],
        chain_id: int | None = None,
        tx_type: int = 0,
        coin_symbol: str | None = None,
        decimals: int | None = None,
        explorer: str | None = None,
    ) -> None:
        self.name: str = name.lower()
        self.rpc: str | List[str] = rpc
        self.chain_id: int | None = chain_id
        self.tx_type: int = tx_type
        self.coin_symbol: str | None = coin_symbol
        self.decimals: int | None = decimals
        self.explorer: str | None = explorer

        self._initialize_chain_id()
        self._coin_symbol_to_upper()

    def _initialize_chain_id(self):
        if self.chain_id:
            return
        try:
            self.chain_id = Web3(Web3.HTTPProvider(self.rpc)).eth.chain_id
        except Exception as err:
            raise Exception(f'Can not get chainId: {err}')

    def _coin_symbol_to_upper(self):
        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()


class Networks(metaclass=Singleton):
    # Mainnet
    Ethereum = Network(
        name='ethereum',
        rpc=YOUR_RPC['ethereum'],
        chain_id=1,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://etherscan.io',
    )

    BSC = Network(
        name='bsc',
        rpc=YOUR_RPC['bsc'],
        chain_id=56,
        tx_type=0,
        coin_symbol=TokenSymbol.BNB,
        decimals=18,
        explorer='https://bscscan.com'
    )

    @classmethod
    def get_network(
        cls,
        network_name: str,
    ) -> Network:
        network_name = network_name.capitalize()

        if not hasattr(cls, network_name):
            raise Exception(
                f"The network has not been added to {__class__.__name__} class"
            )

        return getattr(cls, network_name)
