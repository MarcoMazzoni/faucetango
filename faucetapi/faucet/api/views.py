import datetime

from django.db import transaction
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from web3 import Web3

from faucet.api.pagination import SmallSetPagination
from faucet.api.permissions import IsAdminUserOrReadOnly
from faucet.api.serializers import FundingTransactionSerializer
from faucet.api.throttles import ReceiverAddressBurstRateThrottle, UserIPBurstRateThrottle
from faucet.celery_tasks.tasks import update_transaction_status
from faucet.exceptions import EthTransactionFailedException
from faucet.ioc.blockchain_ioc import blockchain_service
from faucet.models import FundingTransaction, TransactionStatus


class FundingTransactionListCreateAPIView(ListCreateAPIView):
    queryset = FundingTransaction.objects.all().order_by('-created_at')
    serializer_class = FundingTransactionSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = SmallSetPagination
    throttle_classes = [ReceiverAddressBurstRateThrottle, UserIPBurstRateThrottle]

    def get_throttles(self):
        if self.request.method == 'GET':
            return []
        return super().get_throttles()

    def perform_create(self, serializer: FundingTransactionSerializer):
        _AMOUNT = Web3.to_wei(0.001, 'ether')
        try:
            eth_tx = blockchain_service.transfer_funds_from_deposit_wallet(
                receiver_address=serializer.validated_data['receiver_address'],
                amount=_AMOUNT,
            )
            #update_transaction_status.delay(tx_hash)
            transaction.on_commit(lambda: update_transaction_status.delay(eth_tx.transaction_hash))
            serializer.save(amount_wei=_AMOUNT,
                            sender_address=blockchain_service.deposit_wallet_account.address,
                            transaction_hash=eth_tx.transaction_hash,
                            error_message='',
                            block_height=None)
        except EthTransactionFailedException as e:
            serializer.save(amount_wei=_AMOUNT,
                            sender_address=blockchain_service.deposit_wallet_account.address,
                            transaction_hash='',
                            status=TransactionStatus.FAILED,
                            block_height=None,
                            error_message=str(e))


class FundingTransactionStatsAPIView(APIView):
    permission_classes = [IsAdminUserOrReadOnly]
    renderer_classes = [JSONRenderer]

    def get(self, request) -> Response:
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        failed_transactions_count = FundingTransaction.objects\
            .filter(status=TransactionStatus.FAILED, created_at__gt=date_from)\
            .count()
        successful_transactions_count = FundingTransaction.objects\
            .filter(created_at__gt=date_from)\
            .exclude(status=TransactionStatus.FAILED)\
            .count()

        return Response(
            {
                'failed_transactions_24h': failed_transactions_count,
                'successful_transactions_24h': successful_transactions_count,
            },
            status=status.HTTP_200_OK
        )


