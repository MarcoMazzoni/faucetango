from rest_framework import generics

from faucet.api.pagination import SmallSetPagination
from faucet.api.permissions import IsAdminUserOrReadOnly
from faucet.api.serializers import FundingTransactionSerializer
from faucet.api.throttles import ReceiverAddressBurstRateThrottle, UserIPBurstRateThrottle
from faucet.exceptions import EthTransactionFailedException
from faucet.ioc.blockchain_ioc import blockchain_service
from faucet.models import FundingTransaction, TransactionStatus


class FundingTransactionListCreateAPIView(generics.ListCreateAPIView):
    queryset = FundingTransaction.objects.all().order_by('-created_at')
    serializer_class = FundingTransactionSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = SmallSetPagination
    throttle_classes = [ReceiverAddressBurstRateThrottle, UserIPBurstRateThrottle]

    def perform_create(self, serializer: FundingTransactionSerializer):
        _AMOUNT = 10_000_000
        try:
            tx_hash = blockchain_service.transfer_funds_from_deposit_wallet(
                receiver_address=serializer.validated_data['receiver_address'],
                amount=_AMOUNT,
            )
            serializer.save(amount_wei=_AMOUNT,
                            sender_address=blockchain_service.deposit_wallet_account.address,
                            transaction_hash=tx_hash,
                            error_message='',
                            block_height=None)
        except EthTransactionFailedException as e:
            serializer.save(amount_wei=_AMOUNT,
                            sender_address=blockchain_service.deposit_wallet_account.address,
                            transaction_hash='',
                            status=TransactionStatus.FAILED,
                            block_height=None,
                            error_message=str(e))

