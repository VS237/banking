from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    
    path('manage_account/', views.manage_account, name='manage_account'),
    path('accounts/', views.account_list, name='account_list'),
    path('create_bank_account/', views.create_bank_account, name='create_bank_account'),
    
    path('logout/', views.logout_user, name='logout'),
    path('create_account/', views.create_account, name='create_account'),
    
    path('make_transaction/', views.make_transaction, name='make_transaction'),
    path('make_request/', views.make_request, name='make_request'),
    
    path('accounts/<int:account_id>/modify/', views.modify_account, name='modify_account'),
    path('accounts/<int:account_id>/delete/', views.delete_account, name='delete_account'),
    path('accounts/<int:account_id>/delete/confirm/', views.delete_account_confirm, name='delete_account_confirm'),
    path('api/accounts/<int:account_id>/balance/', views.get_account_balance, name='account_balance'),
    path('transaction/', views.transaction_view, name='transaction'),

     # ... your existing banking paths
    path('chat/', views.chat_view, name='chat'),  # For the HTML page
    path('chat/api/', views.chat_api, name='chat_api'),  # For the API endpoint

    path('chat/send/', views.chat_handler, name='chat_handler'),
    path('choose_transaction_type/', views.choose_transaction_type, name='choose_transaction_type'),

    path('loans/', views.loans_view, name='loans'),  # New path for loans view

    path('mobile_money/', views.mobile_money_view, name='mobile_money'),  # New path for mobile money view

]
