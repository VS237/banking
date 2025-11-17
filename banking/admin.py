# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, BankAccounts

class CustomerAdmin(UserAdmin):
    # Remove profile_picture from fieldsets and add_fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Customer Details', {'fields': ('phone_number', 'address', 'city', 'state', 'date_of_birth', 'ssn', 'id_number')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
        ('Customer Details', {
            'fields': ('phone_number', 'address', 'city', 'state', 'date_of_birth', 'ssn', 'id_number'),
        }),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

admin.site.register(Customer, CustomerAdmin)