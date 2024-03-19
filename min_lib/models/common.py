from decimal import Decimal


class TokenAmount:
    def __init__(
        self,
        amount: int | float | Decimal | str,
        decimals: int = 18,
        wei: bool = False,
        set_gwei: bool = False
    ) -> None:
        """
        Initialize the TokenAmount class.

        Args:
            amount (int | float | Decimal | str): The amount.
            decimals (int): The number of decimal places (default is 18).
            wei (bool): If True, the amount is in Wei; otherwise, it's in Ether (default is False).
            set_gwei (bool): If True, the GWei attribute will be calculated and set (default is False).

        """
        if wei:
            self.Wei: int = int(amount)
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

            if set_gwei:
                self.GWei: Decimal = int(amount / 10 ** 9)
        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

            if set_gwei:
                self.GWei: int = int(Decimal(str(amount)) * 10 ** 9)

        self.decimals = decimals

    def __str__(self) -> str:
        return f'{self.Wei}'


class Singleton(type):
    """A class that implements the singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(cls, *args, **kwargs)
        return cls._instances[cls]
