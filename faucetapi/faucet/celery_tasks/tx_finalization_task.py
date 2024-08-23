
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from faucet.ioc.blockchain_ioc import blockchain_service
from faucet.models import FundingTransaction, TransactionStatus


@shared_task(bind=True, max_retries=5, default_retry_delay=60)  # retries 5 times, once every 60 seconds
def update_transaction_status(self, transaction_hash: str):
    try:
        receipt = blockchain_service.w3.eth.getTransactionReceipt(transaction_hash)
        transaction = FundingTransaction.objects.get(transaction_hash=transaction_hash)

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

        transaction.block_height = receipt.blockNumber
        transaction.save()
    except MaxRetriesExceededError:
        # Handle the case where the max retries have been exceeded
        transaction = FundingTransaction.objects.get(transaction_hash=transaction_hash)
        transaction.status = TransactionStatus.FAILED
        transaction.save()
        print(f"Max retries exceeded for transaction {transaction_hash}. Marking as FAILED.")
    except Exception as e:
        print(f"Error updating transaction {transaction_hash}: {e}")