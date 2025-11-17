from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import date

class Customer(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    ssn = models.CharField(max_length=11, blank=True)
    id_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.username
    
def generate_account_number():
    """Generate a unique account number"""
    return str(uuid.uuid4())[:20].replace('-', '').upper()

class BankAccounts(models.Model):
    
    ACCOUNT_STATUS = [
        ('ACTIVE', 'Active'),
        ('DORMANT', 'Dormant'),
        ('FROZEN', 'Frozen'),
        ('CLOSED', 'Closed'),
        ('PENDING', 'Pending Approval'),
        ('SUSPENDED', 'Suspended'),
    ]

    account_number = models.CharField(max_length=20, unique=True,  default=generate_account_number)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='bank_accounts')
    account_type = models.CharField(max_length=50, default='Savings')
    account_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=3, default=0.000, validators=[MinValueValidator(Decimal('0.000')), MaxValueValidator(Decimal('100.000'))])
    status = models.CharField(max_length=10, choices=ACCOUNT_STATUS, default='PENDING')        
    opened_date = models.DateField(auto_now_add=True)
    closed_date = models.DateField(null=True, blank=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    next_interest_calculation_date = models.DateField(null=True, blank=True)
    daily_withdrawal_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1000.00
    )
    daily_transfer_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=5000.00
    )

    def __str__(self):
        # Temporary fix - remove the problematic method call
        try:
            account_type_display = self.get_account_type_display()
        except AttributeError:
            account_type_display = "Unknown Account Type"
        
        return f"{account_type_display} - {self.account_number} - {self.customer.get_full_name()}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('fee', 'Fee'),
    ]
    
    account = models.ForeignKey(BankAccounts, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        ordering = ['-timestamp']    

# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanApplication(models.Model):
    LOAN_TYPES = [
        ('personal', 'Personal Loan'),
        ('mortgage', 'Mortgage Loan'),
        ('auto', 'Auto Loan'),
        ('business', 'Business Loan'),
        ('education', 'Education Loan'),
    ]
    
    EMPLOYMENT_TYPES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    loan_term = models.IntegerField(help_text='Loan term in months')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.username} - {self.loan_type} - ${self.loan_amount}"
    
    class Meta:
        ordering = ['-applied_date']        