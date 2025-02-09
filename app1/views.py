from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from sms.models import SMSReport
from report.models import UserLog
from .forms import BankDepositForm, BankWithdrawForm, CustomerForm, LoanCollectionForm, DPSForm, LoanACForm, DPSDepositForm, DPSWithdrawForm
from .forms import LoanSpecialForm, LoanSpecialCollectionForm, GeneralDepositForm, GeneralWithdrawForm, SavingsDepositForm
from .forms import FDRForm, LoanFineForm, Loan_CC_Form, Loan_CC_CollectionForm, LoanSpecialForm, SavingsWithdrawForm
from .models import ActiveBranch, BankTransaction, Customer, DPSDeposit, DPSInstallmentSchedule, DPSTransactionHistory, FDRTransactionHistory, GeneralDeposit, LoanAC, LoanCollection, DPS, Loan_Special, Logo, Package, SavingsDeposit, ShareAC, ShareACTransactionHistory
from .models import SavingsAC, SavingsTransactionHistory, GeneralTransactionHistory, GeneralAC, FDR
from .models import InstallmentSchedule, LoanFine, Loan_CC, Loan_CC_Collection, Loan_CC_InstallmentSchedule, Loan_Special
from primary_setup.models import Branch, DPSScheme, FDRScheme, Holiday, SMSSetting, Somity
from dateutil.relativedelta import relativedelta
import requests
from django.views.decorators.http import require_POST
from functools import wraps
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.http import JsonResponse
from .utils import verification

from environ import Env
env = Env()
Env.read_env()

sms_url=env('SMS_URL')
api_key = env('API_Key')
client_id = env('Client_ID')
sender_id = env('Sender_ID')
SMS = env('SMS')



def send_sms(**kwargs):

    if SMS != 'on':
        return "SMS notifications are turned off. No SMS was sent."
    
    # print('sending sms...')
    
    number = kwargs.get('number')
    title = kwargs.get('title')
    user = kwargs.get('user')
    account_number = kwargs.get('account_number')
    amount = kwargs.get('amount')
    installment = kwargs.get('installment')
    installment_amount = kwargs.get('installment_amount')
    due = kwargs.get('due')
    balance = kwargs.get('balance')

    last_11_digits = str(number)[-11:]
    number = "88" + last_11_digits
    
    sms = SMSSetting.objects.get(title=title)
    if sms.status == 'off':
        return
    msg = sms.content_bengali


    # Fetch somity_name from the Logo model
    try:
        somity_name = Logo.objects.first().somity_name
    except (Logo.DoesNotExist, AttributeError):
        somity_name = "Unknown Somity"

    msg = msg.replace('[somity_name]', somity_name)
    
    if account_number:
        msg = msg.replace('[account_number]', account_number)
    if amount:
        msg = msg.replace('[amount]', str(amount))
    if installment:
        msg = msg.replace('[installment]', str(installment))
    if installment_amount:
        msg = msg.replace('[installment_amount]', str(installment_amount))
    if due:
        msg = msg.replace('[due]', str(due))
    if balance:
        msg = msg.replace('[balance]', str(balance))
    
    # print('msg:', msg)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "senderId": sender_id,
        "is_Unicode": True,
        "message": msg,
        "mobileNumbers": number, 
        "apiKey": api_key,
        "clientId": client_id
    }
    response = requests.post(url=sms_url, headers=headers, json=payload)
    # print(response)
    SMSReport.objects.create(
        sms_type=title,
        mobile_number=number,
        sms_body=msg,
        sent_by=user.username
    )
    return msg
    
    
    
def group_check(user):
    return user.is_authenticated and (user.groups.filter(name='admin').exists() or user.groups.filter(name='manager').exists())

def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/access-denied/')
    
    return _wrapped_view

def access_denied(request):
    return render(request, 'app1/deny.html')




def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # print('ok')
            login(request, user)
            
            UserLog.objects.create(processed_by=request.user, logs_action='Login', description='User logged in',)
            
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'app1/login.html')

@login_required
def signout(request):
    UserLog.objects.create(processed_by=request.user, logs_action='Logout',description='User logged out')
    logout(request)
    return redirect('login')

@staff_required
def home(request):
    apply_fine_for_all_loans()
    apply_fine_for_all_cc_loans()
    date = datetime.now()

    today = timezone.now().date()
    overdue_installments = DPSInstallmentSchedule.objects.filter(due_date__lt=today, installment_status='---')
    for installment in overdue_installments:
        installment.installment_status = 'due'
        installment.save()

    loan_overdue_installments = InstallmentSchedule.objects.filter(due_date__lt=today, installment_status='---')
    for installment in loan_overdue_installments:
        installment.installment_status = 'due'
        installment.save()

    loan_cc_overdue_installments = Loan_CC_InstallmentSchedule.objects.filter(due_date__lt=today, installment_status='---')
    for installment in loan_cc_overdue_installments:
        installment.installment_status = 'due'
        installment.save()

    active_fdrs = FDR.objects.filter(status='active')
    for fdr in active_fdrs:
        fdr.add_monthly_profit()

    # user_permissions = list(request.user.get_all_permissions())
    # for i in range(len(user_permissions)):
    #     print(user_permissions[i])

    # Run the verification logic
    # redirect_response = verification()
    # if redirect_response:
    #     return redirect_response
    
    return render(request, 'app1/home.html', {'date': date})

# @user_passes_test(group_check)
def package(request):
    package = Package.objects.first()
    if not package:
        return render(request, 'app1/package.html', {'error': 'No packages available'})
    
    return render(request, 'app1/package.html', {'package': package})


###################################################################
# Customer

@login_required
def customer_home(request):
    customer = request.user
    loan = LoanAC.objects.filter(customer=customer)
    loan_cc = Loan_CC.objects.filter(customer=customer)
    loan_sp = Loan_Special.objects.filter(customer=customer)
    dps = DPS.objects.filter(customer=customer)
    fdr = FDR.objects.filter(customer=customer)
    share = ShareAC.objects.filter(customer=customer)
    generalAC = get_object_or_404(GeneralAC, customer=customer)
    savingsAC = get_object_or_404(SavingsAC, customer=customer)

    loan_due = sum(l.total_amount - l.paid_amount for l in loan)
    loan_cc_balance = sum(cc.total_amount for cc in loan_cc)
    loan_sp_balance = sum(sp.amount for sp in loan_sp)
    dps_balance = sum(d.total_amount for d in dps)
    fdr_balance = sum(f.balance_amount for f in fdr)
    share_balance = sum(s.balance for s in share)
    share_profit_balance = sum(s.profit_balance for s in share)

    general_savings = generalAC.balance
    special_savings = savingsAC.balance

    context = {
                'customer': customer,
                'loan_due': loan_due,
                'loan_cc_balance': loan_cc_balance,
                'loan_sp_balance': loan_sp_balance,
                'dps_balance': dps_balance,
                'fdr_balance': fdr_balance,
                'share_balance': share_balance,
                'share_profit_balance': share_profit_balance,
                'general_savings': general_savings,
                'special_savings': special_savings,
                'generalAC': generalAC,
                'shares': share,
                'dpss': dps,
                'fdrs': fdr,
                'loans': loan,
                'loan_ccs': loan_cc,
            }
    return render(request, 'app1/customer_home.html', context)

def customer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('customer_home')
        else:
            messages.error(request, 'Invalid credentials or not a customer.')

    # print('ok')
    return render(request, 'app1/customer_login.html')

@login_required
def customer_signout(request):
    # print('ok')
    logout(request)
    return redirect('customer_login')

@login_required
def customer_change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = Customer.objects.get(account_no=request.user.account_no)
        except Customer.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('customer_home')

        if user.password == old_password:
            if new_password == confirm_password:
                user.password = new_password  # Store the new password in plain text
                user.save()
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('customer_home')
            else:
                messages.error(request, 'New password and confirmation do not match.')
        else:
            messages.error(request, 'Old password is incorrect.')
    
# Customer
###################################################################




@login_required
@permission_required('auth.view_permission', raise_exception=True)
def manage_permissions(request):
    groups = Group.objects.all()
    permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')

    if request.method == 'POST':
        action = request.POST.get('action')
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id) if group_id else None
        
        if action == "add":
            group_name = request.POST.get('group_name')
            if group_name:
                new_group, created = Group.objects.get_or_create(name=group_name)
                if created:
                    messages.success(request, f"Group '{group_name}' added successfully!")
                else:
                    messages.warning(request, f"Group '{group_name}' already exists.")
            else:
                messages.error(request, "Group name cannot be empty.")

        elif action == 'edit' and group:
            group_name = request.POST.get('group_name')
            if group_name:
                group.name = group_name
                group.save()
                messages.success(request, f"Group name updated to '{group.name}'.")
            else:
                messages.error(request, "Group name cannot be empty.")

        elif action == 'delete' and group:
            group.delete()
            messages.success(request, "Group deleted successfully.")

        elif action == "permissions" and group:
            selected_permissions = request.POST.getlist('permissions')
            print("Selected permissions:", selected_permissions)  # Debugging line
            group.permissions.clear()  # Clear existing permissions
            group.permissions.set(selected_permissions)  # Assign new permissions
            group.save()
            messages.success(request, f"Permissions updated for group '{group.name}'!")


        return redirect('manage_permissions')

    categorized_permissions = {}
    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in categorized_permissions:
            categorized_permissions[app_label] = []
        categorized_permissions[app_label].append(perm)

    context = {
        'groups': groups,
        'categorized_permissions': categorized_permissions
    }
    return render(request, 'permissions.html', context)






###################################################################
# Customer

