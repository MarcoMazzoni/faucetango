import typing
from eth_account.signers.local import LocalAccount
from eth_typing import HexStr
from web3 import HTTPProvider, Web3
from web3.exceptions import Web3RPCError
from retrying import retry

from faucet.exceptions import EthTransactionFailedException
from faucet.models import FundingTransaction
from faucet.service.blockchain_service import BlockchainService
from faucet.types import EthTxType


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
        self._deposit_wallet_account: LocalAccount = self._w3.eth.account.from_key(
            HexStr(self._deposit_wallet_private_key))
        self._chain_id = chain_id

    @property
    def deposit_wallet_account(self) -> LocalAccount:
        return self._deposit_wallet_account

    @property
    def w3(self) -> Web3:
        return self._w3

    def transfer_funds_from_deposit_wallet(self, receiver_address: str, amount: int,
                                           retry_number: typing.Optional[int] = None) -> EthTxType:
        try:
            print(f'RETRY NUMBER: {retry_number}')
            retry_number = 0 if not retry_number else retry_number
            return self._build_and_send_transaction(receiver_address, amount,
                                                    replace=True,
                                                    retry_number=retry_number)
        except Web3RPCError as e:
            if 'underpriced' in e.message or 'already known' in e.message \
                    or 'insufficient funds for gas' in e.message:
                print(e.message)
                retry_number = retry_number if retry_number is None else retry_number + 1
                return self.transfer_funds_from_deposit_wallet(receiver_address, amount,
                                                               retry_number=retry_number)
            raise EthTransactionFailedException(e.message)

    def get_account_balance(self, address: str) -> int:
        pass

    def _build_and_send_transaction(self, receiver_address: str, amount_value: int,
                                    replace: bool = False,
                                    retry_number: typing.Optional[int] = None) \
            -> EthTxType:
        last_nonce = self._w3.eth.get_transaction_count(self._deposit_wallet_account.address)
        next_nonce = last_nonce + retry_number if retry_number else last_nonce
        tx = self._build_transaction(receiver_address, amount_value, next_nonce, replace, retry_number)
        print(' ########## TRANSACTION  BUILT')
        signed = self._w3.eth.account.sign_transaction(tx, self._deposit_wallet_private_key)
        tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f'Retry number {retry_number}, hash {tx_hash.hex()}')
        return EthTxType(
            transaction_hash=tx_hash.hex(),
        )

    @classmethod
    def _get_last_transaction_of_account(cls, address: str) -> typing.Optional[FundingTransaction]:
        return FundingTransaction.objects.filter(receiver_address=address).order_by('-created_at').first()

    def _build_transaction(self, receiver_address: str, amount_value: int, next_nonce: int,
                           replace: bool = False, retry_number: typing.Optional[int] = None) -> dict:
        # 1. Build a new tx
        _MULTIPLICATION_FACTOR = 1 if not retry_number else retry_number + 0.5
        _BASE_GAS = 700_000
        max_priority = Web3.to_wei(20 * _MULTIPLICATION_FACTOR, 'gwei') if replace else Web3.to_wei(20, 'gwei')
        max_priority_fee_per_gas = Web3.to_wei(25 * _MULTIPLICATION_FACTOR, 'gwei') if replace else Web3.to_wei(25, 'gwei')
        gas = int(_BASE_GAS * _MULTIPLICATION_FACTOR) if replace else _BASE_GAS
        # gas_price = self._w3.eth.gas_price * 1.15 if replace else self._w3.eth.gas_price
        transaction = {
            'from': self._deposit_wallet_account.address,
            'to': receiver_address,
            'value': amount_value,
            #'nonce': self._w3.eth.get_transaction_count(self._deposit_wallet_account.address),
            'nonce': next_nonce,
            'gas': gas,
            # 'gasPrice': gas_price,
            'maxFeePerGas': max_priority_fee_per_gas,
            'maxPriorityFeePerGas': max_priority,
            'chainId': self._chain_id,
        }
        return transaction
