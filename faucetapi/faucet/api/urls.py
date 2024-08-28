from django.urls import path

from faucet.api.views import FundingTransactionListCreateAPIView, FundingTransactionStatsAPIView

urlpatterns = [
    path('faucet/fund', FundingTransactionListCreateAPIView.as_view(), name='funding-transactions-list'),
    path('faucet/stats', FundingTransactionStatsAPIView.as_view(), name='funding-transactions-view')
]