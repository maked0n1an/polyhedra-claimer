import aiohttp

from web3 import Web3
from web3.types import TxParams
from eth_account.messages import encode_defunct
from eth_utils import to_hex

from input_data.settings import (
    AUTH_MESSAGE,
    ETH_CLAIM_ADDRESS,
    BSC_CLAIM_ADDRESS
)
from min_lib.models.accounts import Account
from min_lib.models.common import TokenAmount
from min_lib.models.constant_models import Status
from min_lib.models.networks import Networks
from min_lib.utils.helpers import retry


class Claimer(Account):
    CLAIM_CONTRACT = {
        Networks.BSC: BSC_CLAIM_ADDRESS,
        Networks.Ethereum: ETH_CLAIM_ADDRESS
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
                set_gwei=True
            )
            return int(data['index']), amount, data['proof']

        except Exception as e:
            self.logger.log_message(
                status=Status.ERROR,
                message=f"An error occurred: {e}"
            )
            return

    async def _check_eligible(self) -> bool:
        try:
            data = await self._send_request(
                method='GET',
                url='https://api-ribbon.vercel.app/api/aevo/check-eligibility',
                params={
                    'address': self.address
                }
            )

            return data['airdrop']
        except Exception as e:
            self.logger.log_message(
                status=Status.ERROR,
                message=f"An error while checking for eligibility: {e}"
            )
            return False

    @retry
    async def claim(
        self
    ) -> bool:
        match self.network.name:
            case Networks.BSC.name:
                gas_price = 1.5
            case Networks.Ethereum.name:
                gas_price = 0.1

        contract = await self.get_contract(
            token=self.CLAIM_CONTRACT
        )

        index, amount, proof = await self._get_proof()
        if not amount:
            return False

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                'claim',
                args=(
                    index, self.address, amount, proof
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
            f' from {self.network.name.upper()}: '
            f'{full_path + tx_hash.hex()}'
        )

        self.logger.log_message(status=status, message=message)
        
        return receipt['status']
