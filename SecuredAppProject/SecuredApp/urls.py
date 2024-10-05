from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('account/<int:account_id>/', views.account_detail, name='account_detail'),
    path('transactions/', views.transactions, name='transactions'),
    path('transfer/<int:account_id>/', views.transfer_funds, name='transfer_funds'),
    path('get_current_accounts/', views.get_current_accounts, name='get_current_accounts'),
    path('download_statement/', views.download_statement, name='download_statement'),
]

# Catch-all for unknown paths
from django.http import HttpResponseNotFound

def custom_page_not_found(request, exception=None):
    return HttpResponseNotFound('This page does not exist.')

handler404 = custom_page_not_found

