from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from VulnApp.models import Customer, Account, Transaction
from decimal import Decimal
from datetime import datetime

class Command(BaseCommand):
    help = 'Populate the database with dummy data for testing purposes'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Transaction.objects.all().delete()
        Account.objects.all().delete()
        Customer.objects.all().delete()
        User.objects.all().delete()

        # Create users and customers
        user1 = User.objects.create_user(username='John', password='password123', first_name='John', last_name='Doe')
        customer1 = Customer.objects.create(user=user1, phone_number='1234567890', address='123 Main St', date_of_birth='1999-01-01')

        user2 = User.objects.create_user(username='Jane', password='password234', first_name='Jane', last_name='Kim')
        customer2 = Customer.objects.create(user=user2, phone_number='0987654321', address='456 Manning Rd', date_of_birth='2000-02-02')

        user3 = User.objects.create_user(username='Attacker', password='attackerpassword', first_name='Attacker', last_name='User')
        customer3 = Customer.objects.create(user=user3, phone_number='0987612345', address='789 University Ave', date_of_birth='2001-03-03')

        # Create accounts for customers
        checking_account1 = Account.objects.create(customer=customer1, account_number='CHK123456', account_type='checking', balance=Decimal('5000.00'))
        savings_account1 = Account.objects.create(customer=customer1, account_number='SAV123456', account_type='savings', balance=Decimal('15000.00'))

        checking_account2 = Account.objects.create(customer=customer2, account_number='CHK654321', account_type='checking', balance=Decimal('3000.00'))
        savings_account2 = Account.objects.create(customer=customer2, account_number='SAV654321', account_type='savings', balance=Decimal('20000.00'))

        checking_account3 = Account.objects.create(customer=customer3, account_number='ATT12345', account_type='checking', balance=Decimal('100.00'))
        savings_account3 = Account.objects.create(customer=customer3, account_number='ATT54321', account_type='savings', balance=Decimal('30000.00'))

        # Create transactions for the accounts
        Transaction.objects.create(account=checking_account1, transaction_type='deposit', amount=Decimal('1000.00'), description='Initial deposit', timestamp=datetime.now())
        Transaction.objects.create(account=savings_account1, transaction_type='withdrawal', amount=Decimal('500.00'), description='ATM withdrawal', timestamp=datetime.now())
        Transaction.objects.create(account=checking_account2, transaction_type='deposit', amount=Decimal('1500.00'), description='Paycheck deposit', timestamp=datetime.now())
        Transaction.objects.create(account=savings_account2, transaction_type='transfer', amount=Decimal('2000.00'), description='Transfer to checking', timestamp=datetime.now())
        Transaction.objects.create(account=savings_account3, transaction_type='transfer', amount=Decimal('5000.00'), description='Transfer to checking', timestamp=datetime.now())

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with dummy data.'))