from rest_framework import serializers

from faucet.models import FundingTransaction


class FundingTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FundingTransaction
        read_only_fields = [
            'transaction_hash',
            'sender_address',
            'amount_wei',
            'status',
            'block_height',
            'error_message',
            'created_at',
            'updated_at',
        ]
        fields = '__all__'
