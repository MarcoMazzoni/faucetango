from django.db import models

# Create your models here.


class TransactionStatus(models.TextChoices):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    FAILED = 'failed'


class FundingTransaction(models.Model):
    transaction_hash = models.CharField(max_length=66, blank=True, null=True)
    sender_address = models.CharField(max_length=42)
    receiver_address = models.CharField(max_length=42)
    # I am using DecimalField with 99 digits because PositiveBigIntegerField is too small (MAX 2**64-1)
    amount_wei = models.DecimalField(max_digits=99, decimal_places=0)
    status = models.CharField(max_length=10, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    block_height = models.PositiveBigIntegerField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_hash
