from datetime import date, datetime, timedelta  # Import only date from datetime, remove timezone
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.utils import timezone  # Correct import from Django
from primary_setup.models import CustomUser, Director, OutLoan, Somity, VoucherCategory
from app1.models import DPS, FDR, ActiveBranch, Customer, DPSTransactionHistory, FDRTransactionHistory, GeneralAC, GeneralTransactionHistory, Loan_CC, Loan_CC_Collection, LoanAC, LoanCollection, SavingsAC, SavingsTransactionHistory, ShareAC, ShareACTransactionHistory
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Count
from django.utils.translation import gettext_lazy as _
from otrans.models import Expense, Income, SSM_Deposit


@login_required
@permission_required('app1.view_generalac')
def today_dashboard(request, start_date=None, end_date=None):

    branch = ActiveBranch.objects.get(user=request.user).branch
    today = timezone.now().date()

    if start_date is None or end_date is None:
        start_date = today
        end_date = today
        dashboard = _("Today")
        dashboard1 = "Today"
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        dashboard = _("Monthly")
        dashboard1 = "Monthly"


    transactions = GeneralTransactionHistory.objects.filter(
        general__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    general_savings_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    general_savings_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = SavingsTransactionHistory.objects.filter(
        general__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    speical_savings_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    special_savings_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = LoanCollection.objects.filter(
        loan__customer__branch=branch,
        Date__range=(start_date, end_date),
    )
    installments_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    installments_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = Loan_CC_Collection.objects.filter(
        loan_cc__customer__branch=branch,
        Date__range=(start_date, end_date),
    )
    cc_loan_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    cc_loan_transaction = transactions.aggregate(Count('id'))['id__count'] or 0
    
    transactions = DPSTransactionHistory.objects.filter(
        dps__customer__branch=branch,
        date__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    dps_collection = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    dps_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = FDRTransactionHistory.objects.filter(
        fdr__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    fdr_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    fdr_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = ShareACTransactionHistory.objects.filter(
        share_ac__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    share_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    share_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = Customer.objects.filter(
        branch=branch,
        joining_date__range=(start_date, end_date),
    )
    admission_fee_collection = transactions.aggregate(Sum('admission_fee'))['admission_fee__sum'] or 0
    admission_fee_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = GeneralTransactionHistory.objects.filter(
        general__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='withdraw'
    )
    savings_withdraw_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    savings_withdraw_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = DPSTransactionHistory.objects.filter(
        dps__customer__branch=branch,
        date__date__range=(start_date, end_date),
        transaction_type='withdraw'
    )
    dps_withdraw_collection = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    dps_withdraw_transaction = transactions.aggregate(Count('id'))['id__count'] or 0

    transactions = FDRTransactionHistory.objects.filter(
        fdr__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='withdraw'
    )
    fdr_withdraw_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    fdr_withdraw_transaction = transactions.aggregate(Count('id'))['id__count'] or 0    

    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')

    context = {
        'general_savings_collection': general_savings_collection,
        'general_savings_transaction': general_savings_transaction,
        'speical_savings_collection': speical_savings_collection,
        'special_savings_transaction': special_savings_transaction,
        'installments_collection': installments_collection,
        'installments_transaction': installments_transaction,
        'cc_loan_collection': cc_loan_collection,
        'cc_loan_transaction': cc_loan_transaction,
        'dps_collection': dps_collection,
        'dps_transaction': dps_transaction,
        'fdr_collection': fdr_collection,
        'fdr_transaction': fdr_transaction,
        'share_collection': share_collection,
        'share_transaction': share_transaction,
        'admission_fee_collection': admission_fee_collection,
        'admission_fee_transaction': admission_fee_transaction,
        'savings_withdraw_collection': savings_withdraw_collection,
        'savings_withdraw_transaction': savings_withdraw_transaction,
        'dps_withdraw_collection': dps_withdraw_collection,
        'dps_withdraw_transaction': dps_withdraw_transaction,
        'fdr_withdraw_collection': fdr_withdraw_collection,
        'fdr_withdraw_transaction': fdr_withdraw_transaction,
        # 'start_date': start_date,
        # 'end_date': end_date,
        'start_date': formatted_start_date,  # Pass the formatted date
        'end_date': formatted_end_date,  
        'dashboard': dashboard,
        'dashboard1': dashboard1,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@permission_required('app1.view_generalac')
def monthly_dashboard(request):
    today = timezone.now().date()

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    print(start_date_str)

    if start_date_str and end_date_str:
        # Convert string to date objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        # Default to the current month's start and end dates
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)

    # Convert dates to strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    print(start_date_str)

    return redirect('today_dashboard', start_date=start_date_str, end_date=end_date_str)



@login_required
@permission_required('app1.view_generaltransactionhistory')
def general_savings_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = GeneralTransactionHistory.objects.filter(
        general__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'General Savings Collection',
    }
    return render(request, 'dashboard/general_savings_collection_print.html', context)

@login_required
@permission_required('app1.view_savingstransactionhistory')
def special_savings_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = SavingsTransactionHistory.objects.filter(
        general__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'Special Savings Collection',
    }
    return render(request, 'dashboard/general_savings_collection_print.html', context)

@login_required
@permission_required('app1.view_loanac')
def installments_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = LoanCollection.objects.filter(
        loan__customer__branch=branch,
        Date__range=(start_date, end_date),
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    total_profit = transactions.aggregate(Sum('profit'))['profit__sum'] or 0
    total_principal = transactions.aggregate(Sum('principal'))['principal__sum'] or 0
    total_fine = transactions.aggregate(Sum('fine'))['fine__sum'] or 0
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'Installments Collection',
        'total_profit': total_profit,
        'total_principal': total_principal,
        'total_fine': total_fine,
    }
    return render(request, 'dashboard/installments_collection_print.html', context)

@login_required
@permission_required('app1.view_loan_cc')
def cc_loan_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = Loan_CC_Collection.objects.filter(
        loan_cc__customer__branch=branch,
        Date__range=(start_date, end_date),
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    # total_fine = transactions.aggregate(Sum('fine'))['fine__sum'] or 0
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'CC Loan Collection',
        # 'total_fine': total_fine,
    }
    return render(request, 'dashboard/cc_loan_collection_print.html', context)

@login_required
def dps_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = DPSTransactionHistory.objects.filter(
        dps__customer__branch=branch,
        date__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    total_collection = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    total_fine = transactions.aggregate(Sum('fine'))['fine__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'DPS Collection',
        'total_fine': total_fine,
    }
    return render(request, 'dashboard/dps_collection_print.html', context)

@login_required
def fdr_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = FDRTransactionHistory.objects.filter(
        fdr__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'FDR Collection',
    }
    return render(request, 'dashboard/fdr_collection_print.html', context)

@login_required
def share_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    start_date = timezone.datetime.strptime(start_date, '%b. %d, %Y').date()
    end_date = timezone.datetime.strptime(end_date, '%b. %d, %Y').date()
 
    transactions = ShareACTransactionHistory.objects.filter(
        share_ac__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='deposit'
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'Share Collection',
    }
    return render(request, 'dashboard/share_collection_print.html', context)

@login_required
def savings_withdraw_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = GeneralTransactionHistory.objects.filter(
        general__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='withdraw'
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'Savings Withdrawal',
    }
    return render(request, 'dashboard/general_savings_collection_print.html', context)

@login_required
def dps_withdraw_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    transactions = DPSTransactionHistory.objects.filter(
        dps__customer__branch=branch,
        date__date__range=(start_date, end_date),
        transaction_type='withdraw'
    )
    total_collection = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    total_fine = transactions.aggregate(Sum('fine'))['fine__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'DPS Withdrawal',
        'total_fine': total_fine,
    }
    return render(request, 'dashboard/dps_collection_print.html', context)

@login_required
def fdr_withdraw_collection(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
 
    transactions = FDRTransactionHistory.objects.filter(
        fdr__customer__branch=branch,
        created_at__date__range=(start_date, end_date),
        transaction_type='withdraw'
    )
    total_collection = transactions.aggregate(Sum('Amount'))['Amount__sum'] or 0
    
    context = {
        'total_collection': total_collection,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'branch': branch,
        'title': 'FDR Withdrawal',
    }
    return render(request, 'dashboard/fdr_collection_print.html', context)

@login_required
def dashboard(request):
    branch = ActiveBranch.objects.get(user=request.user).branch

    total_general_savings = GeneralAC.objects.filter(customer__branch=branch).aggregate(Sum('balance'))['balance__sum'] or 0
    total_special_savings = SavingsAC.objects.filter(customer__branch=branch).aggregate(Sum('balance'))['balance__sum'] or 0
    total_dps_balance = DPS.objects.filter(customer__branch=branch).aggregate(Sum('balance'))['balance__sum'] or 0
    total_loan_balance = LoanAC.objects.filter(customer__branch=branch).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    total_loan_profit = LoanAC.objects.filter(customer__branch=branch).aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0
    total_cc_loan_amount = Loan_CC.objects.filter(customer__branch=branch).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    total_fdr_deposit = FDR.objects.filter(customer__branch=branch).aggregate(Sum('balance_amount'))['balance_amount__sum'] or 0
    total_fdr_profit = FDR.objects.filter(customer__branch=branch).aggregate(Sum('paid_profit'))['paid_profit__sum'] or 0
    total_dps_profit = DPS.objects.filter(customer__branch=branch).aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0
    total_share_balance = ShareAC.objects.filter(customer__branch=branch).aggregate(Sum('balance'))['balance__sum'] or 0
    total_share_profit = ShareAC.objects.filter(customer__branch=branch).aggregate(Sum('profit_balance'))['profit_balance__sum'] or 0

    voucher_category_count = VoucherCategory.objects.filter(branch=branch).count()
    total_income_amount = Income.objects.filter(branch=branch).aggregate(Sum('Amount'))['Amount__sum'] or 0
    total_expense_amount = Expense.objects.filter(branch=branch).aggregate(Sum('Amount'))['Amount__sum'] or 0

    total_customers = Customer.objects.filter(branch=branch).count()
    daily_customers = Customer.objects.filter(branch=branch, customer_type='daily').count()
    weekly_customers = Customer.objects.filter(branch=branch, customer_type='weekly').count()
    monthly_customers = Customer.objects.filter(branch=branch, customer_type='monthly').count()
    male_customers = Customer.objects.filter(branch=branch, gender='Male').count()
    female_customers = Customer.objects.filter(branch=branch, gender='Female').count()
    inactive_customers = Customer.objects.filter(branch=branch, status='Inactive').count()

    total_somity = Somity.objects.filter(branch=branch).count()
    total_staff = CustomUser.objects.filter(branch=branch).count()

    total_general_ac = GeneralAC.objects.filter(customer__branch=branch).count()
    total_dps = DPS.objects.filter(branch=branch).count()
    total_loan_ac = LoanAC.objects.filter(branch=branch).count()
    total_loan_cc = Loan_CC.objects.filter(branch=branch).count()
    total_fdr = FDR.objects.filter(customer__branch=branch).count()

    total_director = Director.objects.filter(branch=branch).count()
    total_director_balance = Director.objects.filter(branch=branch).aggregate(Sum('balance'))['balance__sum'] or 0

    total_outloan = OutLoan.objects.filter(branch=branch).count()
    total_OutLoan_balance = OutLoan.objects.filter(branch=branch).aggregate(Sum('balance'))['balance__sum'] or 0
    total_ssm_amount = SSM_Deposit.objects.filter(branch=branch).aggregate(Sum('Amount'))['Amount__sum'] or 0

    context = {
        'total_general_savings': total_general_savings,
        'total_special_savings': total_special_savings,
        'total_dps_balance': total_dps_balance,
        'total_loan_balance': total_loan_balance,
        'total_loan_profit': total_loan_profit,
        'total_cc_loan_amount': total_cc_loan_amount,
        'total_fdr_deposit': total_fdr_deposit,
        'total_fdr_profit': total_fdr_profit,
        'total_dps_profit': total_dps_profit,
        'total_share_balance': total_share_balance,
        'total_share_profit': total_share_profit,
        'voucher_category_count': voucher_category_count,
        'total_income_amount': total_income_amount,
        'total_expense_amount': total_expense_amount,
        'total_customers': total_customers,
        'daily_customers': daily_customers,
        'weekly_customers': weekly_customers,
        'monthly_customers': monthly_customers,
        'male_customers': male_customers,
        'female_customers': female_customers,
        'inactive_customers': inactive_customers,
        'total_somity': total_somity,
        'total_staff': total_staff,
        'total_general_ac': total_general_ac,
        'total_dps': total_dps,
        'total_loan_ac': total_loan_ac,
        'total_loan_cc': total_loan_cc,
        'total_fdr': total_fdr,
        'total_director': total_director,
        'total_director_balance': total_director_balance,
        'total_outloan': total_outloan,
        'total_OutLoan_balance': total_OutLoan_balance,
        'total_ssm_amount': total_ssm_amount,
    }

    return render(request, 'dashboard/dashboard_all.html', context)


