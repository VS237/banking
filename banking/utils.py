# banking_data_utils.py
from django.contrib.auth.models import User
from django.db import transaction
from .models import (
    CustomerProfile, Account, Transaction, Loan, 
    Branch, EmployeeProfile
)
import random
from decimal import Decimal
from datetime import date, timedelta
import uuid

class BankingDataInserter:
    """Main class for inserting banking data into the system"""
    
    def __init__(self):
        self.regions = [code for code, _ in CustomerProfile.REGIONS]
        self.cities = [code for code, _ in CustomerProfile.CITIES]
        self.account_types = [code for code, _ in Account.ACCOUNT_TYPES]
        self.loan_types = [code for code, _ in Loan.LOAN_TYPES]
    
    @transaction.atomic
    def create_customer(self, user_data, profile_data):
        """
        Create a new customer with user and profile
        
        Args:
            user_data (dict): Data for User model
            profile_data (dict): Data for CustomerProfile model
            
        Returns:
            CustomerProfile: Created customer profile
        """
        try:
            # Create User
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            
            # Create CustomerProfile
            customer = CustomerProfile.objects.create(
                user=user,
                date_of_birth=profile_data['date_of_birth'],
                gender=profile_data['gender'],
                national_id=profile_data['national_id'],
                phone=profile_data['phone'],
                region=profile_data['region'],
                city=profile_data['city'],
                address_line=profile_data['address_line'],
                employment_status=profile_data['employment_status'],
                next_of_kin_name=profile_data.get('next_of_kin_name', ''),
                next_of_kin_relationship=profile_data.get('next_of_kin_relationship', 'OTHER'),
                next_of_kin_phone=profile_data.get('next_of_kin_phone', ''),
                **{k: v for k, v in profile_data.items() 
                   if k not in ['date_of_birth', 'gender', 'national_id', 'phone', 
                              'region', 'city', 'address_line', 'employment_status',
                              'next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_phone']}
            )
            
            return customer
            
        except Exception as e:
            raise Exception(f"Error creating customer: {str(e)}")
    
    @transaction.atomic
    def create_account(self, customer_id, account_data, approved_by=None):
        """
        Create a new bank account for a customer
        
        Args:
            customer_id (int): ID of the customer
            account_data (dict): Account data
            approved_by (User): User who approved the account (optional)
            
        Returns:
            Account: Created account
        """
        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            
            account = Account.objects.create(
                customer=customer,
                account_type=account_data['account_type'],
                balance=account_data.get('balance', Decimal('0.00')),
                interest_rate=account_data.get('interest_rate', Decimal('0.000')),
                is_overdraft_allowed=account_data.get('is_overdraft_allowed', False),
                overdraft_limit=account_data.get('overdraft_limit', Decimal('0.00')),
                has_checkbook=account_data.get('has_checkbook', False),
                has_debit_card=account_data.get('has_debit_card', False),
                approved_by=approved_by,
                **{k: v for k, v in account_data.items() 
                   if k not in ['account_type', 'balance', 'interest_rate', 
                              'is_overdraft_allowed', 'overdraft_limit',
                              'has_checkbook', 'has_debit_card']}
            )
            
            # Generate account number if not provided
            if not account_data.get('account_number'):
                account.generate_account_number()
                account.save()
            
            return account
            
        except CustomerProfile.DoesNotExist:
            raise Exception("Customer does not exist")
        except Exception as e:
            raise Exception(f"Error creating account: {str(e)}")
    
    @transaction.atomic
    def create_transaction(self, account_id, transaction_data, performed_by=None):
        """
        Create a new transaction
        
        Args:
            account_id (int): ID of the account
            transaction_data (dict): Transaction data
            performed_by (User): User who performed the transaction
            
        Returns:
            Transaction: Created transaction
        """
        try:
            account = Account.objects.get(id=account_id)
            
            transaction = Transaction.objects.create(
                account=account,
                transaction_type=transaction_data['transaction_type'],
                amount=transaction_data['amount'],
                description=transaction_data.get('description', ''),
                status=transaction_data.get('status', 'PENDING'),
                performed_by=performed_by,
                **{k: v for k, v in transaction_data.items() 
                   if k not in ['transaction_type', 'amount', 'description', 'status']}
            )
            
            # Update account balance if transaction is completed
            if transaction.status == 'COMPLETED':
                if transaction.transaction_type in ['DEPOSIT', 'INTEREST', 'REFUND']:
                    account.balance += transaction.amount
                elif transaction.transaction_type in ['WITHDRAWAL', 'FEE', 'PAYMENT']:
                    account.balance -= transaction.amount
                account.save()
            
            return transaction
            
        except Account.DoesNotExist:
            raise Exception("Account does not exist")
        except Exception as e:
            raise Exception(f"Error creating transaction: {str(e)}")
    
    @transaction.atomic
    def create_loan(self, customer_id, loan_data, approved_by=None):
        """
        Create a new loan application
        
        Args:
            customer_id (int): ID of the customer
            loan_data (dict): Loan data
            approved_by (User): User who approved the loan (optional)
            
        Returns:
            Loan: Created loan
        """
        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            
            loan = Loan.objects.create(
                customer=customer,
                loan_type=loan_data['loan_type'],
                loan_amount=loan_data['loan_amount'],
                interest_rate=loan_data['interest_rate'],
                term_months=loan_data['term_months'],
                purpose=loan_data.get('purpose', ''),
                approved_by=approved_by,
                **{k: v for k, v in loan_data.items() 
                   if k not in ['loan_type', 'loan_amount', 'interest_rate', 
                              'term_months', 'purpose']}
            )
            
            return loan
            
        except CustomerProfile.DoesNotExist:
            raise Exception("Customer does not exist")
        except Exception as e:
            raise Exception(f"Error creating loan: {str(e)}")
    
    @transaction.atomic
    def create_branch(self, branch_data, manager=None):
        """
        Create a new bank branch
        
        Args:
            branch_data (dict): Branch data
            manager (User): Branch manager (optional)
            
        Returns:
            Branch: Created branch
        """
        try:
            branch = Branch.objects.create(
                branch_code=branch_data['branch_code'],
                name=branch_data['name'],
                region=branch_data['region'],
                city=branch_data['city'],
                address=branch_data['address'],
                phone=branch_data['phone'],
                manager=manager,
                **{k: v for k, v in branch_data.items() 
                   if k not in ['branch_code', 'name', 'region', 'city', 
                              'address', 'phone']}
            )
            
            return branch
            
        except Exception as e:
            raise Exception(f"Error creating branch: {str(e)}")
    
    @transaction.atomic
    def create_employee(self, user_data, employee_data, branch_id):
        """
        Create a new bank employee
        
        Args:
            user_data (dict): Data for User model
            employee_data (dict): Data for EmployeeProfile model
            branch_id (int): ID of the branch
            
        Returns:
            EmployeeProfile: Created employee profile
        """
        try:
            branch = Branch.objects.get(id=branch_id)
            
            # Create User
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            
            # Create EmployeeProfile
            employee = EmployeeProfile.objects.create(
                user=user,
                employee_id=employee_data['employee_id'],
                role=employee_data['role'],
                branch=branch,
                hire_date=employee_data['hire_date'],
                salary=employee_data['salary'],
                work_phone=employee_data.get('work_phone', ''),
                work_email=employee_data.get('work_email', user_data['email']),
                national_id=employee_data['national_id'],
                **{k: v for k, v in employee_data.items() 
                   if k not in ['employee_id', 'role', 'hire_date', 'salary',
                              'work_phone', 'work_email', 'national_id']}
            )
            
            return employee
            
        except Branch.DoesNotExist:
            raise Exception("Branch does not exist")
        except Exception as e:
            raise Exception(f"Error creating employee: {str(e)}")


