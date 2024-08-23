from django.contrib import admin

# Register your models here.
from faucet.models import FundingTransaction

admin.site.register(FundingTransaction)
