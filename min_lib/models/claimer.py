import aiohttp
import json

from web3 import Web3
from web3.types import TxParams
from eth_account.messages import encode_defunct
from eth_utils import to_hex

from input_data.settings import (
    AUTH_MESSAGE,
    ETH_CLAIM_ADDRESS,
    BSC_CLAIM_ADDRESS,
    TOKEN_CONTRACT
)
from min_lib.models.accounts import Account
from min_lib.models.common import TokenAmount
from min_lib.models.constant_models import Status
from min_lib.models.networks import Networks
from min_lib.utils.helpers import retry


class Claimer(Account):
    CLAIM_CONTRACTS = {
        Networks.BSC.name:      BSC_CLAIM_ADDRESS,
        Networks.Ethereum.name: ETH_CLAIM_ADDRESS
    }

    async def _send_request(
        self,
        method: str = 'GET',
        url: str = '',
        headers: dict[str] = None,
        params: dict[str] = None,
        proxy: str = None
    ) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                request = await session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    proxy=proxy
                )
                return await request.json()
        except Exception as e:
            self.logger.log_message(
                status=Status.ERROR,
                message=f"An error while sending request: {e}"
            )
            return False
        
    async def _check_eligible(self) -> bool:
        try:
            addr_prefix = str(self.account.address).lower()[2:5]
            
            if self.network.name == Networks.Ethereum.name:
                url=f"https://pub-88646eee386a4ddb840cfb05e7a8d8a5.r2.dev/eth_data/{addr_prefix}.json"
            else:
                url=f"https://pub-88646eee386a4ddb840cfb05e7a8d8a5.r2.dev/bsc_data/{addr_prefix}.json"            
            
            response = await self._send_request(
                method='GET',
                url=url
            )
            if response is None:
                return 0
            else:
                amount = TokenAmount(
                    amount=int(str(response[self.account.address]['amount']), 16),
                    wei=True
                )
                
                self.logger.log_message(
                    Status.SUCCESS,
                    f'Found {amount.Ether} available for claim!'  
                )
                
                return float(amount.Ether)
        except Exception as e:
            self.logger.log_message(
                status=Status.ERROR,
                message=f"An error while checking for eligibility: {e}"
            )
            return False

    async def _get_proof(self) -> tuple[str, TokenAmount, str]:
        try:
            if not await self._check_eligible():
                self.logger.log_message(
                    status=Status.FAILED,
                    message=f"Account is not eligible for $ZK airdrop"
                )

            message = AUTH_MESSAGE
            sign = self.sign_message(encode_defunct(text=message))

            data = await self._send_request(
                method='POST',
                url='https://api-ribbon.vercel.app/api/aevo/airdrop-proof',
                params={
                    'address': self.address,
                    'message': message,
                    'signature': to_hex(sign.signature),
                }
            )

            if not data:
                return
            data = data['data']['claim']
            amount = TokenAmount(
                amount=int(data['amount'], 16),
                wei=True
            )
            return int(data['index']), amount, data['proof']

        except Exception as e:
            self.logger.log_message(
                status=Status.ERROR,
                message=f"An error occurred: {e}"
            )
            return

    

    @retry
    async def claim(
        self
    ) -> bool:
        try:
            contract = await self.get_contract(
                token=Web3.to_checksum_address(
                    self.CLAIM_CONTRACTS[self.network.name]
                )
            )

            index, amount, proof = await self._get_proof()
            if not amount:
                return False

            tx_params = TxParams(
                to=contract.address,
                data=contract.encodeABI(
                    'claim',
                    args=(
                        index, self.address, amount.Wei, proof
                    ))
            )
            if gas_price:
                tx_params['gasPrice'] = Web3.to_wei(gas_price, 'gwei')

            tx_hash = await self.sign_and_send(tx_params)
            receipt = await self.wait_for_tx_receipt(
                tx_hash,
                self.web3
            )

            full_path = self.network.explorer + self.network.TxPath

            if receipt['status']:
                status = Status.CLAIMED
                message = f'Successfully claimed: '
            else:
                status = Status.ERROR
                message = f'Failed claim: {amount.Ether} ZK'

            message += (
                f' in {self.network.name.upper()}: '
                f'{full_path + tx_hash.hex()}'
            )

            self.logger.log_message(status=status, message=message)

            return receipt['status'], float(amount.Ether)

        except Exception as e:
            self.logger.log_message(
                Status.ERROR, f"{self.network.name.upper()} | Error while claiming: {e}")

            return False

    async def transfer(
        self,
    ) -> bool:
        try:
            contract = await self.get_contract(
                token=self.CLAIM_CONTRACTS[self.network.name]
            )
            gas_price = 0
            match self.network.name:
                case Networks.BSC.name:
                    gas_price = 1

            balance = await self.get_balance(
                token_contract=Web3.to_checksum_address(TOKEN_CONTRACT)
            )

            tx_params = TxParams(
                to=contract.address,
                data=contract.encodeABI(
                    'transfer',
                    args=(
                        Web3.to_checksum_address(self.receiver),
                        balance.Wei
                    ))
            )
            if gas_price:
                tx_params['gasPrice'] = Web3.to_wei(gas_price, 'gwei')

            tx_hash = await self.sign_and_send(tx_params)
            receipt = await self.wait_for_tx_receipt(
                tx_hash,
                self.web3
            )

            full_path = self.network.explorer + self.network.TxPath

            if receipt['status']:
                status = Status.CLAIMED
                message = f'Successfully sent {balance.Ether} ZK to {self.receiver}: '
            else:
                status = Status.ERROR
                message = f'Failed sending: {balance.Ether} ZK'

            message += (
                f' in {self.network.name.upper()}: '
                f'{full_path + tx_hash.hex()}'
            )

            self.logger.log_message(status=status, message=message)

            return receipt['status'], float(balance.Ether)

        except Exception as e:
            self.logger.log_message(
                Status.ERROR, f"{self.network.name.upper()} | Error while sending: {e}")

            return False