class BankingDataGenerator:
    """Class to generate sample banking data for testing"""
    
    def __init__(self):
        self.first_names = ['Jean', 'Marie', 'Paul', 'François', 'Joseph', 'Pierre', 
                           'Marc', 'André', 'Philippe', 'Jacques', 'Michel', 'Louis',
                           'David', 'Daniel', 'Thomas', 'Serge', 'Alain', 'Patrick',
                           'Emmanuel', 'Bernard']
        self.last_names = ['Ngassa', 'Tchoutou', 'Ngo', 'Mbappe', 'Fotso', 'Nana',
                          'Kamga', 'Ndjock', 'Mballa', 'Tchakounte', 'Nguegang',
                          'Ndjami', 'Tchinda', 'Nguemo', 'Ngom', 'Mbarga', 'Ndong',
                          'Essomba', 'Mvondo', 'Zanga']
        self.cities = [code for code, _ in CustomerProfile.CITIES]
        self.regions = [code for code, _ in CustomerProfile.REGIONS]
    
    def generate_national_id(self):
        """Generate a random Cameroon National ID number"""
        return str(random.randint(1000000000, 9999999999))
    
    def generate_phone_number(self):
        """Generate a random Cameroon phone number"""
        prefixes = ['2376', '2377', '2378', '2379']
        prefix = random.choice(prefixes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{number}"
    
    def generate_customer_data(self, index):
        """Generate sample customer data"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        username = f"{first_name.lower()}.{last_name.lower()}{index}"
        email = f"{username}@example.com"
        
        # Generate a random birth date (18-80 years old)
        start_date = date.today() - timedelta(days=80*365)
        end_date = date.today() - timedelta(days=18*365)
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        return {
            'user_data': {
                'username': username,
                'email': email,
                'password': 'password123',
                'first_name': first_name,
                'last_name': last_name
            },
            'profile_data': {
                'date_of_birth': random_date,
                'gender': random.choice(['M', 'F']),
                'national_id': self.generate_national_id(),
                'phone': self.generate_phone_number(),
                'region': random.choice(self.regions),
                'city': random.choice(self.cities),
                'address_line': f"Rue {random.randint(1, 100)}, Quartier {random.choice(['Central', 'Commercial', 'Résidentiel'])}",
                'employment_status': random.choice(['EMPLOYED', 'SELF_EMPLOYED', 'STUDENT', 'UNEMPLOYED']),
                'marital_status': random.choice(['SINGLE', 'MARRIED', 'DIVORCED']),
                'monthly_income': Decimal(random.randint(50000, 500000)),
                'next_of_kin_name': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                'next_of_kin_relationship': random.choice(['PARENT', 'SIBLING', 'SPOUSE']),
                'next_of_kin_phone': self.generate_phone_number(),
                'next_of_kin_address': f"Rue {random.randint(1, 100)}, {random.choice(self.cities)}"
            }
        }
    
    def generate_account_data(self, customer):
        """Generate sample account data"""
        return {
            'account_type': random.choice([code for code, _ in Account.ACCOUNT_TYPES]),
            'balance': Decimal(random.randint(10000, 1000000)),
            'interest_rate': Decimal(random.uniform(0.5, 5.0)),
            'is_overdraft_allowed': random.choice([True, False]),
            'overdraft_limit': Decimal(random.randint(0, 100000)) if random.choice([True, False]) else Decimal('0.00'),
            'has_checkbook': random.choice([True, False]),
            'has_debit_card': random.choice([True, False]),
            'account_name': f"Compte {random.choice(['Principal', 'Épargne', 'Courant'])}"
        }
    
    def generate_transaction_data(self, account):
        """Generate sample transaction data"""
        transaction_types = [code for code, _ in Transaction.TRANSACTION_TYPES]
        return {
            'transaction_type': random.choice(transaction_types),
            'amount': Decimal(random.randint(1000, 200000)),
            'description': f"Transaction {random.choice(['mensuelle', 'ponctuelle', 'de transfert'])}",
            'status': random.choice(['COMPLETED', 'PENDING']),
            'mobile_money_provider': random.choice(['MTN', 'ORANGE', '']) if random.random() > 0.7 else '',
            'mobile_money_number': self.generate_phone_number() if random.random() > 0.7 else ''
        }
    
    def generate_loan_data(self, customer):
        """Generate sample loan data"""
        return {
            'loan_type': random.choice([code for code, _ in Loan.LOAN_TYPES]),
            'loan_amount': Decimal(random.randint(500000, 5000000)),
            'interest_rate': Decimal(random.uniform(5.0, 15.0)),
            'term_months': random.choice([12, 24, 36, 48, 60]),
            'purpose': f"Prêt pour {random.choice(['éducation', 'business', 'immobilier', 'véhicule', 'projet personnel'])}",
            'collateral_description': random.choice(['Titre foncier', 'Véhicule', 'Garantie personnelle', '']),
            'collateral_value': Decimal(random.randint(1000000, 10000000)) if random.random() > 0.5 else None,
            'guarantor_name': f"{random.choice(self.first_names)} {random.choice(self.last_names)}" if random.random() > 0.5 else '',
            'guarantor_phone': self.generate_phone_number() if random.random() > 0.5 else ''
        }
    
    def generate_branch_data(self, index):
        """Generate sample branch data"""
        city = random.choice(self.cities)
        return {
            'branch_code': f"BR{index:03d}",
            'name': f"Agence {city}",
            'region': random.choice(self.regions),
            'city': city,
            'address': f"Avenue {random.choice(['Kennedy', 'De Gaulle', 'Ahidjo'])}, {city}",
            'phone': self.generate_phone_number(),
            'email': f"agence.{city.lower()}@banque.cm",
            'opening_time': '08:00:00',
            'closing_time': '16:00:00',
            'working_days': 'Monday-Friday',
            'saturday_hours': '09:00-13:00',
            'has_atm': random.choice([True, False]),
            'has_safe_deposit': random.choice([True, False])
        }
    
    def generate_employee_data(self, index, branch):
        """Generate sample employee data"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        username = f"emp.{first_name.lower()}.{last_name.lower()}{index}"
        email = f"{username}@banque.cm"
        
        return {
            'user_data': {
                'username': username,
                'email': email,
                'password': 'password123',
                'first_name': first_name,
                'last_name': last_name
            },
            'employee_data': {
                'employee_id': f"EMP{index:04d}",
                'role': random.choice(['TELLER', 'LOAN_OFFICER', 'CUSTOMER_SERVICE', 'OPERATIONS']),
                'hire_date': date.today() - timedelta(days=random.randint(100, 2000)),
                'salary': Decimal(random.randint(150000, 800000)),
                'work_phone': self.generate_phone_number(),
                'work_email': email,
                'national_id': self.generate_national_id()
            }
        }


# Utility functions for common operations
def create_deposit(account_id, amount, description="", performed_by=None):
    """Helper function to create a deposit transaction"""
    inserter = BankingDataInserter()
    return inserter.create_transaction(
        account_id,
        {
            'transaction_type': 'DEPOSIT',
            'amount': amount,
            'description': description,
            'status': 'COMPLETED'
        },
        performed_by
    )

def create_withdrawal(account_id, amount, description="", performed_by=None):
    """Helper function to create a withdrawal transaction"""
    inserter = BankingDataInserter()
    return inserter.create_transaction(
        account_id,
        {
            'transaction_type': 'WITHDRAWAL',
            'amount': amount,
            'description': description,
            'status': 'COMPLETED'
        },
        performed_by
    )

def create_transfer(from_account_id, to_account_id, amount, description="", performed_by=None):
    """Helper function to create a transfer between accounts"""
    inserter = BankingDataInserter()
    
    # Create withdrawal from source account
    withdrawal = inserter.create_transaction(
        from_account_id,
        {
            'transaction_type': 'TRANSFER',
            'amount': amount,
            'description': f"Transfer to account {to_account_id}: {description}",
            'status': 'COMPLETED',
            'related_account_id': to_account_id
        },
        performed_by
    )
    
    # Create deposit to target account
    deposit = inserter.create_transaction(
        to_account_id,
        {
            'transaction_type': 'TRANSFER',
            'amount': amount,
            'description': f"Transfer from account {from_account_id}: {description}",
            'status': 'COMPLETED',
            'related_account_id': from_account_id
        },
        performed_by
    )
    
    return withdrawal, deposit

def approve_loan(loan_id, approved_by):
    """Helper function to approve a loan"""
    try:
        loan = Loan.objects.get(id=loan_id)
        loan.status = 'APPROVED'
        loan.approved_by = approved_by
        loan.approval_date = date.today()
        
        # Calculate monthly payment (simple interest)
        monthly_rate = loan.interest_rate / 100 / 12
        loan.monthly_payment = (loan.loan_amount * monthly_rate * 
                              (1 + monthly_rate) ** loan.term_months) / \
                             ((1 + monthly_rate) ** loan.term_months - 1)
        
        loan.remaining_balance = loan.loan_amount
        loan.save()
        
        return loan
        
    except Loan.DoesNotExist:
        raise Exception("Loan does not exist")

def generate_sample_data(num_customers=10, num_employees=3, num_branches=2):
    """Generate sample banking data for testing"""
    generator = BankingDataGenerator()
    inserter = BankingDataInserter()
    
    # Create branches
    branches = []
    for i in range(1, num_branches + 1):
        branch_data = generator.generate_branch_data(i)
        branch = inserter.create_branch(branch_data)
        branches.append(branch)
    
    # Create employees
    employees = []
    for i in range(1, num_employees + 1):
        employee_data = generator.generate_employee_data(i, random.choice(branches))
        employee = inserter.create_employee(
            employee_data['user_data'],
            employee_data['employee_data'],
            random.choice(branches).id
        )
        employees.append(employee)
    
    # Create customers and accounts
    customers = []
    accounts = []
    for i in range(1, num_customers + 1):
        customer_data = generator.generate_customer_data(i)
        customer = inserter.create_customer(
            customer_data['user_data'],
            customer_data['profile_data']
        )
        customers.append(customer)
        
        # Create 1-3 accounts per customer
        num_accounts = random.randint(1, 3)
        for _ in range(num_accounts):
            account_data = generator.generate_account_data(customer)
            account = inserter.create_account(
                customer.id,
                account_data,
                random.choice(employees).user if employees else None
            )
            accounts.append(account)
            
            # Create some transactions
            num_transactions = random.randint(3, 10)
            for _ in range(num_transactions):
                transaction_data = generator.generate_transaction_data(account)
                inserter.create_transaction(
                    account.id,
                    transaction_data,
                    random.choice(employees).user if employees else None
                )
        
        # Create loans for some customers
        if random.random() > 0.7:  # 30% chance
            loan_data = generator.generate_loan_data(customer)
            loan = inserter.create_loan(
                customer.id,
                loan_data,
                random.choice([e for e in employees if e.role == 'LOAN_OFFICER']).user 
                if any(e.role == 'LOAN_OFFICER' for e in employees) else None
            )
            
            # Approve some loans
            if random.random() > 0.5 and any(e.role == 'LOAN_OFFICER' for e in employees):
                approve_loan(loan.id, random.choice([e for e in employees if e.role == 'LOAN_OFFICER']).user)
    
    return {
        'branches': branches,
        'employees': employees,
        'customers': customers,
        'accounts': accounts
    }