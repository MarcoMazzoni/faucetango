from django.urls import path

from faucet.api.views import FundingTransactionListCreateAPIView

urlpatterns = [
    path('faucet/fund', FundingTransactionListCreateAPIView.as_view(), name='funding-transactions-list'),
]