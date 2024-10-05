# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()

    def __str__(self):
        return f'{self.user.username} - {self.user.first_name} {self.user.last_name}'

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('credit', 'Credit Account'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=12, unique=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.account_number} ({self.account_type}) - {self.customer.user.username}'

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type.capitalize()} of ${self.amount} on {self.account.account_number}'
    