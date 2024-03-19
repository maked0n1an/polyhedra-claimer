from min_lib.models.networks import Network, Networks


class AccountInfo:
    def __init__(
        self,
        account_name: str | int,
        private_key: str,
        receiver_wallet: str,
        network: Network = Networks.Ethereum
    ) -> None:
        self.id = str(account_name)
        self.private_key = private_key
        self.receiver = receiver_wallet
        self.network = network