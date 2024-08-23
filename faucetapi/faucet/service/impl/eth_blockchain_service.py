import json

from eth_account.signers.local import LocalAccount
from web3 import HTTPProvider, Web3
from web3.exceptions import Web3RPCError

from faucet.exceptions import EthTransactionFailedException
from faucet.service.blockchain_service import BlockchainService


class ETHBlockchainService(BlockchainService):
    def __init__(self,
                 deposit_wallet_private_key: str,
                 ethereum_node_url: str,
                 provider_timeout: int = 15,
                 chain_id: int = 1337):
        self._w3_provider = HTTPProvider(
            ethereum_node_url,
            request_kwargs={"timeout": provider_timeout},
        )
        self._w3: Web3 = Web3(self._w3_provider)
        self._deposit_wallet_private_key = deposit_wallet_private_key
        self._deposit_wallet_account: LocalAccount = self._w3.eth.account.from_key(self._deposit_wallet_private_key)
        self._chain_id = chain_id

    @property
    def deposit_wallet_account(self) -> LocalAccount:
        return self._deposit_wallet_account

    @property
    def w3(self) -> Web3:
        return self._w3

    def transfer_funds_from_deposit_wallet(self, receiver_address: str, amount: int) -> str:
        try:
            tx = self._build_transaction(receiver_address, amount)
            signed = self._w3.eth.account.sign_transaction(tx, self._deposit_wallet_private_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            tx = self._w3.eth.get_transaction(tx_hash)
            return tx_hash.hex()
        except Web3RPCError as e:
            raise EthTransactionFailedException(e.message)

    def get_account_balance(self, address: str) -> int:
        pass

    def _build_transaction(self, receiver_address: str, amount_value: int) -> dict:
        # 1. Build a new tx
        transaction = {
            'from': self._deposit_wallet_account.address,
            'to': receiver_address,
            'value': amount_value,
            'nonce': self._w3.eth.get_transaction_count(self._deposit_wallet_account.address),
            'gas': 2000000,
            'maxFeePerGas': 90000000,
            'maxPriorityFeePerGas': 1000000000,
            'chainId': self._chain_id
        }
        return transaction
