import abc


class BlockchainService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def transfer_funds_from_deposit_wallet(self, receiver_address: str, amount: int) -> None:
        pass

    @abc.abstractmethod
    def get_account_balance(self, address: str) -> int:
        pass
