
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class FundingTransactionViewListTestCase(APITestCase):

    list_url = reverse('funding-transactions-list')

    def test_get_funding_transactions(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
