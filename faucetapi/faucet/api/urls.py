from django.urls import path, include

from faucet.api.views import FundingTransactionListCreateAPIView, FundingTransactionStatsAPIView

urlpatterns = [
    path('faucet/fund', FundingTransactionListCreateAPIView.as_view(), name='funding-transactions-list'),
    path('faucet/stats', FundingTransactionStatsAPIView.as_view(), name='funding-transactions-view'),
    path('prometheus-a3e86714-a105-48a0-ab03-f928903861ff/', include('django_prometheus.urls'))
]