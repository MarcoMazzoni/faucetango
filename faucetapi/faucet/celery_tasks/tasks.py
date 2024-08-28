
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from web3.exceptions import Web3RPCError

from faucet.ioc.blockchain_ioc import blockchain_service
from faucet.models import FundingTransaction, TransactionStatus

_POLL_LATENCY = 10.0
_TIMEOUT_FOR_RECEIPT = 50.0


@shared_task(bind=True, max_retries=10, default_retry_delay=60)  # retries 5 times, once every 60 seconds
def update_transaction_status(self, transaction_hash: str):
    try:
        receipt = blockchain_service.w3.eth.get_transaction_receipt(transaction_hash)
        if not receipt:
            print('Receipt not yet available, retrying...')
            self.retry(countdown=10)

        transaction = FundingTransaction.objects.filter(transaction_hash=transaction_hash).get()

        if receipt.status == 0:
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = 'Transaction failed'
            transaction.save()

        if receipt is None or receipt.blockNumber is None:
            # If receipt or blockNumber is None, retry the task
            raise self.retry(countdown=60)  # retry after 60 seconds

        # Update the transaction status based on the receipt
        if receipt.status == 1:
            transaction.status = TransactionStatus.CONFIRMED

        transaction.block_height = receipt['blockNumber']
        transaction.save()
    except MaxRetriesExceededError:
        # Handle the case where the max retries have been exceeded
        transaction = FundingTransaction.objects.filter(transaction_hash=transaction_hash).get()
        transaction.status = TransactionStatus.FAILED
        transaction.error_message = 'Transaction failed'
        transaction.save()
        print(f"Max retries exceeded for transaction {transaction_hash}. Marking as FAILED.")
    except Web3RPCError as e:
        if 'not found' in e.message:
            print('Receipt not yet available, retrying...')
            self.retry(countdown=10)
    except Exception as e:
        print(f"Error updating transaction {transaction_hash}: {e}")