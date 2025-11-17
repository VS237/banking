from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Customer, BankAccounts
from django.core.validators import MinValueValidator
from .models import LoanApplication

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
    phone_number = forms.CharField(label="", max_length=15, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone Number'}))
    address = forms.CharField(label="", widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Address', 'rows':3}))
    city = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}))
    state = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}))
    date_of_birth = forms.DateField(label="", widget=forms.DateInput(attrs={'class':'form-control', 'placeholder':'Date of Birth (YYYY-MM-DD)', 'type':'date'}))
    ssn = forms.CharField(label="", max_length=11, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'SSN'}))
    id_number = forms.CharField(label="", max_length=20, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'ID Number'}))


    class Meta:
        model = Customer
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'address', 'state', 'city', 'date_of_birth', 'ssn', 'id_number')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class BankAccountForm(forms.ModelForm):
    ACCOUNT_TYPE_CHOICES = [
        ('Savings', 'Savings Account'),
        ('Checking', 'Checking Account'),
        ('Business', 'Business Account'),
        ('Fixed Deposit', 'Fixed Deposit Account'),
        ('Current', 'Current Account'),
    ]
    
    # Account type configuration with Cameroon-appropriate values (in XAF)
    ACCOUNT_DEFAULTS = {
        'Savings': {
            'interest_rate': 2.5,  # Higher interest rates common in Cameroon
            'daily_withdrawal_limit': 500000,  # ~$800 equivalent
            'daily_transfer_limit': 1000000    # ~$1600 equivalent
        },
        'Checking': {
            'interest_rate': 0.5,
            'daily_withdrawal_limit': 1000000,  # ~$1600 equivalent
            'daily_transfer_limit': 2000000     # ~$3200 equivalent
        },
        'Business': {
            'interest_rate': 1.2,
            'daily_withdrawal_limit': 3000000,  # ~$4800 equivalent
            'daily_transfer_limit': 5000000     # ~$8000 equivalent
        },
        'Fixed Deposit': {
            'interest_rate': 6.0,  # Higher fixed deposit rates in Cameroon
            'daily_withdrawal_limit': 0.00,  # No withdrawals for fixed deposits
            'daily_transfer_limit': 0.00     # No transfers for fixed deposits
        },
        'Current': {
            'interest_rate': 0.0,
            'daily_withdrawal_limit': 1500000,  # ~$2400 equivalent
            'daily_transfer_limit': 3000000     # ~$4800 equivalent
        }
    }
    
    # Override account_type to use choices
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={'onchange': 'updateAccountDefaults()'})
    )
    
    # Fixed initial balance - user can't modify it
    initial_balance = forms.DecimalField(
        max_digits=15,  # Increased for larger XAF amounts
        decimal_places=2, 
        required=False,
        initial=0.00,
        min_value=0.00,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control-plaintext',
            'style': 'background-color: #f8f9fa;'
        }),
        label="Solde Initial"
    )
    
    class Meta:
        model = BankAccounts
        fields = ['account_type', 'account_name', 'initial_balance', 
                 'interest_rate', 'daily_withdrawal_limit', 'daily_transfer_limit']
        widgets = {
            'account_name': forms.TextInput(attrs={'placeholder': 'ex: My Savings Account'}),
            'interest_rate': forms.NumberInput(attrs={
                'step': '0.001', 
                'min': '0.000', 
                'max': '100.000',
                'readonly': 'readonly',
                'class': 'form-control-plaintext',
                'style': 'background-color: #f8f9fa;'
            }),
            'daily_withdrawal_limit': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control-plaintext',
                'style': 'background-color: #f8f9fa;'
            }),
            'daily_transfer_limit': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control-plaintext',
                'style': 'background-color: #f8f9fa;'
            }),
        }
        labels = {
            'account_type': 'Account Type',
            'account_name': 'Account Name',
            'interest_rate': 'Interest Rate(%)',
            'daily_withdrawal_limit': 'Daily Withdrawal limit',
            'daily_transfer_limit': 'Daily Transfer limit',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial balance to 0 and make it readonly
        self.fields['initial_balance'].initial = 0.00
        
        # Set initial values based on default account type (Savings)
        account_type = self.initial.get('account_type', 'Savings')
        self.set_account_defaults(account_type)
    
    def set_account_defaults(self, account_type):
        """Set form field values based on account type"""
        defaults = self.ACCOUNT_DEFAULTS.get(account_type, self.ACCOUNT_DEFAULTS['Savings'])
        
        # Set the values for the fields
        self.fields['interest_rate'].initial = defaults['interest_rate']
        self.fields['daily_withdrawal_limit'].initial = defaults['daily_withdrawal_limit']
        self.fields['daily_transfer_limit'].initial = defaults['daily_transfer_limit']
        
        # Format numbers with XAF currency and Cameroonian formatting
        withdrawal_formatted = f"{defaults['daily_withdrawal_limit']:,.0f} XAF"
        transfer_formatted = f"{defaults['daily_transfer_limit']:,.0f} XAF"
        
        # Update widget attributes based on account type
        if account_type == 'Fixed Deposit':
            self.fields['daily_withdrawal_limit'].help_text = "Aucun retrait autorisé pour les comptes à terme fixe"
            self.fields['daily_transfer_limit'].help_text = "Aucun transfert autorisé pour les comptes à terme fixe"
        else:
            self.fields['daily_withdrawal_limit'].help_text = f"Maximum daily retrieval: {withdrawal_formatted}"
            self.fields['daily_transfer_limit'].help_text = f"Maximum daily transfer: {transfer_formatted}"
            
            # Add information about Cameroon banking regulations
            self.fields['interest_rate'].help_text = "Taux annuel conforme à la réglementation de la COBAC"
    
    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        
        # Ensure the initial balance is always 0
        cleaned_data['initial_balance'] = 0.00
        
        # Set the calculated values based on account type
        if account_type in self.ACCOUNT_DEFAULTS:
            defaults = self.ACCOUNT_DEFAULTS[account_type]
            cleaned_data['interest_rate'] = defaults['interest_rate']
            cleaned_data['daily_withdrawal_limit'] = defaults['daily_withdrawal_limit']
            cleaned_data['daily_transfer_limit'] = defaults['daily_transfer_limit']
        
        return cleaned_data


class LoanApplicationForm(forms.ModelForm):
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
    
    loan_type = forms.ChoiceField(
        choices=LOAN_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Loan Type'
    )
    
    loan_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(100)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter loan amount',
            'min': '100'
        }),
        label='Loan Amount ($)'
    )
    
    loan_term = forms.IntegerField(
        min_value=1,
        max_value=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Loan term in months',
            'min': '1',
            'max': '360'
        }),
        label='Loan Term (months)'
    )
    
    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Employment Status'
    )
    
    annual_income = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your annual income',
            'min': '0'
        }),
        label='Annual Income ($)'
    )
    
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please describe the purpose of this loan...'
        }),
        label='Loan Purpose'
    )
    
    class Meta:
        model = LoanApplication
        fields = [
            'loan_type', 
            'loan_amount', 
            'loan_term', 
            'employment_type',
            'annual_income', 
            'purpose'
        ]	
	
# forms.py
from django import forms

class MobileMoneyForm(forms.Form):
    phone_number = forms.CharField(
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter mobile number',
            'pattern': '[0-9]{10}',
            'maxlength': '10'
        }),
        label="Mobile Number"
    )
    
    secret_code = forms.CharField(
        max_length=6,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter secret code',
            'minlength': '4',
            'maxlength': '6'
        }),
        label="Secret Code"
    )    