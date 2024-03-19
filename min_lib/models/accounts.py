import random
from typing import Any
from hexbytes import (
    HexBytes
)

from web3 import Web3, AsyncWeb3
from web3.types import (
    TxReceipt,
    TxParams,
    _Hash32,
)
from web3.eth import AsyncEth
from web3.contract import Contract

from eth_typing import ChecksumAddress
from eth_account import Account as EthAccount
from eth_account.signers.local import LocalAccount
from eth_account.datastructures import (
    SignedTransaction,
    SignedMessage
)

from min_lib.models.common import TokenAmount
from min_lib.models.logger import Logger
from min_lib.models.networks import (
    Network,
    Networks
)


class AccountInfo:
    def __init__(
        self,
        account_name: str | int,
        private_key: str,
        receiver_wallet: str,
        network: Network | None = Networks.BSC
    ) -> None:
        self.id = str(account_name)
        self.private_key = private_key
        self.receiver = receiver_wallet
        self.network = network


class Account:
    def __init__(self, account_info: AccountInfo):
        self.account_info = account_info
        self.receiver = account_info.receiver
        self.network = account_info.network

        self.web3 = Web3(
            AsyncWeb3.AsyncHTTPProvider(
                random.choice(self.account_info.network.rpc)
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[],
        )
        self.account: LocalAccount = EthAccount.from_key(
            account_info.private_key
        )
        self.address = self.account.address
        self.logger = Logger(self.account_info.id, self.account.address)

    def get_contract(self, contract_address: ChecksumAddress | str, abi: Any) -> Contract:
        contract_address = Web3.to_checksum_address(contract_address)

        contract = self.web3.eth.contract(address=contract_address, abi=abi)

        return contract

    def sign_transaction(self, tx_params: TxParams) -> SignedTransaction:
        signed_tx = self.account.sign_transaction(
            transaction_dict=tx_params
        )

        return signed_tx

    def sign_message(self, message: str) -> SignedMessage:
        signed_message = self.account.sign_message(
            signable_message=message
        )

        return signed_message

    async def get_nonce(self, address: ChecksumAddress | None = None) -> int:
        if not address:
            address = self.address

        nonce = await self.web3.eth.get_transaction_count(address)
        return nonce

    async def get_gas_price(self) -> TokenAmount:
        amount = await self.web3.eth.gas_price

        return TokenAmount(
            amount=amount,
            decimals=self.network.decimals,
            wei=True
        )

    async def get_max_priority_fee(self) -> TokenAmount:
        max_priority_fee = await self.web3.eth.max_priority_fee

        return TokenAmount(
            max_priority_fee,
            decimals=self.network.decimals,
            wei=True
        )

    async def get_estimate_gas(self, tx_params: TxParams) -> TokenAmount:
        gas_price = await self.web3.eth.estimate_gas(transaction=tx_params)

        return TokenAmount(
            gas_price,
            decimals=self.network.decimals,
            wei=True
        )

    async def wait_for_tx_receipt(
        self,
        tx_hash: _Hash32,
        web3: Web3 | AsyncWeb3,
        timeout: int | float = 120,
        poll_latency: float = 0.1
    ) -> TxReceipt:
        self.receipt = await web3.eth.wait_for_transaction_receipt(
            transaction_hash=tx_hash, timeout=timeout, poll_latency=poll_latency
        )

        return self.receipt

    async def auto_add_params(self, tx_params: TxParams | dict) -> TxParams:
        if 'chainId' not in tx_params:
            tx_params['chainId'] = self.network.chain_id

        if not tx_params.get('nonce'):
            tx_params['nonce'] = await self.get_nonce()

        if 'from' not in tx_params:
            tx_params['from'] = self.account.address

        is_eip_1559_tx_type = self.network.tx_type == 2
        current_gas_price = await self.get_gas_price()

        if is_eip_1559_tx_type:
            tx_params['maxFeePerGas'] = tx_params.pop(
                'gasPrice', current_gas_price.Wei)

        elif 'gasPrice' not in tx_params:
            tx_params['gasPrice'] = current_gas_price.Wei

        if 'maxFeePerGas' in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (await self.get_max_priority_fee()).Wei
            tx_params['maxFeePerGas'] += tx_params['maxPriorityFeePerGas']

        multiplier_of_gas = tx_params.pop('multiplier', 1)

        if not tx_params.get('gas') or not int(tx_params['gas']):
            gas = await self.get_estimate_gas(tx_params=tx_params)
            tx_params['gas'] = int(gas.Wei * multiplier_of_gas)

        return tx_params

    async def sign_and_send(self, tx_params: TxParams) -> HexBytes:
        tx_params = await self.auto_add_params(tx_params)
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.web3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

        return tx_hash
    
    async def get_balance(self, address_contract) -> int:
        contract = self.get_contract(address_contract, abi=token_abi)
        try:
            balance = await contract.functions.balanceOf(self.address).call()
            return balance
        except Exception as e:
            logger.error(f'{self.acc_info} - {e}')
            await asyncio.sleep(1)
            return await self.get_balance(address_contract)
