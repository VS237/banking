from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django import forms
import uuid
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import BankAccounts, Customer, Transaction
from .forms import BankAccountForm
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction





def home(request):
    context = {
        'hero_image': static('images/hero_2.jpg')
    }
    return render(request, 'banking/home.html', context)

@login_required(login_url='login')
def create_account(request):
    return render(request, 'banking/create_account.html')

@login_required
def manage_account(request):
    return render(request, 'banking/manage_account.html')

@login_required
def make_transaction(request):
    return render(request, 'banking/make_transaction.html')

@login_required
def make_request(request):
    return render(request, 'banking/make_request.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'banking/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('home')

def generate_account_number():
    """Generate a unique account number"""
    return str(uuid.uuid4())[:20].replace('-', '').upper()


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                # Authenticate and login the user
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Complete Your Registration by creating Your First Bank Account!')
                    return redirect('create_account')
                else:
                    messages.warning(request, 'Account created but automatic login failed. Please log in manually.')
                    return redirect('login')
                    
            except Exception as e:
                # Handle unexpected errors during user creation
                messages.error(request, f'An unexpected error occurred during registration: {str(e)}')
                return render(request, 'banking/register.html', {'form': form})
                
        else:
            # Detailed form error handling
            error_messages = []
            
            # Check for specific field errors
            if 'username' in form.errors:
                if 'already exists' in str(form.errors['username']).lower():
                    error_messages.append('Username already exists. Please choose a different one.')
                else:
                    error_messages.append('Invalid username. ' + str(form.errors['username']))
            
            if 'email' in form.errors:
                if 'already exists' in str(form.errors['email']).lower():
                    error_messages.append('Email address is already registered.')
                else:
                    error_messages.append('Invalid email address. ' + str(form.errors['email']))
            
            if 'password1' in form.errors:
                password_errors = str(form.errors['password1'])
                if 'too short' in password_errors.lower():
                    error_messages.append('Password is too short. Minimum length is 8 characters.')
                elif 'too common' in password_errors.lower():
                    error_messages.append('Password is too common. Please choose a stronger password.')
                elif 'numeric' in password_errors.lower():
                    error_messages.append('Password cannot be entirely numeric.')
                else:
                    error_messages.append('Password requirements not met. ' + password_errors)
            
            if 'password2' in form.errors:
                if 'match' in str(form.errors['password2']).lower():
                    error_messages.append('Passwords do not match.')
                else:
                    error_messages.append('Password confirmation error. ' + str(form.errors['password2']))
            
            # Add any other general errors
            for field, errors in form.errors.items():
                if field not in ['username', 'email', 'password1', 'password2']:
                    error_messages.append(f'{field}: {errors}')
            
            # If no specific errors were caught, show general message
            if not error_messages:
                error_messages.append('Please correct the errors below.')
            
            # Add all error messages
            for error_msg in error_messages:
                messages.error(request, error_msg)
            
            # Return the form with errors to display them
            return render(request, 'banking/register.html', {'form': form})
    
    else:        
        return render(request, 'banking/register.html', {'form': form})
    

@login_required
def create_bank_account(request):
    customer = request.user
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            try:
                # Create account without saving yet
                account = form.save(commit=False)
                
                account.customer = customer
                account.save()
                
                # Save the account
                account.save()
                
                messages.success(request, f'Account created successfully! Account Number: {account.account_number}')
                return redirect('account_list')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BankAccountForm()
    
    return render(request, 'banking/create_bank_account.html', {'form': form,
                                                                'customer': customer})

def create_account(request):
    customer = request.user
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            try:
                # Create account without saving yet
                account = form.save(commit=False)
                
                account.customer = customer
                account.save()
                
                # Save the account
                account.save()
                
                messages.success(request, f'Account created successfully! Account Number: {account.account_number}')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BankAccountForm()
    
    return render(request, 'banking/create_account.html', {'form': form,
                                                                'customer': customer})

@login_required
def account_list(request):
    """
    Display all bank accounts for the logged-in user in card format
    """
    # Get accounts for the current user's customer profile
    
    accounts = BankAccounts.objects.filter(customer=request.user).select_related('customer')
    
    context = {
        'accounts': accounts,
        'total_balance': sum(account.balance for account in accounts)
    }
    
    return render(request, 'banking/account_list.html', context)

@login_required
def modify_account(request, account_id):
    """
    View to modify an existing bank account
    """
    account = get_object_or_404(BankAccounts, id=account_id, customer=request.user)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account {account.account_number} updated successfully!')
            return redirect('account_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BankAccountForm(instance=account)
    
    context = {
        'form': form,
        'account': account,
        'title': 'Modify Account'
    }
    
    return render(request, 'banking/account_form.html', context)

@login_required
@require_POST
def delete_account(request, account_id):
    """
    View to delete a bank account (POST request only)
    """
    account = get_object_or_404(BankAccounts, id=account_id, customer=request.user)
    
    # Check if account has zero balance before deletion
    if account.balance != 0:
        messages.error(request, 'Cannot delete account with non-zero balance.')
        return redirect('account_list')
    
    account_number = account.account_number
    account.delete()
    
    messages.success(request, f'Account {account_number} deleted successfully!')
    return redirect('account_list')

@login_required
def delete_account_confirm(request, account_id):
    """
    Confirmation page for account deletion
    """
    account = get_object_or_404(BankAccounts, id=account_id, customer=request.user)
    
    context = {
        'account': account
    }
    
    return render(request, 'banking/account_confirm_delete.html', context)

# AJAX view for quick balance check
@login_required
def get_account_balance(request, account_id):
    """
    API endpoint to get account balance (for AJAX requests)
    """
    account = get_object_or_404(BankAccounts, id=account_id, customer=request.user)
    
    return JsonResponse({
        'account_number': account.account_number,
        'balance': float(account.balance),
        'available_balance': float(account.available_balance)
    })


@login_required
def transaction_view(request):
    customer = request.user
    accounts = BankAccounts.objects.filter(customer=customer)
    all_accounts = BankAccounts.objects.all()
    
    if request.method == 'POST':
        try:
            transaction_type = request.POST.get('transaction_type')
            account_id = request.POST.get('account')
            recipient_account_id = request.POST.get('recipient_account')
            amount = Decimal(request.POST.get('amount'))
            description = request.POST.get('description', '')
            
            # Get the account
            account = BankAccounts.objects.get(id=account_id, customer=customer)
            
            # Process transaction based on type
            if transaction_type == 'deposit':
                process_deposit(account, amount, description)
                messages.success(request, f'Successfully deposited {amount} XAF to your account.')
                
            elif transaction_type == 'withdraw':
                # Check sufficient funds including fee
                if account.balance >= amount + Decimal('2.50'):
                    process_withdrawal(account, amount, description)
                    messages.success(request, f'Successfully withdrew {amount} XAF. 250 XAF  fee applied.')
                else:
                    messages.error(request, 'Insufficient funds for withdrawal.')
                    return redirect('transaction')
                    
            elif transaction_type == 'transfer':
                recipient_account = BankAccounts.objects.get(id=recipient_account_id)
                # Check sufficient funds including fee
                if account.balance >= amount + Decimal('1.00'):
                    process_transfer(account, recipient_account, amount, description)
                    messages.success(request, f'Successfully transfered {amount} XAF to {recipient_account.account_number}. 100 XAF fee applied.')
                else:
                    messages.error(request, 'Insufficient funds for transfer.')
                    return redirect('transaction')
            
            return redirect('account_list')
            
        except BankAccounts.DoesNotExist:
            messages.error(request, 'Account not found.')
        except Exception as e:
            messages.error(request, f'Transaction failed: {str(e)}')
    
    return render(request, 'banking/transaction_form.html', {
        'accounts': accounts,
        'all_accounts': all_accounts
    })

def process_deposit(account, amount, description):
    """Process a deposit transaction"""
    with transaction.atomic():
        account.balance += amount
        account.save()
        
        Transaction.objects.create(
            account=account,
            transaction_type='deposit',
            amount=amount,
            description=description or f'Deposit to {account.account_number}',
            status='completed',
            balance_after=account.balance
        )

def process_withdrawal(account, amount, description):
    """Process a withdrawal transaction with fee"""
    with transaction.atomic():
        # Deduct amount and fee
        total_deduction = amount + Decimal('250')
        account.balance -= total_deduction
        account.save()
        
        # Create withdrawal transaction
        Transaction.objects.create(
            account=account,
            transaction_type='withdrawal',
            amount=amount,
            description=description or f'Withdrawal from {account.account_number}',
            status='completed',
            balance_after=account.balance
        )
        
        # Create fee transaction
        Transaction.objects.create(
            account=account,
            transaction_type='fee',
            amount=Decimal('2.50'),
            description='ATM withdrawal fee',
            status='completed',
            balance_after=account.balance
        )

def process_transfer(sender_account, recipient_account, amount, description):
    """Process a transfer between accounts with fee"""
    with transaction.atomic():
        # Deduct amount and fee from sender
        total_deduction = amount + Decimal('200')
        sender_account.balance -= total_deduction
        sender_account.save()
        
        # Add amount to recipient
        recipient_account.balance += amount
        recipient_account.save()
        
        # Create transfer-out transaction for sender
        Transaction.objects.create(
            account=sender_account,
            transaction_type='transfer_out',
            amount=amount,
            description=description or f'Transfer to {recipient_account.account_number}',
            status='completed',
            balance_after=sender_account.balance
        )
        
        # Create fee transaction for sender
        Transaction.objects.create(
            account=sender_account,
            transaction_type='fee',
            amount=Decimal('1.00'),
            description='Transfer fee',
            status='completed',
            balance_after=sender_account.balance
        )
        
        # Create transfer-in transaction for recipient
        Transaction.objects.create(
            account=recipient_account,
            transaction_type='transfer_in',
            amount=amount,
            description=f'Transfer from {sender_account.account_number}',
            status='completed',
            balance_after=recipient_account.balance
        )

# chatbot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .services import OpenRouterService
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def chat_api(request):
    """
    API endpoint for chatbot requests
    """
    logger.info(f"Received chat request: {request.body}")

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get response from chatbot
        response = OpenRouterService.get_chat_response(user_message, conversation_history)
        
        return JsonResponse({
            'response': response,
            'success': True
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def chat_view(request):
    """
    Render the chat interface
    """
    return render(request, 'banking/chat.html')        

# views.py
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

# Your banking-specific training data
BANKING_CONTEXT = """
You are a helpful banking assistant for a financial institution. You can help customers with:

1. Account balances and transactions
2. Transferring funds between accounts
3. Bill payments and scheduling
4. Card services (blocking cards, reporting loss)
5. Loan applications and information
6. Interest rates and fees
7. Branch and ATM locations
8. Online banking support
9. Security and fraud prevention

Always be polite, professional, and ensure you protect customer privacy. 
Never ask for or store full account numbers, passwords, or PINs.

If you don't know the answer to a question, direct the customer to call our 
24/7 support line at 1-800-BANK-HELP.
"""

@csrf_exempt
@require_POST
def chat_handler(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Prepare the prompt with banking context
        prompt = f"{BANKING_CONTEXT}\n\nCustomer: {user_message}\nAssistant:"
        
        # Call Deepseek via OpenRouter
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek/deepseek-chat-v3.1",  # Check for the latest model name
            "messages": [
                {"role": "system", "content": "You are a helpful banking assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response_data = response.json()
        
        if response.status_code == 200:
            bot_response = response_data['choices'][0]['message']['content']
            return JsonResponse({'response': bot_response})
        else:
            return JsonResponse({'error': 'Failed to get response from AI'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required    
def choose_transaction_type(request):
    return render(request, 'banking/choose_transaction_type.html')    

@login_required
def loans_view(request):
    return render(request, 'banking/loans.html')

@login_required
def mobile_money_view(request):
    return render(request, 'banking/mobile_money.html')# models.py