@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            active_branch = ActiveBranch.objects.filter(user=request.user).first()
            
            if not active_branch:
                messages.error(request, 'No active branch set.')
                return redirect('customer_add')

            customer = form.save(commit=False)
            customer.branch = active_branch.branch
            customer.processed_by = request.user
            customer.save()

            UserLog.objects.create(processed_by=request.user,logs_action='Add Member',description=f'Account Number: {customer.account_no}')
            UserLog.objects.create(processed_by=request.user,action='Admission Fee',amount=customer.admission_fee, customer=customer)
            UserLog.objects.create(processed_by=request.user,action='Admission Form Fee',amount=customer.admission_form_fee, customer=customer)

            sms_msg = send_sms(
                number=customer.mobile_number,
                title='Add Customer',
                user=request.user,
                account_number=customer.account_no,
            )
            messages.success(request, 'Customer has been added successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm(user=request.user)
    return render(request, 'app1/customer/customer_add.html', {'form': form})

# @user_passes_test(group_check)
@login_required
def customer_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        customers = Customer.objects.filter(branch=active_branch.branch).order_by
    else:
        customers = Customer.objects.none()

    return render(request, 'app1/customer/customer_list.html', {'customers': customers})

@login_required
def customer_details(request, id):
    customer = get_object_or_404(Customer, id=id)
    context = {
        'customer': customer,
    }
    return render(request, 'app1/customer/customer_details.html', context)

@login_required
def customer_edit(request, id):
    customer = get_object_or_404(Customer, id=id)
    # old_password = customer.password
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            data = form.save(commit=False)
            # new_password = data.password
            
            # Check if the password has changed
            # if new_password and new_password != old_password:
            #     # Update the password properly
            #     customer.set_password(new_password)
            #     customer.save()

            data.save()
            messages.success(request, 'Customer details have been updated successfully.')
            UserLog.objects.create(processed_by=request.user, logs_action='Edit Member',description=f'Account Number: {customer.account_no}')
            return redirect('customer_edit', id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    context = {
        'form': form,
    }
    return render(request, 'app1/customer/customer_edit.html', context)

# Customer
################################################################

################################################################
# General AC

@login_required
@permission_required('app1.view_generalac', raise_exception=True)
def general_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        customers = GeneralAC.objects.filter(customer__branch=active_branch.branch).order_by('-id')
    else:
        customers = GeneralAC.objects.none()

    return render(request, 'app1/general/general_list.html', {'customers': customers})

@login_required
@permission_required('app1.add_generaldeposit', raise_exception=True)
def general_deposit(request, id):
    general_ac = get_object_or_404(GeneralAC, id=id)

    if request.method == 'POST':
        form = GeneralDepositForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            general_ac.balance += data.Amount
            general_ac.total_deposit += data.Amount
            data.processed_by = request.user
            data.general = general_ac
            data.save()
            general_ac.save()

            GeneralTransactionHistory.objects.create(
                general=general_ac,
                transaction_type='deposit',
                Amount=data.Amount,
                processed_by=request.user,
                note=data.Note,
                current_balance=general_ac.balance,
                VoucherID=data.VoucherID
            )

            UserLog.objects.create(processed_by=request.user,action=f'Deposit General AC {general_ac.customer.customer_type}',amount=data.Amount, customer=general_ac.customer,)
            UserLog.objects.create(processed_by=request.user,logs_action='Deposit General AC',description=f'Account Number: {general_ac.customer.account_no}, TrxID: {data.VoucherID}')
            
            # msg = f'প্রিয় স্যার, আপনার সাধারণ অ্যাকাউন্টে Tk. {data.Amount} জমা হয়েছে। ব্যালান্স Tk. {general_ac.balance}'
            # send_sms(general_ac.customer.mobile_number, msg, 'Deposit General AC', request.user)
            sms_msg = send_sms(
                number=general_ac.customer.mobile_number,
                title='Deposit General AC',
                user=request.user,
                amount=data.Amount,
                balance=general_ac.balance,
                account_number=general_ac.customer.account_no,
            )
            messages.success(request, sms_msg)
            return redirect('general_list')
        
    else:
        form = GeneralDepositForm()
        
    return render(request, 'app1/general/general_deposit.html', {'form': form, 'data': general_ac})

@login_required
@permission_required('app1.add_generalwithdraw', raise_exception=True)
def general_withdraw(request, id):
    general_ac = get_object_or_404(GeneralAC, id=id)

    if request.method == 'POST':
        form = GeneralWithdrawForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            general_ac.balance -= data.Amount
            general_ac.total_withdraw += data.Amount
            data.processed_by = request.user
            data.general = general_ac
            data.save()
            general_ac.save()

            GeneralTransactionHistory.objects.create(
                general=general_ac,
                transaction_type='withdraw',
                Amount=data.Amount,
                processed_by=request.user,
                note=data.Note,
                current_balance=general_ac.balance, 
                VoucherID=data.VoucherID
            )
            sms_msg = send_sms(
                number=general_ac.customer.mobile_number,
                title='Withdraw General AC',
                user=request.user,
                amount=data.Amount,
                balance=general_ac.balance,
                account_number=general_ac.customer.account_no,
            )
            messages.success(request, sms_msg)
            action = f'Withdraw General AC {general_ac.customer.customer_type}'
            UserLog.objects.create(processed_by=request.user,action=action,amount=data.Amount, customer=general_ac.customer, trx=True)
            
            UserLog.objects.create(processed_by=request.user,logs_action='Withdraw General AC',description=f'Account Number: {general_ac.customer.account_no}, TrxID: {data.VoucherID}')
            return redirect('general_list')
    else:
        form = GeneralWithdrawForm()

    return render(request, 'app1/general/general_withdraw.html', {'form': form, 'data': general_ac})

@login_required
# @permission_required('app1.view_generalac', raise_exception=True)
def general_transaction_history(request, id):
    general = GeneralAC.objects.get(id=id)
    transactions = general.general_transaction_history.all().order_by('-created_at')
    return render(request, 'app1/general/general_transactions.html', {'data': general, 'transactions': transactions})

@login_required
@permission_required('app1.add_generaldeposit', raise_exception=True)
def general_deposit_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            general_ac = GeneralAC.objects.get(customer__account_no=account_no)
            return redirect('general_deposit', id=general_ac.id)
        except GeneralAC.DoesNotExist:
            return render(request, 'app1/general/deposit_search.html', {
                'error': 'Account number not found.'
            })
    return render(request, 'app1/general/deposit_search.html')

@login_required
@permission_required('app1.add_generalwithdraw', raise_exception=True)
def general_withdraw_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            general_ac = GeneralAC.objects.get(customer__account_no=account_no)
            return redirect('general_withdraw', id=general_ac.id)
        except GeneralAC.DoesNotExist:
            return render(request, 'app1/general/withdraw_search.html', {
                'error': 'Account number not found.'
            })
    return render(request, 'app1/general/withdraw_search.html')

@login_required
@permission_required('app1.add_generaldeposit', raise_exception=True)
def somity_wise_general_deposit(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch

    if request.method == 'GET':
        # Existing GET logic
        date = request.GET.get('date')
        group_id = request.GET.get('group')

        if group_id:
            try:
                group_name = Somity.objects.get(id=group_id, branch=active_branch)
            except Somity.DoesNotExist:
                group_name = None
                account = []
                # messages.error(request, "No matching Somity found for the selected group.")
        else:
            group_name = None
            account = []
            # messages.error(request, "No group selected.")

        if date and group_name:
            customers_in_group = Customer.objects.filter(group_id=group_id)
            account = GeneralAC.objects.filter(customer__in=customers_in_group)
        else:
            account = []

        groups = Somity.objects.filter(branch=active_branch)

        context = {
            'entries': account,
            'groups': groups,
            'date': date,
            'group_name': group_name, 
        }

        return render(request, 'credit/somity_wise_general.html', context)

    elif request.method == 'POST':
        # Handle DPS deposits
        selected_ids = request.POST.getlist('selected_ids')

        for id in selected_ids:
            print(id)
            general_ac = get_object_or_404(GeneralAC, id=id)
            print(general_ac)
            # special_ac = get_object_or_404(SavingsAC, id=id)
            special_ac = SavingsAC.objects.get(customer=general_ac.customer) 
            print(special_ac)
            
            general_amount = request.POST.get(f'general_amount_{id}', '0')
            special_amount = request.POST.get(f'special_amount_{id}', '0')

            general_amount = Decimal(general_amount)
            special_amount = Decimal(special_amount)

            print(general_amount, special_amount)

            general_deposit = GeneralDeposit.objects.create(
                general=general_ac,
                Amount=general_amount,
                processed_by=request.user
            )
            special_ac_deposit = SavingsDeposit.objects.create(
                general=special_ac,
                Amount=special_amount,
                processed_by=request.user
            )

            print("data saved")

            general_ac.balance += general_amount
            general_ac.total_deposit += general_amount
            general_ac.save()

            special_ac.balance += special_amount
            special_ac.total_deposit += special_amount
            special_ac.save()

            # Create Transaction History
            GeneralTransactionHistory.objects.create(
                general=general_ac,
                transaction_type='deposit',
                Amount=general_amount,
                processed_by=request.user,
                current_balance=general_ac.balance,
            )
            SavingsTransactionHistory.objects.create(
                general=special_ac,
                transaction_type='deposit',
                Amount=special_amount,
                processed_by=request.user,
                current_balance=special_ac.balance,
            )
            sms_msg = send_sms(
                number=general_ac.customer.mobile_number,
                title='Somity Wise General AC Deposit',
                user=request.user,
                amount=general_amount,
                balance=general_ac.balance,
                account_number=general_ac.customer.account_no,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='Somity Wise General AC Deposit ',description=f'')
            UserLog.objects.create(processed_by=request.user,action=f'Deposit General AC {general_ac.customer.customer_type}',amount=general_amount, customer=general_ac.customer,)
            UserLog.objects.create(processed_by=request.user,action=f'Deposit Special AC {special_ac.customer.customer_type}',amount=special_amount, customer=general_ac.customer,)

        return redirect('somity_wise_general_deposit')

@login_required
@permission_required('app1.add_generaldeposit', raise_exception=True)
def common_collection(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch
    print(f"Active branch: {active_branch}")  # Debug statement

    if request.method == 'GET':
        date = request.GET.get('date')
        account_no = request.GET.get('account_no')
        print(f"Received GET request with date: {date} and account_no: {account_no}")  # Debug statement

        try:
            customer = Customer.objects.get(account_no=account_no, branch=active_branch)
            print(f"Customer found: {customer}")  # Debug statement

            general_ac = GeneralAC.objects.get(customer=customer)
            print(f"GeneralAC found: {general_ac}")  # Debug statement

            special_ac = SavingsAC.objects.get(customer=customer)
            print(f"SavingsAC found: {special_ac}")  # Debug statement

            account = {
                'account_no': customer.account_no,
                'customer_name': customer.customer_name,
                'customer_father': customer.customer_father,
                'customer_mother': customer.customer_mother,
                'mobile_number': customer.mobile_number,
                'customer_type': customer.customer_type,
                'group': customer.group,
                'current_village': customer.current_village,
                'current_post_office': customer.current_post_office,
                'current_thana': customer.current_thana,
                'current_district': customer.current_district,
                'permanent_village': customer.permanent_village,
                'permanent_post_office': customer.permanent_post_office,
                'permanent_thana': customer.permanent_thana,
                'permanent_district': customer.permanent_district,
                'general_ac': general_ac,
                'regular_target': general_ac.regular_target,
                'special_ac': special_ac,
            }
        except Customer.DoesNotExist:
            account = None
            print("Customer.DoesNotExist: No customer found with the provided account number.")  # Debug statement
            # messages.error(request, "No customer found with the provided account number.")
        except GeneralAC.DoesNotExist:
            account = None
            print("GeneralAC.DoesNotExist: No General Savings account found for the customer.")  # Debug statement
            # messages.error(request, "No General Savings account found for the customer.")
        except SavingsAC.DoesNotExist:
            account = None
            print("SavingsAC.DoesNotExist: No Special Savings account found for the customer.")  # Debug statement
            # messages.error(request, "No Special Savings account found for the customer.")

        context = {
            'entries': account,
            'date': date,
        }

        print(f"Context prepared for rendering: {context}")  # Debug statement
        return render(request, 'credit/common_collection.html', context)

    elif request.method == 'POST':
        print("Processing POST request")  # Debug statement
        try:
            account_no = request.POST.get('account_no')
            print(f"POST account_no: {account_no}")  # Debug statement

            customer = Customer.objects.get(account_no=account_no, branch=active_branch)
            print(f"Customer found in POST: {customer}")  # Debug statement

            general_ac = GeneralAC.objects.get(customer=customer)
            print(f"GeneralAC found in POST: {general_ac}")  # Debug statement

            special_ac = SavingsAC.objects.get(customer=customer)
            print(f"SavingsAC found in POST: {special_ac}")  # Debug statement

            general_amount = Decimal(request.POST.get('general_amount', '0'))
            special_amount = Decimal(request.POST.get('special_amount', '0'))
            print(f"General amount: {general_amount}, Special amount: {special_amount}")  # Debug statement

            GeneralDeposit.objects.create(
                general=general_ac,
                Amount=general_amount,
                processed_by=request.user
            )
            print("GeneralDeposit created")  # Debug statement

            SavingsDeposit.objects.create(
                general=special_ac,
                Amount=special_amount,
                processed_by=request.user
            )
            print("SavingsDeposit created")  # Debug statement

            general_ac.balance += general_amount
            general_ac.total_deposit += general_amount
            general_ac.save()
            print(f"Updated GeneralAC balance: {general_ac.balance}")  # Debug statement

            special_ac.balance += special_amount
            special_ac.total_deposit += special_amount
            special_ac.save()
            print(f"Updated SavingsAC balance: {special_ac.balance}")  # Debug statement

            GeneralTransactionHistory.objects.create(
                general=general_ac,
                transaction_type='deposit',
                Amount=general_amount,
                processed_by=request.user,
                current_balance=general_ac.balance,
            )
            print("GeneralTransactionHistory created")  # Debug statement

            SavingsTransactionHistory.objects.create(
                general=special_ac,
                transaction_type='deposit',
                Amount=special_amount,
                processed_by=request.user,
                current_balance=special_ac.balance,
            )
            print("SavingsTransactionHistory created")

            UserLog.objects.create(processed_by=request.user,logs_action='Common Collection',description=f'')
            UserLog.objects.create(processed_by=request.user,action=f'Deposit General AC {general_ac.customer.customer_type}',amount=general_amount, customer=general_ac.customer,)
            UserLog.objects.create(processed_by=request.user,action=f'Deposit Special AC {special_ac.customer.customer_type}',amount=special_amount, customer=general_ac.customer,)

            messages.success(request, "Deposits successfully processed.")
        except Customer.DoesNotExist:
            print("Customer.DoesNotExist in POST: No customer found with the provided account number.")  # Debug statement
            messages.error(request, "No customer found with the provided account number.")
        except GeneralAC.DoesNotExist:
            print("GeneralAC.DoesNotExist in POST: No General Savings account found for the customer.")  # Debug statement
            messages.error(request, "No General Savings account found for the customer.")
        except SavingsAC.DoesNotExist:
            print("SavingsAC.DoesNotExist in POST: No Special Savings account found for the customer.")  # Debug statement
            messages.error(request, "No Special Savings account found for the customer.")
        except Exception as e:
            print(f"Exception in POST: {str(e)}")  # Debug statement
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('common_collection')

# General AC
################################################################

################################################################
# Savings AC

@login_required
@permission_required('app1.view_savingsac', raise_exception=True)
def savings_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        customers = SavingsAC.objects.filter(customer__branch=active_branch.branch).order_by('-id')
    else:
        customers = SavingsAC.objects.none()

    return render(request, 'app1/savings/general_list.html', {'customers': customers})

@login_required
@permission_required('app1.view_savingsdeposit', raise_exception=True)
def savings_deposit(request, id):
    account = get_object_or_404(SavingsAC, id=id)

    if request.method == 'POST':
        form = SavingsDepositForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            account.balance += data.Amount
            account.total_deposit += data.Amount
            data.processed_by = request.user
            data.general = account
            data.save()
            account.save()

            SavingsTransactionHistory.objects.create(
                general=account,
                transaction_type='deposit',
                Amount=data.Amount,
                processed_by=request.user,
                note=data.Note,
                current_balance=account.balance, 
                VoucherID=data.VoucherID
            )
            action = f'Deposit Special AC {account.customer.customer_type}'
            UserLog.objects.create(processed_by=request.user,action=action,amount=data.Amount, customer=account.customer)
            
            UserLog.objects.create(processed_by=request.user,logs_action='deposit_special_ac',description=f'Account Number: {account.customer.account_no}, TrxID: {data.VoucherID}')
            
            return redirect('savings_list')
    else:
        form = SavingsDepositForm()

    return render(request, 'app1/savings/general_deposit.html', {'form': form, 'data': account})

@login_required
@permission_required('app1.view_savingswithdraw', raise_exception=True)
def savings_withdraw(request, id):
    account = get_object_or_404(SavingsAC, id=id)

    if request.method == 'POST':
        form = SavingsWithdrawForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            account.balance -= data.Amount
            account.total_withdraw += data.Amount
            data.processed_by = request.user
            data.general = account
            data.save()
            account.save()

            SavingsTransactionHistory.objects.create(
                general=account,
                transaction_type='withdraw',
                Amount=data.Amount,
                processed_by=request.user,
                note=data.Note,
                current_balance=account.balance,
                VoucherID=data.VoucherID
            )

            action = f'withdraw_special_ac_{account.customer.customer_type}'
            UserLog.objects.create(processed_by=request.user,action=action,amount=data.Amount, customer=account.customer,
                                   transaction_type='cash_out', cashflow_type1='expense', cashflow_type2='payment')
            
            UserLog.objects.create(processed_by=request.user,logs_action='withdraw_special_ac',description=f'Account Number: {account.customer.account_no}, TrxID: {data.VoucherID}')
            return redirect('savings_list')
    else:
        form = SavingsWithdrawForm()

    return render(request, 'app1/savings/general_withdraw.html', {'form': form, 'data': account})

@login_required
def savings_transaction_history(request, id):
    general = SavingsAC.objects.get(id=id)
    transactions = general.savings_transaction_history.all().order_by('-created_at')
    return render(request, 'app1/savings/general_transactions.html', {'data': general, 'transactions': transactions})

@login_required
@permission_required('app1.view_savingsdeposit', raise_exception=True)
def savings_deposit_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            accounnt = SavingsAC.objects.get(customer__account_no=account_no)
            return redirect('savings_deposit', id=accounnt.id)
        except SavingsAC.DoesNotExist:
            return render(request, 'app1/savings/deposit_search.html', {
                'error': 'Account number not found.'
            })
    return render(request, 'app1/savings/deposit_search.html')

@login_required
@permission_required('app1.view_savingswithdraw', raise_exception=True)
def savings_withdraw_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            account = SavingsAC.objects.get(customer__account_no=account_no)
            return redirect('savings_withdraw', id=account.id)
        except SavingsAC.DoesNotExist:
            return render(request, 'app1/savings/withdraw_search.html', {
                'error': 'Account number not found.'
            })
    return render(request, 'app1/savings/withdraw_search.html')

# Savings AC
################################################################

################################################################
# LOAN

@login_required
@permission_required('app1.add_loanac', raise_exception=True)
def loan_search(request):
    return render(request, 'app1/loan/loan_search.html')

@login_required
@permission_required('app1.view_loanac', raise_exception=True)
def loan_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        data = LoanAC.objects.filter(branch=active_branch.branch).order_by('-id')
    else:
        data = LoanAC.objects.none()

    return render(request, 'app1/loan/loan_list.html', {'data': data})

from datetime import date
@login_required
@permission_required('app1.add_loanac', raise_exception=True)
def loan_create(request, account_no):
    try:
        customer = Customer.objects.get(account_no=account_no)
        active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
        if not active_branch:
            messages.error(request, 'No active branch set.')
            return redirect('home')

        if request.method == 'POST':
            form = LoanACForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.customer = customer
                data.processed_by = request.user
                data.branch = active_branch.branch
                data.save()
                messages.success(request, f"Loan created successfully with Transaction ID {data.transaction_id}.")
                
                sms_msg = send_sms(
                    number=customer.mobile_number,
                    title='Add Loan AC',
                    user=request.user,
                    amount=data.loan_amount,
                    installment=data.number_of_installments,
                    installment_amount=data.installment_amount
                )
                messages.success(request, sms_msg)
                UserLog.objects.create(processed_by=request.user,logs_action='Add Loan AC',description=f'Account Number: {customer.account_no}, Loan ID: {data.transaction_id}')
                UserLog.objects.create(processed_by=request.user,action=f'Loan Distribute {customer.customer_type}',amount=data.loan_amount, customer=customer, trx=True)
                UserLog.objects.create(processed_by=request.user,action=f'Loan Share {customer.customer_type}',amount=data.share, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'Loan Form Fee {customer.customer_type}',amount=data.loan_form_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'Insurance Fee',amount=data.insurance_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'Stamp Fee',amount=data.stamp_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'Risk Fee',amount=data.risk_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'Other Fee',amount=data.other_fee, customer=customer)


                data.generate_installment_schedule()
                return redirect('loan_list',)
            else:
                messages.error(request, "There was an error with the form.")
        else:
            form = LoanACForm()

        context = {'customer': customer, 'form': form}
        return render(request, 'app1/loan/loan_create.html', context)
    
    except Customer.DoesNotExist:
        messages.error(request, f"No customer found with account number: {account_no}")
        return redirect('loan_search')

@login_required
@permission_required('app1.view_loanac', raise_exception=True)
def loan_schedule(request, loan_id):
    loan = LoanAC.objects.get(id=loan_id)
    schedules = loan.installment_schedules.all()
    paid_installments_count = schedules.filter(installment_status='paid').count()
    holidays = Holiday.objects.values_list('date', flat=True)
    due = loan.total_amount - loan.paid_amount
    context = {
        'loan': loan,
        'schedules': schedules,
        'holidays': holidays,
        'paid_installments_count': paid_installments_count,
        'due': due,
    }
    return render(request, 'app1/loan/loan_schedule.html', context)


import logging
logger = logging.getLogger('app1')

@login_required
@permission_required('app1.view_loancollection', raise_exception=True)
@transaction.atomic
def loan_collection(request, loan_id):
    logger.info(f"Processing loan collection for loan_id: {loan_id}")
    
    try:
        loan = get_object_or_404(LoanAC, id=loan_id)
        logger.debug(f"Loan retrieved: {loan}")

        if request.method == 'POST':
            logger.info("POST request received.")
            form = LoanCollectionForm(request.POST, loan=loan)
            if form.is_valid():
                logger.info("Form is valid. Processing payment.")
                data = form.save(commit=False)
                payment_amount = data.Amount
                logger.debug(f"Payment amount: {payment_amount}")
                loan_balance = loan.paid_amount + payment_amount

                # Update installment statuses
                installments = InstallmentSchedule.objects.filter(
                    loan=loan, installment_status='---'
                ).order_by('due_date')
                # logger.debug(f"Installments to process: {list(installments)}")

                for installment in installments:
                    installment_total = installment.amount * installment.installment_number
                    logger.debug(f"Checking installment {installment.id}: "
                                 f"Total={installment_total}, Balance={loan_balance}")
                    if loan_balance >= installment_total:
                        installment.installment_status = 'paid'
                        installment.save()
                        logger.info(f"Installment {installment.id} marked as paid.")
                    else:
                        logger.info(f"Stopping installment processing. Insufficient balance.")
                        break

                # Update loan and save the deposit record
                loan.paid_amount += payment_amount
                loan.save()
                logger.info(f"Loan updated: Paid amount = {loan.paid_amount}")

                data.loan = loan
                data.save()
                logger.info(f"Payment record saved: {data}")

                # Calculate principal and profit
                profit_rate = loan.profit_percent / 100
                principal = payment_amount / (1 + profit_rate)
                profit = payment_amount - principal
                logger.debug(f"Calculated Principal: {principal}, Profit: {profit}")

                # Send SMS notification
                sms_msg = send_sms(
                    number=loan.customer.mobile_number,
                    title='Installment Collection',
                    user=request.user,
                    amount=payment_amount,
                    due=str(loan.due),
                    account_number=loan.customer.account_no,
                )
                logger.info(f"SMS sent successfully: {sms_msg}")
                messages.success(request, sms_msg)

                # Create user logs
                UserLog.objects.bulk_create([
                    UserLog(
                        loan=loan,
                        processed_by=request.user,
                        logs_action='Installment Collection',
                        description=f'Account Number: {loan.customer.account_no}, TrxID: {data.VoucherID}'
                    ),
                    UserLog(
                        loan=loan,
                        processed_by=request.user,
                        action=f'Installment Principal {loan.customer.customer_type}',
                        amount=principal,
                        customer=loan.customer
                    ),
                    UserLog(
                        loan=loan,
                        processed_by=request.user,
                        action=f'Installment Profit {loan.customer.customer_type}',
                        amount=profit,
                        customer=loan.customer
                    )
                ])
                logger.info("User logs created successfully.")

                return redirect('loan_schedule', loan_id=loan.id)
            else:
                logger.warning("Form validation failed.")
        else:
            form = LoanCollectionForm(loan=loan)
            logger.info("Rendering form for GET request.")
        
        return render(request, 'app1/loan/loan_collection.html', {'form': form, 'loan': loan})

    except Exception as e:
        logger.error(f"An error occurred while processing loan collection: {e}", exc_info=True)
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('loan_list')  # Redirect to a safe fallback view


@login_required
def loan_trans(request, loan_id):
    loan = LoanAC.objects.get(id=loan_id)
    loan_transactions = LoanCollection.objects.filter(loan=loan)
    context = {
        'loan': loan,
        'loan_transactions': loan_transactions,
    }
    
    return render(request, 'app1/loan/loan_trans.html', context)

@login_required
@permission_required('app1.view_loancollection', raise_exception=True)
def loan_fine(request, loan_id):
    loan = LoanAC.objects.get(id=loan_id)
    loan_fines = LoanFine.objects.filter(loan=loan)
    loan_collection = LoanCollection.objects.filter(loan=loan)
    if request.method == 'POST':
        form = LoanFineForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            loan.fine += data.Amount
            loan.save()
            # Create a new LoanCollection with only the fine amount
            loan_collection = LoanCollection.objects.create(
                loan=loan,
                fine=data.Amount
            )
            loan_collection.save()

            
            data.loan = loan
            data.save()
            return redirect('loan_fine', loan_id=loan.id)
        else:
            messages.error(request, "There was an error with the form.")
    else:
        form = LoanFineForm()

    context = {'form': form, 'loan': loan, 'loan_fines': loan_fines}
    return render(request, 'app1/loan/loan_fine.html', context)

@login_required
@permission_required('app1.view_loancollection', raise_exception=True)
def loan_collection_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            loans = LoanAC.objects.filter(customer=customer)
            
            if loans.exists():
                return render(request, 'app1/loan/loan_cs_results.html', {'loans': loans, 'customer': customer})
            else:
                return render(request, 'app1/loan/loan_cs.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/loan/loan_cs.html', {'error': 'No customer found with this account number in the current branch.'})
    
    return render(request, 'app1/loan/loan_cs.html')

@login_required
@permission_required('app1.add_loanac', raise_exception=True)
def loan_close_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            loans = LoanAC.objects.filter(customer=customer)
            
            if loans.exists():
                return render(request, 'app1/loan/loan_close.html', {'loans': loans, 'customer': customer})
            else:
                return render(request, 'app1/loan/loan_cc.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/loan/loan_cc.html', {'error': 'No customer found with this account number in the current branch.'})
    return render(request, 'app1/loan/loan_cc.html')

@login_required
@permission_required('app1.add_loanac', raise_exception=True)
def loan_close(request, loan_id):
    loan = get_object_or_404(LoanAC, id=loan_id)
    loan.status = 'paid'
    loan.save(update_fields=['status'])
    sms_msg = send_sms(
        number=loan.customer.mobile_number,
        title='Loan Closing',
        user=request.user,
        account_number=loan.customer.account_no,
    )
    messages.success(request, sms_msg)
    UserLog.objects.create(processed_by=request.user,logs_action='Loan Closing',description=f'Account Number: {loan.customer.account_no}')
    UserLog.objects.create(processed_by=request.user,action=f'Loan Closing',amount=loan.loan_amount, customer=loan.customer)
    UserLog.objects.create(processed_by=request.user,action=f'Loan Profit',amount=loan.due_profit, customer=loan.customer)
    return redirect('loan_list') 

@login_required
@permission_required('app1.view_loancollection', raise_exception=True)
def somity_wise_loan(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch

    if request.method == 'GET':
        # Existing GET logic
        date = request.GET.get('date')
        group_id = request.GET.get('group')
        scheme = request.GET.get('scheme')

        if group_id:
            try:
                group_name = Somity.objects.get(id=group_id, branch=active_branch)
            except Somity.DoesNotExist:
                group_name = None
                account = []
                # messages.error(request, "No matching Somity found for the selected group.")
        else:
            group_name = None
            account = []
            # messages.error(request, "No group selected.")

        if date and group_name:
            customers_in_group = Customer.objects.filter(group_id=group_id)
            account = LoanAC.objects.filter(customer__in=customers_in_group, loan_scheme=scheme)
        else:
            account = []

        groups = Somity.objects.filter(branch=active_branch)

        context = {
            'entries': account,
            'groups': groups,
            'date': date,
            'group_name': group_name, 
            'scheme': scheme,
        }

        return render(request, 'credit/somity_wise_loan.html', context)

    elif request.method == 'POST':
        # Handle DPS deposits
        selected_ids = request.POST.getlist('selected_ids')

        for id in selected_ids:
            print(id)

            loan_ac = get_object_or_404(LoanAC, id=id)
            
            received_amount = request.POST.get(f'received_amount_{id}', '0')
            fine_amount = request.POST.get(f'fine_amount_{id}', '0')

            received_amount = Decimal(received_amount)
            fine_amount = Decimal(fine_amount)

            print(received_amount, fine_amount)


            loan_ac.paid_amount += received_amount
            loan_ac.fine += fine_amount

            installments = InstallmentSchedule.objects.filter(loan=loan_ac, installment_status='---').order_by('due_date')
            
            balance = loan_ac.paid_amount
            for installment in installments:

                print(balance, installment.amount*installment.installment_number)
                # if remaining_amount >= installment.amount*installment.installment_number:
                if (balance >= installment.amount*installment.installment_number) or (balance==installment.amount):
                    installment.installment_status = 'paid'
                    installment.save()
                else:
                    # Partial payment or no more full installment payments
                    break

            loan_ac.save()


            # Create Transaction History
            loan_trx = LoanCollection.objects.create(
                loan=loan_ac,
                Amount=received_amount,
                processed_by=request.user,
                fine=fine_amount,
            )

            principal = received_amount/(1+(loan_ac.profit_percent/100))
            profit = received_amount - principal
            due = str(loan_ac.due)
            sms_msg = send_sms(
                number=loan_ac.customer.mobile_number,
                title='Somity Wise Installment Collection',
                user=request.user,
                amount=received_amount,
                due=due,
                account_number=loan_ac.customer.account_no,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='Somity Wise Installment Collection',description=f'Account Number: {loan_ac.customer.account_no}, TrxID: {loan_trx.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Installment Principal {loan_ac.customer.customer_type}',amount=principal, customer=loan_ac.customer)
            UserLog.objects.create(processed_by=request.user,action=f'Installment Profit {loan_ac.customer.customer_type}',amount=profit, customer=loan_ac.customer)

        return redirect('somity_wise_loan')


def apply_fine_for_all_loans():
    # Fetch all loans
    all_loans = LoanAC.objects.all()
    
    for loan in all_loans:
        # Get the fine amount from the loan
        fine_amount = loan.fine_per_missed_installment or Decimal('0.00')

        # Find all due installments that have not had a fine applied yet
        missed_installments = loan.installment_schedules.filter(
            installment_status='due',
            fine_applied=False,
            due_date__lt=timezone.now().date()  # Check for past due dates
        )

        for installment in missed_installments:
            installment.fine_applied = True
            installment.save()

            # Create a LoanFine record for each missed installment
            LoanFine.objects.create(
                loan=loan,
                Date=timezone.now().date(),
                Amount=fine_amount,
                Note=f"Fine for missed installment on {installment.due_date}"
            )

            # Update the loan's total fine amount
            loan.fine += fine_amount
            loan.save()

# LOAN
################################################################

################################################################
# LOAN_CC

@login_required
@permission_required('app1.view_loan_cc', raise_exception=True)
def loan_cc_search(request):
    return render(request, 'app1/loan_cc/loan_cc_search.html')


@login_required
@permission_required('app1.add_loan_cc', raise_exception=True)
def loan_cc_create(request, account_no):
    try:
        customer = Customer.objects.get(account_no=account_no)
        active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
        if not active_branch:
            messages.error(request, 'No active branch set.')
            return redirect('home')

        if request.method == 'POST':
            form = Loan_CC_Form(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.customer = customer
                data.processed_by = request.user
                data.branch = active_branch.branch
                data.save()

                sms_msg = send_sms(
                    number=customer.mobile_number,
                    title='Add CC Loan AC',
                    user=request.user,
                    amount=data.loan_amount,
                )
                messages.success(request, sms_msg)
                UserLog.objects.create(processed_by=request.user,logs_action='Add CC Loan AC',description=f'Account Number: {customer.account_no}, Loan ID: {data.transaction_id}')
                UserLog.objects.create(processed_by=request.user,action=f'CC Loan Distribute',amount=data.loan_amount, customer=customer, trx=True)

                UserLog.objects.create(processed_by=request.user,action=f'CC Loan Opening Fee',amount=data.loan_form_fee, customer=customer)

                UserLog.objects.create(processed_by=request.user,action=f'CC Loan Insurance Fee',amount=data.insurance_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'CC Loan Stamp Fee',amount=data.stamp_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'CC Loan Risk Fee',amount=data.risk_fee, customer=customer)
                UserLog.objects.create(processed_by=request.user,action=f'CC Loan Other Fee',amount=data.other_fee, customer=customer)


                messages.success(request, f"CC Loan created successfully with Transaction ID {data.transaction_id}.")
                data.generate_installment_schedule()
                return redirect('loan_cc_list',)
            else:
                messages.error(request, "There was an error with the form.")
        else:
            form = Loan_CC_Form()

        context = {'customer': customer, 'form': form}
        return render(request, 'app1/loan_cc/loan_cc_create.html', context)
    
    except Customer.DoesNotExist:
        messages.error(request, f"No customer found with account number: {account_no}")
        return redirect('loan_cc_search')

@login_required
@permission_required('app1.view_loan_cc', raise_exception=True)
def loan_cc_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        data = Loan_CC.objects.filter(branch=active_branch.branch).order_by('-id')
        for loan in data:
            loan.paid_installments = loan.loan_cc_installment_schedules.filter(installment_status='paid').count()
            loan.due_amount = loan.total_amount - loan.paid_amount
    else:
        data = Loan_CC.objects.none()

    return render(request, 'app1/loan_cc/loan_cc_list.html', {'data': data})

@login_required
@permission_required('app1.view_loan_cc', raise_exception=True)
def loan_cc_collection(request, loan_id):
    loan_cc = Loan_CC.objects.get(id=loan_id)
    if request.method == 'POST':
        form = Loan_CC_CollectionForm(request.POST, loan_cc=loan_cc)
        if form.is_valid():
            data = form.save(commit=False)

            balance = loan_cc.paid_amount + data.Amount
            loan_cc.fine += data.Fine

            installments = Loan_CC_InstallmentSchedule.objects.filter(loan_cc=loan_cc, installment_status='---').order_by('due_date')
            
            # Process the installments
            for installment in installments:
                # if remaining_amount >= installment.amount*installment.installment_number:
                if balance >= installment.amount*installment.installment_number:
            
                    installment.installment_status = 'paid'
                    installment.save()
                else:
                    # Partial payment or no more full installment payments
                    break

            # Update DPS balance
            loan_cc.paid_amount += data.Amount
            loan_cc.save()

            # Save the deposit record
            data.loan_cc = loan_cc
            data.processed_by = request.user
            data.save()

            due = str(loan_cc.due)
            sms_msg = send_sms(
                number=loan_cc.customer.mobile_number,
                title='CC Installment Collection',
                user=request.user,
                amount=data.Amount,
                due=due,
                account_number=loan_cc.customer.account_no,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='CC Loan Collection',description=f'Account Number: {loan_cc.customer.account_no}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Installment Principal',amount=data.Fine, customer=loan_cc.customer)
            UserLog.objects.create(processed_by=request.user,action=f'CC Loan Profit Collection',amount=data.Amount, customer=loan_cc.customer)

            return redirect('loan_cc_list')
    else:
        form = Loan_CC_CollectionForm(loan_cc=loan_cc)
    return render(request, 'app1/loan_cc/loan_cc_collection.html', {'form': form, 'loan': loan_cc})

@login_required
def loan_cc_trans(request, loan_id):
    loan_cc = Loan_CC.objects.get(id=loan_id)
    loan_transactions = Loan_CC_Collection.objects.filter(loan_cc=loan_cc)
    loan_cc.due_amount = loan_cc.total_amount - loan_cc.paid_amount
    context = {
        'loan': loan_cc,
        'loan_transactions': loan_transactions,
    }
    
    return render(request, 'app1/loan_cc/loan_cc_trans.html', context)

@login_required
@permission_required('app1.view_loan_cc', raise_exception=True)
def loan_cc_collection_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            loans = Loan_CC.objects.filter(customer=customer)
            
            if loans.exists():
                return render(request, 'app1/loan/loan_cs_results.html', {'loans': loans, 'customer': customer})
            else:
                return render(request, 'app1/loan/loan_cs.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/loan/loan_cs.html', {'error': 'No customer found with this account number in the current branch.'})
    
    return render(request, 'app1/loan/loan_cs.html')

@login_required
@permission_required('app1.add_loan_cc', raise_exception=True)
def loan_cc_close_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            loans = Loan_CC.objects.filter(customer=customer)
            
            if loans.exists():
                return render(request, 'app1/loan_cc/loan_close.html', {'loans': loans, 'customer': customer})
            else:
                return render(request, 'app1/loan_cc/loan_cc.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/loan_cc/loan_cc.html', {'error': 'No customer found with this account number in the current branch.'})
    return render(request, 'app1/loan_cc/loan_cc.html')

@login_required
@permission_required('app1.add_loan_cc', raise_exception=True)
def loan_cc_close(request, loan_id):
    loan = get_object_or_404(Loan_CC, id=loan_id)
    loan.status = 'paid'
    loan.save(update_fields=['status'])

    sms_msg = send_sms(
        number=loan.customer.mobile_number,
        title='CC Loan Closing',
        user=request.user,
        account_number=loan.customer.account_no,
    )
    messages.success(request, sms_msg)
    UserLog.objects.create(processed_by=request.user,logs_action='CC Loan Closing',description=f'Account Number: {loan.customer.account_no}')
    UserLog.objects.create(processed_by=request.user,action=f'CC Loan Closing',amount=loan.loan_amount, customer=loan.customer)
    UserLog.objects.create(processed_by=request.user,action=f'CC Loan Profit',amount=loan.due_profit, customer=loan.customer)
    return redirect('loan_cc_list') 


def apply_fine_for_all_cc_loans():
    # Fetch all loans
    all_loans = Loan_CC.objects.all()
    
    for loan in all_loans:
        # Get the fine amount from the loan
        fine_amount = loan.fine_per_missed_installment or Decimal('0.00')

        # Find all due installments that have not had a fine applied yet
        missed_installments = loan.loan_cc_installment_schedules.filter(
            installment_status='due',
            fine_applied=False,
            due_date__lt=timezone.now().date()  # Check for past due dates
        )

        for installment in missed_installments:
            installment.fine_applied = True
            installment.save()

            # Create a LoanFine record for each missed installment
            # LoanFine.objects.create(
            #     loan=loan,
            #     Date=timezone.now().date(),
            #     Amount=fine_amount,
            #     Note=f"Fine for missed installment on {installment.due_date}"
            # )

            # Update the loan's total fine amount
            loan.fine += fine_amount
            loan.save()

# LOAN_CC
################################################################

################################################################
# Special LOAN

@login_required
@permission_required('app1.add_loan_sp', raise_exception=True)
def loan_sp_search(request):
    return render(request, 'app1/loan_sp/loan_search.html')

@login_required
@permission_required('app1.add_loan_sp', raise_exception=True)
def loan_sp_create(request, account_no):
    try:
        customer = Customer.objects.get(account_no=account_no)
        active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
        if not active_branch:
            messages.error(request, 'No active branch set.')
            return redirect('home')

        if request.method == 'POST':
            form = LoanSpecialForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.customer = customer
                data.processed_by = request.user
                data.branch = active_branch.branch
                data.save()
                messages.success(request, f"Special Loan created successfully with Transaction ID {data.transaction_id}.")

                UserLog.objects.create(processed_by=request.user,logs_action='Add Special Loan AC',description=f'Account Number: {customer.account_no}, Loan ID: {data.transaction_id}')
                UserLog.objects.create(processed_by=request.user,action=f'Special Loan Distribute',amount=data.amount, customer=customer, trx=True)

                return redirect('loan_sp_list',)
            else:
                messages.error(request, "There was an error with the form.")
        else:
            form = LoanSpecialForm()

        context = {'customer': customer, 'form': form}
        return render(request, 'app1/loan_sp/loan_create.html', context)
    
    except Customer.DoesNotExist:
        messages.error(request, f"No customer found with account number: {account_no}")
        return redirect('loan_sp_search')

@login_required
@permission_required('app1.view_loan_sp', raise_exception=True)
def loan_sp_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        data = Loan_Special.objects.filter(branch=active_branch.branch).order_by('-id')
    else:
        data = Loan_Special.objects.none()

    return render(request, 'app1/loan_sp/loan_list.html', {'data': data})

@login_required
@permission_required('app1.view_loan_sp', raise_exception=True)
def loan_sp_collection(request, loan_id):
    loan = Loan_Special.objects.get(id=loan_id)
    if request.method == 'POST':
        form = LoanSpecialCollectionForm(request.POST, loan=loan)
        if form.is_valid():
            data = form.save(commit=False)

            loan.profit = data.Amount
            loan.status = 'paid'
            loan.end_date = data.Date
            loan.save()

            data.loan = loan
            data.processed_by = request.user
            data.save()

            UserLog.objects.create(processed_by=request.user,logs_action='Special Loan AC Closing',description=f'Account Number: {loan.customer.account_no}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Special Loan Closing',amount=loan.amount, customer=loan.customer)
            UserLog.objects.create(processed_by=request.user,action=f'Special Loan Profit',amount=data.Amount, customer=loan.customer)

            return redirect('loan_sp_list')
    else:
        form = LoanSpecialCollectionForm(loan=loan)
    return render(request, 'app1/loan_sp/loan_collection.html', {'form': form, 'loan': loan})

@login_required
@permission_required('app1.view_loan_sp', raise_exception=True)
def loan_sp_close_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            loans = Loan_Special.objects.filter(customer=customer)
            
            if loans.exists():
                return render(request, 'app1/loan_sp/loan_close.html', {'loans': loans, 'customer': customer})
            else:
                return render(request, 'app1/loan_sp/loan_cc.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/loan_sp/loan_cc.html', {'error': 'No customer found with this account number in the current branch.'})
    return render(request, 'app1/loan_sp/loan_cc.html')

@login_required
@permission_required('app1.add_loan_sp', raise_exception=True)
def loan_sp_close(request, loan_id):
    loan = get_object_or_404(Loan_Special, id=loan_id)
    loan.status = 'paid'
    loan.save(update_fields=['status'])
    return redirect('loan_sp_list') 

# Special LOAN
################################################################

################################################################
# DPS

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_search(request):
    return render(request, 'app1/dps/dps_search.html')

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    if active_branch:
        data = DPS.objects.filter(branch=active_branch.branch).order_by('-id')
        for dps in data:
            # dps.paid_installments = dps.dps_installment_schedules.filter(installment_status='paid').count()
            dps.due_amount = dps.total_amount - dps.balance
    else:
        data = DPS.objects.none()

    return render(request, 'app1/dps/dps_list.html', {'data': data})

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_create(request, account_no):
    try:
        customer = Customer.objects.get(account_no=account_no)
        active_branch = ActiveBranch.objects.filter(user=request.user).first()

        if not active_branch:
            messages.error(request, 'No active branch set.')
            return redirect('home')

        if request.method == 'POST':
            form = DPSForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.customer = customer
                data.processed_by = request.user
                data.branch = active_branch.branch
                data.save()
                data.generate_installment_schedule()
                messages.success(request, f"DPS created successfully with Transaction ID {data.transaction_id}.")

                sms_msg = send_sms(
                    number=customer.mobile_number,
                    title='Add DPS AC',
                    user=request.user,
                    amount=data.dps_opening_charge,
                )
                messages.success(request, sms_msg)
                UserLog.objects.create(processed_by=request.user,logs_action='Add DPS AC',description=f'Account Number: {customer.account_no}, DPS ID: {data.transaction_id}')
                UserLog.objects.create(processed_by=request.user,action=f'DPS Opening Charge',amount=data.dps_opening_charge, customer=customer)

                return redirect('dps_list')
            else:
                messages.error(request, "There was an error with the form.")
        else:
            form = DPSForm()

        dps_schemes = list(DPSScheme.objects.values())

        context = {
            'customer': customer,
            'form': form,
            'dps_schemes': dps_schemes,
        }
        return render(request, 'app1/dps/dps_create.html', context)
    except Customer.DoesNotExist:
        messages.error(request, f"No customer found with account number: {account_no}")
        return redirect('dps_search')

@login_required
def dps_schedule(request, id):
    dps = DPS.objects.get(id=id)
    schedules = dps.dps_installment_schedules.all()
    paid_installments_count = schedules.filter(installment_status='paid').count()
    holidays = Holiday.objects.values_list('date', flat=True)
    due = dps.total_amount - dps.balance
    context = {
        'dps': dps,
        'schedules': schedules,
        'holidays': holidays,
        'paid_installments_count': paid_installments_count,
        'due': due,
    }
    return render(request, 'app1/dps/dps_schedule.html', context)

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_deposit(request, id):
    dps = get_object_or_404(DPS, id=id)
    if request.method == 'POST':
        form = DPSDepositForm(request.POST, dps=dps)
        if form.is_valid():
            data = form.save(commit=False)
            amount_to_deposit = data.Amount
            remaining_amount = amount_to_deposit
            print(f"Amount to deposit: {amount_to_deposit}")
            print(f"Current DPS balance: {dps.balance}")

            # Fetch due installments in order
            installments = DPSInstallmentSchedule.objects.filter(dps=dps, installment_status='---').order_by('due_date')
            
            # Process the installments
            for installment in installments:
                if remaining_amount >= installment.amount*installment.installment_number:
                    # Fully pay this installment
                    remaining_amount -= installment.amount
                    installment.installment_status = 'paid'
                    installment.save()
                else:
                    # Partial payment or no more full installment payments
                    break

            # Update DPS balance
            dps.balance += amount_to_deposit
            dps.save()
            print(f"Updated DPS balance: {dps.balance}")

            # Save the deposit record
            data.dps = dps
            data.processed_by = request.user
            data.save()

            DPSTransactionHistory.objects.create(
                dps=dps,
                transaction_type='deposit',
                amount=data.Amount,
                processed_by=request.user,
                note=data.Note,
                current_balance=dps.balance, 
                fine=data.Fine,
                VoucherID=data.VoucherID
            )

            sms_msg = send_sms(
                number=dps.customer.mobile_number,
                title='Deposit DPS',
                user=request.user,
                amount=data.Amount,
                balance=dps.balance,
                account_number=dps.customer.account_no,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='Deposit DPS',description=f'Account Number: {dps.customer.account_no}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Deposit to DPS',amount=data.Amount, customer=dps.customer)
            UserLog.objects.create(processed_by=request.user,action=f'Deposit Penalty',amount=data.Fine, customer=dps.customer)

            return redirect('dps_deposit', id=dps.id)
    else:
        form = DPSDepositForm(dps=dps)
    return render(request, 'app1/dps/dps_deposit.html', {'form': form, 'dps': dps})

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_withdraw(request, id):
    dps = DPS.objects.get(id=id)
    if request.method == 'POST':
        form = DPSWithdrawForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.dps = dps
            withdrawal.processed_by = request.user
            withdrawal.save()

            # Deduct balance
            dps.balance -= withdrawal.Amount
            dps.save()

            # Update installment statuses
            today = timezone.now().date()
            installments = DPSInstallmentSchedule.objects.filter(dps=dps)

            for installment in installments:
                if installment.due_date < today:
                    if dps.balance < installment.amount*installment.installment_number:
                        installment.installment_status = 'due'
                elif installment.due_date >= today:
                    if dps.balance < installment.amount*installment.installment_number:
                        installment.installment_status = '---'
                installment.save()

            DPSTransactionHistory.objects.create(
                dps=dps,
                transaction_type='withdraw',
                amount=withdrawal.Amount,
                processed_by=request.user,
                note=withdrawal.Note,
                current_balance=dps.balance, 
                VoucherID=withdrawal.VoucherID
            )
            sms_msg = send_sms(
                number=dps.customer.mobile_number,
                title='Withdraw DPS',
                user=request.user,
                amount=withdrawal.Amount,
                balance=dps.balance,
                account_number=dps.customer.account_no,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,action='Withdraw from DPS',amount=withdrawal.Amount, customer=dps.customer, trx=True)
            UserLog.objects.create(processed_by=request.user,action='DPS Profit Withdraw',amount=withdrawal.Give_Profit, customer=dps.customer, trx=True)
            
            UserLog.objects.create(processed_by=request.user,logs_action='Withdraw DPS AC',description=f'Account Number: {dps.customer.account_no}, TrxID: {withdrawal.VoucherID}')

            return redirect('dps_schedule', id=dps.id)
    else:
        form = DPSWithdrawForm()

    return render(request, 'app1/dps/dps_withdraw.html', {'form': form, 'dps': dps})

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_transaction(request, id):
    dps = DPS.objects.get(id=id)
    transactions = dps.transaction_history.all().order_by('-date')
    return render(request, 'app1/dps/dps_transaction.html', {'dps': dps, 'transactions': transactions})

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_deposit_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            dps = DPS.objects.filter(customer=customer)
            
            if dps.exists():
                return render(request, 'app1/dps/dps_ds_results.html', {'dps': dps, 'customer': customer})
            else:
                return render(request, 'app1/dps/dps_ds.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/dps/dps_ds.html', {'error': 'No customer found with this account number in the current branch.'})
    
    return render(request, 'app1/dps/dps_ds.html')

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_withdraw_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            dps = DPS.objects.filter(customer=customer)
            
            if dps.exists():
                return render(request, 'app1/dps/dps_ws_results.html', {'dps': dps, 'customer': customer})
            else:
                return render(request, 'app1/dps/dps_ws.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/dps/dps_ws.html', {'error': 'No customer found with this account number in the current branch.'})
    
    return render(request, 'app1/dps/dps_ws.html')

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def dps_close_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
           
            dps = DPS.objects.filter(customer=customer)
            
            if dps.exists():
                return render(request, 'app1/dps/dps_cs_results.html', {'dps': dps, 'customer': customer})
            else:
                return render(request, 'app1/dps/dps_cs.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/dps/dps_cs.html', {'error': 'No customer found with this account number in the current branch.'})
    return render(request, 'app1/dps/dps_cs.html')

@login_required
@require_POST
@permission_required('app1.add_dps', raise_exception=True)
def dps_close(request, id):
    dps = get_object_or_404(DPS, id=id)
    
    # Retrieve values from POST request
    profit_percentage = request.POST.get('profit_percentage')
    profit_taka = request.POST.get('profit_taka')
    closing_charge = request.POST.get('closing_charge')
    bonus = request.POST.get('performance_bonus')
    
    # Convert values to float and update the model
    if profit_percentage:
        dps.profit_percent = float(profit_percentage)
    if profit_taka:
        dps.profit_taka = float(profit_taka)
    if closing_charge:
        dps.dps_closing_charge = float(closing_charge)
    if bonus:
        dps.bonus = float(bonus)

    # Update status and save the model
    dps.status = 'closed'
    dps.save(update_fields=['status', 'profit_percent', 'profit_taka', 'dps_closing_charge', 'bonus'])

    sms_msg = send_sms(
        number=dps.customer.mobile_number,
        title='DPS Closing',
        user=request.user,
        account_number=dps.customer.account_no,
    )
    messages.success(request, sms_msg)
    UserLog.objects.create(processed_by=request.user,logs_action='DPS AC Closed',description=f'Account Number: {dps.customer.account_no}, DPS ID: {dps.transaction_id}')

    UserLog.objects.create(processed_by=request.user,action=f'DPS Closing',amount=dps.balance, customer=dps.customer, trx=True)
    UserLog.objects.create(processed_by=request.user,action=f'DPS Profit Withdraw',amount=profit_taka, customer=dps.customer, trx=True)
    UserLog.objects.create(processed_by=request.user,action=f'DPS Performance Bonus',amount=bonus, customer=dps.customer, trx=True)
    UserLog.objects.create(processed_by=request.user,action=f'DPS Closing Charge',amount=closing_charge, customer=dps.customer)
    return redirect('dps_list')

@login_required
@permission_required('app1.add_dps', raise_exception=True)
def somity_wise_dps_deposit(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch

    if request.method == 'GET':
        # Existing GET logic
        date = request.GET.get('date')
        group_id = request.GET.get('group')

        if group_id:
            try:
                group_name = Somity.objects.get(id=group_id, branch=active_branch)
            except Somity.DoesNotExist:
                group_name = None
                dps_entries = []
                # messages.error(request, "No matching Somity found for the selected group.")
        else:
            group_name = None
            dps_entries = []
            # messages.error(request, "No group selected.")

        if date and group_name:
            customers_in_group = Customer.objects.filter(group_id=group_id)
            dps_entries = DPS.objects.filter(customer__in=customers_in_group)
        else:
            dps_entries = []

        groups = Somity.objects.filter(branch=active_branch)

        context = {
            'dps_entries': dps_entries,
            'groups': groups,
            'date': date,
            'group_name': group_name, 
        }

        return render(request, 'credit/somity_wise_dps.html', context)

    elif request.method == 'POST':
        # Handle DPS deposits
        selected_dps_ids = request.POST.getlist('selected_dps')

        for dps_id in selected_dps_ids:
            dps = get_object_or_404(DPS, id=dps_id)
            
            # Safely convert amounts
            amount = request.POST.get(f'amount_{dps_id}', '0')
            fine = request.POST.get(f'fine_{dps_id}', '0')
            
            try:
                amount = Decimal(amount)
                fine = Decimal(fine)
            except (InvalidOperation, ValueError):
                messages.error(request, "Invalid amount or fine value provided.")
                return redirect('somity_wise_dps_deposit')

            note = request.POST.get(f'note_{dps_id}', '')

            print(note)

            # Create DPS Deposit
            dps_deposit = DPSDeposit.objects.create(
                dps=dps,
                Amount=amount,
                Fine=fine,
                Note=note,
                processed_by=request.user
            )

            print("dps saved")
            dps.balance += amount
            # Fetch due installments in order
            installments = DPSInstallmentSchedule.objects.filter(dps=dps, installment_status='---').order_by('due_date')
            
            # Process the installments
            remaining_amount = dps.balance
            for installment in installments:
                print(remaining_amount, installment.amount*installment.installment_number)
                if remaining_amount >= installment.amount*installment.installment_number :
                    # Fully pay this installment
                    remaining_amount -= installment.amount
                    installment.installment_status = 'paid'
                    installment.save()
                else:
                    # Partial payment or no more full installment payments
                    break


            # Update DPS balance
            
            dps.save()

            # Create Transaction History
            DPSTransactionHistory.objects.create(
                dps=dps,
                transaction_type='deposit',
                amount=amount,
                processed_by=request.user,
                note=note,
                current_balance=dps.balance,
                fine=fine,
            )

            sms_msg = send_sms(
                number=dps.customer.mobile_number,
                title='Somity Wise DPS Deposit',
                user=request.user,
                amount=amount,
                balance=dps.balance,
                account_number=dps.customer.account_no,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='Somity Wise DPS Deposit',description=f'Account Number: {dps.customer.account_no}, TrxID: {dps_deposit.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Deposit to DPS',amount=amount, customer=dps.customer)
            UserLog.objects.create(processed_by=request.user,action=f'Deposit Penalty',amount=fine, customer=dps.customer)

        return redirect('somity_wise_dps_deposit')

# DPS
################################################################

################################################################
# FDR

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_search(request):
    schemes = FDRScheme.objects.all()
    context = {
        'schemes': schemes,
    }
    return render(request, 'app1/fdr/fdr_search.html', context)

@login_required
@permission_required('app1.view_fdr', raise_exception=True)
def fdr_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        customers = FDR.objects.filter(customer__branch=active_branch.branch).order_by('-id')
    else:
        customers = FDR.objects.none()

    return render(request, 'app1/fdr/fdr_list.html', {'customers': customers})

@login_required
@permission_required('app1.view_fdr', raise_exception=True)
def fdr_create(request, account_no):
    customer = get_object_or_404(Customer, account_no=account_no)
    scheme_id = request.GET.get('scheme_id')
    scheme = get_object_or_404(FDRScheme, id=scheme_id) if scheme_id else None

    if request.method == 'POST':
        form = FDRForm(request.POST, scheme=scheme)
        if form.is_valid():
            fdr = form.save(commit=False)
            fdr.customer = customer
            fdr.scheme = scheme
            fdr.processed_by = request.user
            fdr.balance_amount = fdr.opening_amount
            fdr.monthly_profit_percentage = scheme.profit_percent
            fdr.end_date = fdr.start_date + relativedelta(months=scheme.duration)

            fdr.save()

            sms_msg = send_sms(
                number=customer.mobile_number,
                title='Add FDR AC',
                user=request.user,
                amount=fdr.opening_amount,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='Add FDR AC',description=f'Account Number: {customer.account_no}, DPS ID: {fdr.transaction_id}')
            UserLog.objects.create(processed_by=request.user,action=f'FDR Opening',amount=fdr.opening_amount, customer=customer)

            return redirect('home')
    else:
        form = FDRForm(scheme=scheme)

    return render(request, 'app1/fdr/fdr_create.html', {'form': form, 'customer': customer})

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_deposit(request, id):
    fdr = get_object_or_404(FDR, id=id)
    customer = fdr.customer

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        processed_by = request.user

        monthly_profit_percentage = request.POST.get('new_profit_rate')
        if monthly_profit_percentage:
            fdr.monthly_profit_percentage = monthly_profit_percentage

        fdr.balance_amount += Decimal(amount)
        fdr.monthly_profit_taka = Decimal(fdr.balance_amount) * (Decimal(fdr.monthly_profit_percentage)/100) 
        fdr.save()

        fdr_trans = FDRTransactionHistory.objects.create(
            fdr=fdr,
            transaction_type='deposit',
            Amount=Decimal(amount),
            processed_by=processed_by,
            note=note,
            current_balance=fdr.balance_amount,
        )

        
        sms_msg = send_sms(
            number=fdr.customer.mobile_number,
            title='Deposit FDR',
            user=request.user,
            amount=amount,
            balance=fdr.balance_amount,
            account_number=fdr.customer.account_no,
        )
        messages.success(request, sms_msg)
        
        UserLog.objects.create(processed_by=request.user,logs_action='Deposit FDR',description=f'Account Number: {fdr.customer.account_no}, TrxID: {fdr_trans.VoucherID}')
        UserLog.objects.create(processed_by=request.user,action=f'FDR Balance Deposit',amount=amount, customer=fdr.customer)

        return redirect('fdr_list')

    return render(request, 'app1/fdr/fdr_deposit.html', {'fdr': fdr, 'customer': customer})

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_withdraw(request, id):
    fdr = get_object_or_404(FDR, id=id)
    customer = fdr.customer

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        processed_by = request.user

        monthly_profit_percentage = request.POST.get('new_profit_rate')
        if monthly_profit_percentage:
            fdr.monthly_profit_percentage = monthly_profit_percentage

        fdr.balance_amount -= Decimal(amount)
        fdr.monthly_profit_taka = fdr.balance_amount * (fdr.monthly_profit_percentage/100) 
        fdr.save()

        fdr_trans = FDRTransactionHistory.objects.create(
            fdr=fdr,
            transaction_type='withdraw',
            Amount=Decimal(amount),
            processed_by=processed_by,
            note=note,
            current_balance=fdr.balance_amount,
        )
        sms_msg = send_sms(
            number=fdr.customer.mobile_number,
            title='FDR Balance Withdraw',
            user=request.user,
            amount=amount,
            balance=fdr.balance_amount,
            account_number=fdr.customer.account_no,
        )
        messages.success(request, sms_msg)
        UserLog.objects.create(processed_by=request.user,logs_action='FDR Balance Withdraw',description=f'Account Number: {fdr.customer.account_no}, TrxID: {fdr_trans.VoucherID}')
        UserLog.objects.create(processed_by=request.user,action=f'FDR Balance Withdraw',amount=amount, customer=fdr.customer)

        return redirect('fdr_list')

    return render(request, 'app1/fdr/fdr_withdraw.html', {'fdr': fdr, 'customer': customer})

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_profit_withdraw(request, id):
    fdr = get_object_or_404(FDR, id=id)
    customer = fdr.customer

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        note = f'{note} : Profit Withdraw'
        processed_by = request.user

        fdr.available_profit -= Decimal(amount)
        fdr.paid_profit += Decimal(amount)

        fdr.save()

        fdr_trx = FDRTransactionHistory.objects.create(
            fdr=fdr,
            transaction_type='withdraw',
            Amount=Decimal(amount),
            processed_by=processed_by,
            note=note,
            current_balance=fdr.balance_amount,
        )
        sms_msg = send_sms(
            number=fdr.customer.mobile_number,
            title='FDR Profit Withdraw',
            user=request.user,
            amount=amount,
            balance=fdr.balance_amount,
            account_number=fdr.customer.account_no,
        )
        messages.success(request, sms_msg)
        UserLog.objects.create(processed_by=request.user,logs_action='FDR Profit Withdraw',description=f'Account Number: {customer.account_no}, Loan ID: {fdr_trx.VoucherID}')
        UserLog.objects.create(processed_by=request.user,action=f'FDR Profit Withdraw',amount=amount, customer=customer, trx=True)

        return redirect('fdr_list')

    return render(request, 'app1/fdr/fdr_profit_withdraw.html', {'fdr': fdr, 'customer': customer})

@login_required
@permission_required('app1.view_fdr', raise_exception=True)
def fdr_transaction_history(request, id):
    fdr = FDR.objects.get(id=id)
    transactions = fdr.fdr_transaction_history.all().order_by('-created_at')
    return render(request, 'app1/fdr/fdr_transactions.html', {'data': fdr, 'transactions': transactions})

@login_required
@permission_required('app1.view_fdr', raise_exception=True)
def fdr_profit(request, id):
    fdr = get_object_or_404(FDR, id=id)
    profit_history = fdr.profit_history.all().order_by('-added_on')
    
    context = {
        'fdr': fdr,
        'profit_history': profit_history
    }
    
    return render(request, 'app1/fdr/fdr_profit.html', context)

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_deposit_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            fdr = FDR.objects.get(customer__account_no=account_no)
            return redirect('fdr_deposit', fdr.id)
        except FDR.DoesNotExist:
            context = {'error': f'No share account found with account number: {account_no}'}
            return render(request, 'app1/fdr/fdr_deposit_search.html', context)
    return render(request, 'app1/fdr/fdr_deposit_search.html')

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_profit_withdraw_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            fdr = FDR.objects.filter(customer=customer)
            
            if fdr.exists():
                return render(request, 'app1/fdr/fdr_pws.html', {'fdrs': fdr, 'customer': customer})
            else:
                return render(request, 'app1/fdr/fdr_debit_search.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/fdr/fdr_debit_search.html', {'error': 'No customer found with this account number in the current branch.'})
    
    return render(request, 'app1/fdr/fdr_debit_search.html')

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_balance_withdraw_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
            # Find loans for the customer
            fdr = FDR.objects.filter(customer=customer)
            
            if fdr.exists():
                return render(request, 'app1/fdr/fdr_bws.html', {'fdrs': fdr, 'customer': customer})
            else:
                return render(request, 'app1/fdr/fdr_debit_search.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/fdr/fdr_debit_search.html', {'error': 'No customer found with this account number in the current branch.'})
    
    return render(request, 'app1/fdr/fdr_debit_search.html')

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_close_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        # Check if the customer exists in the active branch
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()
        
        if customer:
           
            fdr = FDR.objects.filter(customer=customer)
            
            if fdr.exists():
                return render(request, 'app1/fdr/fdr_cs_results.html', {'fdrs': fdr, 'customer': customer})
            else:
                return render(request, 'app1/fdr/fdr_debit_search.html', {'error': 'No loans found for this account number.'})
        else:
            return render(request, 'app1/fdr/fdr_debit_search.html', {'error': 'No customer found with this account number in the current branch.'})
    return render(request, 'app1/fdr/fdr_debit_search.html')

@login_required
@permission_required('app1.add_fdr', raise_exception=True)
def fdr_close(request, id):
    fdr = get_object_or_404(FDR, id=id)
    fdr.status = 'closed'
    fdr.save(update_fields=['status'])

    sms_msg = send_sms(
        number=fdr.customer.mobile_number,
        title='FDR Closing',
        user=request.user,
        account_number=fdr.customer.account_no,
    )
    messages.success(request, sms_msg)
    UserLog.objects.create(processed_by=request.user,logs_action='FDR Closing',description=f'Account Number: {fdr.customer.account_no}, TrxID: {fdr.transaction_id}')
    UserLog.objects.create(processed_by=request.user,action=f'FDR Profit Withdraw',amount=fdr.available_profit, customer=fdr.customer, trx=True)
    UserLog.objects.create(processed_by=request.user,action=f'FDR Closing',amount=fdr.balance_amount, customer=fdr.customer, trx=True)

    return redirect('fdr_list') 

# FDR
################################################################

################################################################
# ShareAC

@login_required
@permission_required('app1.view_shareac', raise_exception=True)
def share_list(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if active_branch:
        customers = ShareAC.objects.filter(customer__branch=active_branch.branch)
    else:
        customers = ShareAC.objects.none()

    return render(request, 'app1/share/share_list.html', {'customers': customers})


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_deposit(request, share_id):
    share_ac = get_object_or_404(ShareAC, share_id=share_id)
    customer = share_ac.customer

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        processed_by = request.user

        share_ac.balance += Decimal(amount)
        share_ac.deposit += Decimal(amount)
        share_ac.save()

        trx = ShareACTransactionHistory.objects.create(
            share_ac=share_ac,
            transaction_type='deposit',
            Amount=Decimal(amount),
            processed_by=processed_by,
            note=note,
            balance=share_ac.balance,
        )
        sms_msg = send_sms(
            number=share_ac.customer.mobile_number,
            title='Deposit Share AC',
            user=request.user,
            amount=amount,
            balance=share_ac.balance,
            account_number=share_ac.customer.account_no,
        )
        messages.success(request, sms_msg)
        UserLog.objects.create(processed_by=request.user,logs_action='Deposit Share AC',description=f'Account Number: {customer.account_no}, TrxID: {trx.VoucherID}')
        UserLog.objects.create(processed_by=request.user,action=f'Deposit Share AC',amount=amount, customer=customer)

        return redirect('share_list')

    return render(request, 'app1/share/share_deposit.html', {'share_ac': share_ac, 'customer': customer})


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_withdraw(request, share_id):
    share_ac = get_object_or_404(ShareAC, share_id=share_id)
    customer = share_ac.customer

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        processed_by = request.user

        share_ac.balance -= Decimal(amount)
        share_ac.withdraw += Decimal(amount)
        share_ac.save()

        share_trx = ShareACTransactionHistory.objects.create(
            share_ac=share_ac,
            transaction_type='withdraw',
            Amount=Decimal(amount),
            processed_by=processed_by,
            note=note,
            balance=share_ac.balance,
        )
        sms_msg = send_sms(
            number=share_ac.customer.mobile_number,
            title='Withdraw Share AC',
            user=request.user,
            amount=amount,
            balance=share_ac.balance,
            account_number=share_ac.customer.account_no,
        )
        messages.success(request, sms_msg)
        UserLog.objects.create(processed_by=request.user,logs_action='Withdraw Share AC',description=f'Account Number: {customer.account_no}, TrxID: {share_trx.VoucherID}')
        UserLog.objects.create(processed_by=request.user,action=f'Withdraw Share AC',amount=amount, customer=customer, trx=True)

        return redirect('share_list')

    return render(request, 'app1/share/share_withdraw.html', {'share_ac': share_ac, 'customer': customer})


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_profit_withdraw(request, share_id):
    share_ac = get_object_or_404(ShareAC, share_id=share_id)
    customer = share_ac.customer

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        note = f'{note} Profit Withdraw'
        processed_by = request.user

        # share_ac.balance -= Decimal(amount)
        share_ac.profit_withdraw += Decimal(amount)
        share_ac.save()

        share_trx = ShareACTransactionHistory.objects.create(
            share_ac=share_ac,
            transaction_type='withdraw',
            Amount=Decimal(amount),
            processed_by=processed_by,
            note=note,
            balance=share_ac.balance,
        )
        sms_msg = send_sms(
            number=share_ac.customer.mobile_number,
            title='Profit Withdraw Share AC',
            user=request.user,
            amount=amount,
            balance=share_ac.profit_balance,
            account_number=share_ac.customer.account_no,
        )
        messages.success(request, sms_msg)
        UserLog.objects.create(processed_by=request.user,logs_action='Profit Withdraw Share AC',description=f'Account Number: {customer.account_no}, TrxID: {share_trx.VoucherID}')
        UserLog.objects.create(processed_by=request.user,action=f'Profit Withdraw Share AC',amount=amount, customer=customer, trx=True)

        return redirect('share_list')

    return render(request, 'app1/share/share_profit_withdraw.html', {'share_ac': share_ac, 'customer': customer})


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_transfer(request, share_id):
    share_ac = get_object_or_404(ShareAC, share_id=share_id)
    customer = share_ac.customer
    prev_customer = customer
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        nominee = request.POST.get('nominee')
        customer = get_object_or_404(Customer, account_no=account_no)

        share_ac.customer = customer
        share_ac.nominee = nominee
        share_ac.save()

        UserLog.objects.create(processed_by=request.user,logs_action='Transfer Share AC',description=f'Share ID: {share_ac.share_id}, From:{prev_customer.account_no}, To: {share_ac.customer.account_no}')

        return redirect('share_list')

    return render(request, 'app1/share/share_transfer.html', {'share_ac': share_ac, 'customer': customer})


@login_required
@permission_required('app1.view_shareactransactionhistory', raise_exception=True)
def share_transaction_history(request, share_id):
    share_ac = ShareAC.objects.get(share_id=share_id)
    transactions = share_ac.share_ac_transaction_history.all().order_by('-created_at')
    return render(request, 'app1/share/share_transactions.html', {'data': share_ac, 'transactions': transactions})


@login_required
@permission_required('app1.view_shareac', raise_exception=True)
def share_search(request):
    return render(request, 'app1/share/share_search.html')


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_create(request, account_no):
    try:
        customer = Customer.objects.get(account_no=account_no)

        if request.method == 'POST':
            balance = request.POST.get('balance')
            nominee = request.POST.get('nominee')
            note = request.POST.get('note')

            share = ShareAC(
                customer=customer,
                balance=balance,
                nominee=nominee,
            )
            share.save()

            messages.success(request, f"Share Account created successfully.")

            trx = ShareACTransactionHistory.objects.create(
                share_ac=share,
                transaction_type='deposit',
                Amount=Decimal(balance),
                processed_by=request.user,
                note=note,
                balance=share.balance,
            )

            sms_msg = send_sms(
                number=customer.mobile_number,
                title='Add Share AC',
                user=request.user,
            )
            messages.success(request, sms_msg)
            UserLog.objects.create(processed_by=request.user,logs_action='Add Share AC',description=f'Account Number: {customer.account_no}')
            UserLog.objects.create(processed_by=request.user,action=f'Share AC Previous Balance',amount=balance, customer=customer)
            return redirect('share_list')

        context = {'customer': customer}
        return render(request, 'app1/share/share_create.html', context)
    
    except Customer.DoesNotExist:
        messages.error(request, f"No customer found with account number: {account_no}")
        return redirect('share_search')


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_deposit_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            share_ac = ShareAC.objects.get(customer__account_no=account_no)
            return redirect('share_deposit', share_ac.share_id)
        except ShareAC.DoesNotExist:
            context = {'error': f'No share account found with account number: {account_no}'}
            return render(request, 'app1/share/share_deposit_search.html', context)
    return render(request, 'app1/share/share_deposit_search.html')


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_withdraw_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            share_ac = ShareAC.objects.get(customer__account_no=account_no)
            return redirect('share_withdraw', share_ac.share_id)
        except ShareAC.DoesNotExist:
            context = {'error': f'No share account found with account number: {account_no}'}
            return render(request, 'app1/share/share_deposit_search.html', context)
    return render(request, 'app1/share/share_deposit_search.html')


@login_required
@permission_required('app1.add_shareac', raise_exception=True)
def share_profit_withdraw_search(request):
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        try:
            share_ac = ShareAC.objects.get(customer__account_no=account_no)
            return redirect('share_profit_withdraw', share_ac.share_id)
        except ShareAC.DoesNotExist:
            context = {'error': f'No share account found with account number: {account_no}'}
            return render(request, 'app1/share/share_deposit_search.html', context)
    return render(request, 'app1/share/share_deposit_search.html')



# ShareAC
################################################################


@login_required
@permission_required('app1.add_banktransaction', raise_exception=True)
def bank_withdraw(request):
    if request.method == 'POST':
        form = BankWithdrawForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.processed_by = request.user
            transaction.save()

            bank = transaction.bank
            bank.balance -= transaction.withdraw_amount
            bank.save()

            UserLog.objects.create(processed_by=request.user,logs_action='Bank Withdraw',description=f'Bank: {bank.bank_name}, TrxID: {transaction.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Bank Withdraw',amount=transaction.withdraw_amount)

            return redirect('bank_withdraw')
    else:
        form = BankWithdrawForm(request=request)

    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    bank_transactions = BankTransaction.objects.filter(bank__branch=active_branch.branch).order_by('-id')


    return render(request, 'app1/bank_withdraw.html', {'form': form, 'bank_transactions': bank_transactions})


@login_required
@permission_required('app1.add_banktransaction', raise_exception=True)
def bank_deposit(request):
    if request.method == 'POST':
        form = BankDepositForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.processed_by = request.user
            transaction.save()

            bank = transaction.bank
            bank.balance += transaction.deposit_amount
            bank.save()

            
            UserLog.objects.create(processed_by=request.user,logs_action='Bank Deposit',description=f'Bank: {bank.bank_name}, TrxID: {transaction.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Bank Deposit',amount=transaction.deposit_amount, trx=True)

            return redirect('bank_deposit')
    else:
        form = BankDepositForm(request=request)

    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    bank_transactions = BankTransaction.objects.filter(bank__branch=active_branch.branch).order_by('-id')


    return render(request, 'app1/bank_deposit.html', {'form': form, 'bank_transactions': bank_transactions})


################################################################
# Delete

@login_required
@permission_required('app1.delete_customer', raise_exception=True)
def delete_search(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()

        if customer:
            loan = LoanAC.objects.filter(customer=customer)
            loan_cc = Loan_CC.objects.filter(customer=customer)
            loan_sp = Loan_Special.objects.filter(customer=customer)
            dps = DPS.objects.filter(customer=customer)
            fdr = FDR.objects.filter(customer=customer)
            share = ShareAC.objects.filter(customer=customer)

            context={
                'loans': loan,
                'loan_ccs': loan_cc,
                'loan_sps': loan_sp,
                'dpss': dps,
                'fdrs': fdr,
                'shares': share,
                'customer': customer,
            }
            # return render(request, 'app1/delete_search_results.html', context)
            return render(request, 'app1/dsr.html', context)

        else:
            return render(request, 'app1/delete_search.html', {'error': 'No customer found with this account number in the current branch.'})
    return render(request, 'app1/delete_search.html')


@login_required
@permission_required('app1.delete_customer', raise_exception=True)
def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('customer_list')


@login_required
@permission_required('app1.delete_loanac', raise_exception=True)
def loan_delete(request, id):
    loan = get_object_or_404(LoanAC, id=id)
    UserLog.objects.filter(loan=loan).delete()
    loan.delete()
    return redirect('delete_search')


@login_required
@permission_required('app1.delete_loan_cc', raise_exception=True)
def loan_cc_delete(request, id):
    loan_cc = get_object_or_404(Loan_CC, id=id)
    loan_cc.delete()
    return redirect('delete_search')


@login_required
@permission_required('app1.delete_loan_special', raise_exception=True)
def loan_sp_delete(request, id):
    loan_sp = get_object_or_404(Loan_Special, id=id)
    loan_sp.delete()
    return redirect('delete_search')


@login_required
@permission_required('app1.delete_dps', raise_exception=True)
def fdr_delete(request, id):
    fdr = get_object_or_404(FDR, id=id)
    fdr.delete()
    return redirect('delete_search')


@login_required
@permission_required('app1.delete_dps', raise_exception=True)
def dps_delete(request, id):
    dps = get_object_or_404(DPS, id=id)
    dps.delete()
    return redirect('delete_search')


@login_required
@permission_required('app1.delete_shareac', raise_exception=True)
def share_delete(request, share_id):
    share = get_object_or_404(ShareAC, share_id=share_id)
    share.delete()
    return redirect('delete_search')



# Delete
################################################################

from django.db import transaction
from django.http import JsonResponse

@login_required
@csrf_exempt
def update_active_branch(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        branch_id = data.get('branch_id')

        if branch_id:
            branch = Branch.objects.filter(id=branch_id).first()
            if not branch:
                return JsonResponse({'status': 'error', 'message': 'Invalid branch ID'}, status=400)

            try:
                with transaction.atomic():
                    active_branch, created = ActiveBranch.objects.get_or_create(user=request.user)
                    active_branch.branch = branch
                    active_branch.save()

                return JsonResponse({'status': 'success'})
            except Exception as e:
                print(f"Error updating active branch: {e}")
                return JsonResponse({'status': 'error', 'message': 'Failed to update active branch'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required
def set_language(request):
    language = request.POST.get('language', 'en')
    request.session['language'] = language
    return redirect('/')



