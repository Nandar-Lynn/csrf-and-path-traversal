# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, Account, Transaction
from decimal import Decimal 
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
import os

def login_view(request):
    # Get the 'next' parameter from the request, if it exists
    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Check if 'next_url' exists and is safe for redirection
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                
                # Otherwise, redirect to 'home'
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    customer = Customer.objects.get(user=request.user)
    accounts = Account.objects.filter(customer=customer)
    transactions = Transaction.objects.filter(account__in=accounts).order_by('-timestamp')[:10]
    return render(request, 'home.html', {'customer': customer, 'accounts': accounts, 'transactions': transactions})

@login_required
# View for showing account details
def account_detail(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
    return render(request, 'account_details.html', {'account': account, 'transactions': transactions})

@login_required
# View for displaying all transactions of a customer
def transactions(request):
    customer = get_object_or_404(Customer, user=request.user)
    accounts = Account.objects.filter(customer=customer)
    transactions = Transaction.objects.filter(account__in=accounts).order_by('-timestamp')
    return render(request, 'transactions.html', {'transactions': transactions})

# @login_required
# def transfer_funds(request, account_id):
#     from_account = get_object_or_404(Account, id=account_id, customer=request.user.customer)

#     # Handle GET request to process the transfer
#     if request.method == 'GET':
#         to_account_number = request.GET.get('to_account')
#         amount = Decimal(request.GET.get('amount'))

#         # Ensure the destination account exists
#         try:
#             to_account = Account.objects.get(account_number=to_account_number)
#         except Account.DoesNotExist:
#             return render(request, 'transfer_fund.html', {'from_account': from_account, 'error': 'Destination account not found.'})

#         # Perform the transfer if sufficient balance
#         if from_account.balance >= amount:
#             from_account.balance -= amount
#             to_account.balance += amount
#             from_account.save()
#             to_account.save()

#             # Record the transactions
#             Transaction.objects.create(
#                 account=from_account,
#                 transaction_type='withdrawal',
#                 amount=amount,
#                 description=f'Transfer to {to_account.account_number}'
#             )
#             Transaction.objects.create(
#                 account=to_account,
#                 transaction_type='deposit',
#                 amount=amount,
#                 description=f'Transfer from {from_account.account_number}'
#             )

#             return redirect('home')
#         else:
#             return render(request, 'transfer_fund.html', {'from_account': from_account, 'error': 'Insufficient funds.'})

#     return render(request, 'transfer_fund.html', {'from_account': from_account})


@login_required
def transfer_funds(request, account_id):
    # Debug print statement to check if the view is called
    print("Transfer function called with account_id:", account_id)
    
    from_account = get_object_or_404(Account, id=account_id, customer=request.user.customer)
    print("From account:", from_account)

    if request.method == 'GET':
        # Debug print to check the GET parameters
        to_account_number = request.GET.get('to_account')
        amount = request.GET.get('amount')

        print("To account from GET:", to_account_number)
        print("Amount from GET:", amount)

        if not to_account_number or not amount:
            print("Missing to_account or amount in GET request.")
            return render(request, 'transfer_fund.html', {
                'from_account': from_account,
                'error': 'Missing required parameters.'
            })

        try:
            amount = Decimal(amount)
        except Exception as e:
            print("Error converting amount to Decimal:", e)
            return render(request, 'transfer_fund.html', {
                'from_account': from_account,
                'error': 'Invalid amount format.'
            })

        try:
            to_account = Account.objects.get(account_number=to_account_number)
            print("To account found:", to_account)
        except Account.DoesNotExist:
            print("To account does not exist.")
            return render(request, 'transfer_fund.html', {
                'from_account': from_account,
                'error': 'Destination account not found.'
            })

        if from_account.balance >= amount:
            print("Sufficient balance, proceeding with transfer.")
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

            # Record the transactions
            Transaction.objects.create(
                account=from_account,
                transaction_type='withdrawal',
                amount=amount,
                description=f'Transfer to {to_account.account_number}'
            )
            Transaction.objects.create(
                account=to_account,
                transaction_type='deposit',
                amount=amount,
                description=f'Transfer from {from_account.account_number}'
            )

            print("Transfer successful.")
            return redirect('home')
        else:
            print("Insufficient funds.")
            return render(request, 'transfer_fund.html', {
                'from_account': from_account,
                'error': 'Insufficient funds.'
            })

    return render(request, 'transfer_fund.html', {'from_account': from_account})

@login_required
def get_current_accounts(request):
    if request.user.is_authenticated:
        # Get all the user's accounts
        accounts = Account.objects.filter(customer=request.user.customer).values('id')
        return JsonResponse(list(accounts), safe=False)
    return JsonResponse({'error': 'User not logged in or no accounts found'}, status=400)

# def download_statement(request):
#     # User provides the statement file name via query parameter
#     file_name = request.GET.get('statement')

#     if not file_name:
#         raise Http404("Statement not found")

#     # Vulnerable: Construct the file path directly from user input without sanitization
#     file_path = os.path.join(settings.BASE_DIR, 'statements', file_name)

#     # Check if the file exists and return it as a download
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as f:
#             response = HttpResponse(f.read(), content_type="application/pdf")
#             response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#             return response
#     else:
#         raise Http404("Statement not found")

def download_statement(request):
    file_name = request.GET.get('statement')

    if not file_name:
        raise Http404("Statement not found")

    # Construct file path by directly concatenating BASE_DIR with user input
    file_path = os.path.normpath(str(settings.BASE_DIR) + '/statements/' + file_name)

    # Print the file path for debugging
    print(f"Attempting to access file: {file_path}")

    # Skip the os.path.exists() check to allow traversal
    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/pdf")
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    except FileNotFoundError:
        print("File does not exist:", file_path)
        raise Http404("Statement not found")
    except Exception as e:
        print(f"Error accessing file: {e}")
        raise Http404("An error occurred while accessing the file")