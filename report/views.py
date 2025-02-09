from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from app1.models import DPS, FDR, ActiveBranch, DPSTransactionHistory, FDRTransactionHistory, GeneralAC, GeneralDeposit, GeneralTransactionHistory, Loan_CC, Loan_CC_Collection, Loan_Special, LoanAC, Customer, LoanCollection, LoanFine, SavingsAC, SavingsDeposit, SavingsTransactionHistory, ShareAC, ShareACTransactionHistory
from otrans.models import Expense, Income
from report.models import UserLog
from .forms import AccountStatementForm, DPSReportForm, GeneralLedgerForm, GroupSelectionForm, GroupSchemeSelectionForm, CustomerSearchForm, FixedDepositReportForm, LoanOCReportForm, MonthWiseTopSheetForm, ProfitLossReportForm, ReceivePaymentReportForm, ReportForm, ShareReportForm, UESReportForm, UWESReportForm, VoucherReportForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from app1.models import BankTransaction, ActiveBranch
from primary_setup.models import Bank, CustomUser, Director, OutLoan
from datetime import datetime
from calendar import monthrange
from datetime import datetime




@login_required
def daily_loan_report(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    group_form = GroupSelectionForm(branch=branch)
    loans = []
    total_loan_amount = total_profit_taka = total_total_amount = total_paid_amount = total_due = total_installment_amount = 0.0

    if request.method == 'POST':
        group_form = GroupSelectionForm(request.POST, branch=branch)
        if group_form.is_valid():
            selected_groups = group_form.cleaned_data['group']
            customers = Customer.objects.filter(group__in=selected_groups)
            loans = LoanAC.objects.filter(loan_scheme='daily', customer__in=customers, branch=branch)

            # Calculate the totals as floats
            total_loan_amount = float(loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0.0)
            total_profit_taka = float(loans.aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0.0)
            total_total_amount = float(loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.0)
            total_paid_amount = float(loans.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0)
            total_installment_amount = float(loans.aggregate(Sum('installment_amount'))['installment_amount__sum'] or 0.0)

            # Calculate the total due amount manually since it's not a field in the model
            total_due = sum(float(loan.total_amount) - float(loan.paid_amount) for loan in loans)


    return render(request, 'report/loan_report_daily.html', {
        'branch': branch,
        'report_date': date.today(),
        'group_form': group_form,
        'loans': loans,
        'total_loan_amount': total_loan_amount,
        'total_profit_taka': total_profit_taka,
        'total_total_amount': total_total_amount,
        'total_paid_amount': total_paid_amount,
        'total_due': total_due,
        'total_installment_amount': total_installment_amount,
    })

@login_required
def weekly_loan_report(request):
    branch = ActiveBranch.objects.filter(user=request.user).first().branch
    group_form = GroupSelectionForm(branch=branch)
    loans = []
    total_loan_amount = total_profit_taka = total_total_amount = total_paid_amount = total_due = total_installment_amount = 0.0

    if request.method == 'POST':
        group_form = GroupSelectionForm(request.POST, branch=branch)
        if group_form.is_valid():
            selected_groups = group_form.cleaned_data['group']
            loans = LoanAC.objects.filter(loan_scheme='weekly', customer__group__in=selected_groups, branch=branch)

            # Calculate the totals as floats
            total_loan_amount = float(loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0.0)
            total_profit_taka = float(loans.aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0.0)
            total_total_amount = float(loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.0)
            total_paid_amount = float(loans.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0)
            total_installment_amount = float(loans.aggregate(Sum('installment_amount'))['installment_amount__sum'] or 0.0)

            # Calculate the total due amount manually since it's not a field in the model
            total_due = sum(float(loan.total_amount) - float(loan.paid_amount) for loan in loans)

    return render(request, 'report/loan_report_weekly.html', {
        'branch': branch,
        'report_date': date.today(),
        'group_form': group_form,
        'loans': loans,
        'total_loan_amount': total_loan_amount,
        'total_profit_taka': total_profit_taka,
        'total_total_amount': total_total_amount,
        'total_paid_amount': total_paid_amount,
        'total_due': total_due,
        'total_installment_amount': total_installment_amount,
    })

@login_required
def monthly_loan_report(request):
    branch = ActiveBranch.objects.filter(user=request.user).first().branch
    group_form = GroupSelectionForm(branch=branch)
    loans = []
    total_loan_amount = total_profit_taka = total_total_amount = total_paid_amount = total_due = total_installment_amount = 0.0

    if request.method == 'POST':
        group_form = GroupSelectionForm(request.POST, branch=branch)
        if group_form.is_valid():
            selected_groups = group_form.cleaned_data['group']
            loans = LoanAC.objects.filter(loan_scheme='monthly', customer__group__in=selected_groups, branch=branch)

            # Calculate the totals as floats
            total_loan_amount = float(loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0.0)
            total_profit_taka = float(loans.aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0.0)
            total_total_amount = float(loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.0)
            total_paid_amount = float(loans.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0)
            total_installment_amount = float(loans.aggregate(Sum('installment_amount'))['installment_amount__sum'] or 0.0)

            # Calculate the total due amount manually since it's not a field in the model
            total_due = sum(float(loan.total_amount) - float(loan.paid_amount) for loan in loans)

    return render(request, 'report/loan_report_monthly.html', {
        'branch': branch,
        'report_date': date.today(),
        'group_form': group_form,
        'loans': loans,
        'total_loan_amount': total_loan_amount,
        'total_profit_taka': total_profit_taka,
        'total_total_amount': total_total_amount,
        'total_paid_amount': total_paid_amount,
        'total_due': total_due,
        'total_installment_amount': total_installment_amount,
    })

@login_required
def loan_due_list(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    form = GroupSchemeSelectionForm(branch=branch)
    loans = []
    total_loan_amount = total_profit_taka = total_total_amount = total_paid_amount = total_due = total_over_due = 0.0

    if request.method == 'POST':
        form = GroupSchemeSelectionForm(request.POST, branch=branch)
        if form.is_valid():
            selected_groups = form.cleaned_data['group']
            selected_scheme = form.cleaned_data['scheme']
            customers = Customer.objects.filter(group__in=selected_groups)
            loans = LoanAC.objects.filter(
                loan_scheme=selected_scheme, 
                customer__in=customers, 
                branch=branch,
            )       
            for loan in loans:
                loan.over_due = loan.missed_installments * loan.installment_amount

                        # Calculate the totals as floats
            total_loan_amount = float(loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0.0)
            total_profit_taka = float(loans.aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0.0)
            total_total_amount = float(loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.0)
            total_paid_amount = float(loans.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0)
            # total_installment_amount = float(loans.aggregate(Sum('installment_amount'))['installment_amount__sum'] or 0.0)

            # Calculate the total due amount manually since it's not a field in the model
            total_due = sum(float(loan.total_amount) - float(loan.paid_amount) for loan in loans)
            total_over_due = sum(float(loan.missed_installments) * float(loan.installment_amount) for loan in loans)

    return render(request, 'report/loan_due_list.html', {
        'branch': branch,
        'report_date': date.today(),
        'form': form,
        'loans': loans,
        'total_loan_amount': total_loan_amount,
        'total_profit_taka': total_profit_taka,
        'total_total_amount': total_total_amount,
        'total_paid_amount': total_paid_amount,
        'total_due': total_due,
        'total_over_due': total_over_due,
        # 'total_installment_amount': total_installment_amount,
    })

@login_required
def loan_recovery_percentage(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    form = GroupSchemeSelectionForm(branch=branch)
    loans = []
    total_loan_amount = total_profit_taka = total_total_amount = total_paid_amount = total_due = total_over_due = 0.0
    total_paid_percentage = total_due_percentage = 0.0

    if request.method == 'POST':
        form = GroupSchemeSelectionForm(request.POST, branch=branch)
        if form.is_valid():
            selected_groups = form.cleaned_data['group']
            selected_scheme = form.cleaned_data['scheme']
            customers = Customer.objects.filter(group__in=selected_groups)
            loans = LoanAC.objects.filter(
                loan_scheme=selected_scheme, 
                customer__in=customers, 
                branch=branch,
            )       
            for loan in loans:
                loan.total_paid_percentage = (loan.paid_amount * 100)/loan.total_amount
                loan.total_due_percentage = (loan.due * 100)/loan.total_amount

            # Calculate the totals as floats
            total_loan_amount = float(loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0.0)
            total_profit_taka = float(loans.aggregate(Sum('profit_taka'))['profit_taka__sum'] or 0.0)
            total_total_amount = float(loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.0)
            total_paid_amount = float(loans.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0)

            # Calculate the total due amount manually since it's not a field in the model
            total_due = sum(float(loan.total_amount) - float(loan.paid_amount) for loan in loans)

            
            if total_total_amount == 0:
                total_paid_percentage = 0.0
                total_due_percentage = 0.0
            else:
                total_paid_percentage = (total_paid_amount * 100) / total_total_amount
                total_due_percentage = (total_due * 100) / total_total_amount

    return render(request, 'report/loan_recovery_percentage.html', {
        'branch': branch,
        'report_date': date.today(),
        'form': form,
        'loans': loans,
        'total_loan_amount': total_loan_amount,
        'total_profit_taka': total_profit_taka,
        'total_total_amount': total_total_amount,
        'total_paid_amount': total_paid_amount,
        'total_due': total_due,
        'total_paid_percentage': total_paid_percentage,
        'total_due_percentage': total_due_percentage,
    })

@login_required
def customer_report(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    form = CustomerSearchForm(branch=branch)
    customers = []

    if request.method == 'POST':
        form = CustomerSearchForm(request.POST, branch=branch)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            selected_somity = form.cleaned_data['somity']
            
            customers = Customer.objects.filter(
                joining_date__range=[start_date, end_date],
                group__in=selected_somity
            )

    return render(request, 'report/customer_report.html', {
        'branch': branch,
        'form': form,
        'customers': customers,
    })

@login_required
def customer_balance(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()

    if request.method == 'POST':
        account_no = request.POST.get('account_no')
        
        customer = Customer.objects.filter(account_no=account_no, branch=active_branch.branch).first()

        if customer:
            # Fetch related accounts
            loan = LoanAC.objects.filter(customer=customer)
            loan_cc = Loan_CC.objects.filter(customer=customer)
            loan_sp = Loan_Special.objects.filter(customer=customer)
            dps = DPS.objects.filter(customer=customer)
            fdr = FDR.objects.filter(customer=customer)
            share = ShareAC.objects.filter(customer=customer)
            generalAC = get_object_or_404(GeneralAC, customer=customer)
            savingsAC = get_object_or_404(SavingsAC, customer=customer)

            # Calculate balances
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
                'special_savings': special_savings
            }
            return render(request, 'report/customer_balance.html', context)

        else:
            return render(request, 'report/search.html', {'error': 'No customer found with this account number in the current branch.'})

    return render(request, 'report/search.html')

@login_required
def bank_transactions(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        bank_id = request.POST.get('bank')
        active_branch = ActiveBranch.objects.get(user=request.user)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'report/transaction.html', {'error': 'Invalid date format'})

        if bank_id == 'all':
            transactions = BankTransaction.objects.filter(
                date__gte=start_date,
                date__lte=end_date,
                bank__branch=active_branch.branch
            )
            bank = None
        else:
            try:
                bank = Bank.objects.get(id=bank_id, branch=active_branch.branch)
                transactions = BankTransaction.objects.filter(
                    date__gte=start_date,
                    date__lte=end_date,
                    bank=bank
                )
            except Bank.DoesNotExist:
                return render(request, 'report/transaction.html', {'error': 'Invalid bank selection'})

        banks = Bank.objects.filter(branch=active_branch.branch)
        report_date = datetime.now().strftime('%Y-%m-%d')
        return render(request, 'report/transaction.html', {'transactions': transactions, 'banks': banks, 'branch': active_branch.branch, 'bank': bank, 'report_date': report_date, 'start_date': start_date, 'end_date': end_date})
    else:
        active_branch = ActiveBranch.objects.get(user=request.user)
        banks = Bank.objects.filter(branch=active_branch.branch)
        report_date = datetime.now().strftime('%Y-%m-%d')
        return render(request, 'report/transaction.html', {'banks': banks, 'branch': active_branch.branch, 'bank': None, 'report_date': report_date, 'start_date': None, 'end_date': None})




@login_required
def fixed_deposit_report(request):
    fdrs = None
    total_opening_amount = 0
    total_paid_profit = 0
    total_monthly_profit_taka = 0
    total_payable = 0

    if request.method == 'POST':
        form = FixedDepositReportForm(request.POST, user=request.user)
        if form.is_valid():
            # Retrieve the filter criteria from the form
            somities = form.cleaned_data['somity']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            scheme_name = form.cleaned_data['scheme_name']
            status = form.cleaned_data['status']
            account_number = form.cleaned_data['account_number']

            # Filter the FDR model based on the criteria
            fdrs = FDR.objects.all()

            if somities:
                fdrs = fdrs.filter(customer__group__in=somities)

            if start_date and end_date:
                fdrs = fdrs.filter(start_date__gte=start_date, start_date__lte=end_date)

            if scheme_name:
                fdrs = fdrs.filter(scheme__scheme_name=scheme_name)

            if status and status != 'all':
                fdrs = fdrs.filter(status=status)

            if account_number:
                fdrs = fdrs.filter(customer__account_no=account_number)

            totals = fdrs.aggregate(
                total_opening_amount=Sum('opening_amount'),
                total_paid_profit=Sum('paid_profit'),
                total_monthly_profit_taka=Sum('monthly_profit_taka'),
                total_payable=Sum(
                    ExpressionWrapper(
                        F('monthly_profit_taka') - F('paid_profit'),
                        output_field=DecimalField()
                    )
                )
            )

            branch = ActiveBranch.objects.get(user=request.user).branch

            return render(request, 'report/fdr_print.html', {'fdrs': fdrs, 'branch': branch, 'totals': totals})
    else:
        form = FixedDepositReportForm(user=request.user)

    return render(request, 'report/fdr.html', {'form': form})

@login_required
def dps_report(request):
    dpss = None
    total_amount_per_installments = total_total_amount = total_balance = 0
    total_profit_taka = total_due = 0

    if request.method == 'POST':
        form = DPSReportForm(request.POST, user=request.user)
        if form.is_valid():
            # Retrieve the filter criteria from the form
            somities = form.cleaned_data['somity']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            scheme_name = form.cleaned_data['scheme_name']
            status = form.cleaned_data['status']
            account_number = form.cleaned_data['account_number']

            # Filter the FDR model based on the criteria
            dpss = DPS.objects.all()

            if somities:
                dpss = dpss.filter(customer__group__in=somities)

            if start_date and end_date:
                dpss = dpss.filter(created_date__gte=start_date, created_date__lte=end_date)

            if scheme_name:
                dpss = dpss.filter(scheme__scheme_name=scheme_name)

            if status and status != 'all':
                dpss = dpss.filter(status=status)

            if account_number:
                dpss = dpss.filter(customer__account_no=account_number)

            totals = dpss.aggregate(
                total_amount_per_installments=Sum('amount_per_installments'),
                total_total_amount=Sum('total_amount'),
                total_balance=Sum('balance'),
                total_profit_taka=Sum('profit_taka'),
                total_due=Sum(
                    ExpressionWrapper(
                        F('total_amount') - F('balance'),
                        output_field=DecimalField()
                    )
                )
            )

            branch = ActiveBranch.objects.get(user=request.user).branch

            return render(request, 'report/dps_print.html', {'dpss': dpss, 'branch': branch, 'totals': totals})
    else:
        form = DPSReportForm(user=request.user)

    return render(request, 'report/dps.html', {'form': form})

@login_required
def share_report(request):
    share_ac = None
    total_balance = total_profit_balance = 0
    if request.method == 'POST':
        form = ShareReportForm(request.POST, user=request.user)
        if form.is_valid():
            # Retrieve the filter criteria from the form
            somities = form.cleaned_data['somity']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            account_number = form.cleaned_data['account_number']

            share_ac = ShareAC.objects.all()

            if somities:
                share_ac = share_ac.filter(customer__group__in=somities)

            # if start_date and end_date:
            #     share_ac = share_ac.filter(created_at__gte=start_date, created_at__lte=end_date)

            if account_number:
                share_ac = share_ac.filter(customer__account_no=account_number)

            totals = share_ac.aggregate(
                total_balance=Sum('balance'),
                total_profit_balance=Sum('profit_balance'),
            )

            branch = ActiveBranch.objects.get(user=request.user).branch

            return render(request, 'report/share_print.html', {'share_ac': share_ac, 'branch': branch, 'totals': totals})
    else:
        form = ShareReportForm(user=request.user)

    return render(request, 'report/share.html', {'form': form})


@login_required
def voucher_report(request):
    entries = None
    totals = {'total_amount': 0}
    if request.method == 'POST':
        form = VoucherReportForm(request.POST, user=request.user)
        if form.is_valid():
            # Retrieve the filter criteria from the form
            status = form.cleaned_data['status']
            voucher_categories = form.cleaned_data['voucher_category']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # users = form.cleaned_data['user']

            # Determine which model to query based on the status
            if status == 'Income':
                entries = Income.objects.all()
            else:
                entries = Expense.objects.all()

            # Filter by active branch
            branch = ActiveBranch.objects.get(user=request.user).branch
            entries = entries.filter(branch=branch)

            # Apply filters
            if voucher_categories:
                entries = entries.filter(voucher_category=voucher_categories)

            if start_date and end_date:
                date_field = 'IncomeDate' if status == 'Income' else 'ExpenseDate'
                entries = entries.filter(**{f'{date_field}__gte': start_date, f'{date_field}__lte': end_date})

            # if users:
            #     user_field = 'IncomeBy' if status == 'Income' else 'ExpenseBy'
            #     entries = entries.filter(**{f'{user_field}__in': [user.username for user in users]})

            # Aggregate totals
            totals = entries.aggregate(
                total_amount=Sum('Amount')
            )

            return render(request, 'report/voucher_print.html', {'entries': entries, 'branch': branch, 'totals': totals, 'status': status})
    else:
        form = VoucherReportForm(user=request.user)

    return render(request, 'report/voucher.html', {'form': form})



@login_required
def loanOC_report(request):
    entries = None
    totals = {'total_amount': 0}
    
    if request.method == 'POST':
        form = LoanOCReportForm(request.POST, user=request.user)
        if form.is_valid():
            # Retrieve the filter criteria from the form
            status = form.cleaned_data['status']
            somities = form.cleaned_data['somity']
            loan_category = form.cleaned_data['loan_category']
            loan_scheme = form.cleaned_data['loan_scheme']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            account_number = form.cleaned_data['account_number']
            
            # Filter LoanAC model based on form data
            branch = ActiveBranch.objects.get(user=request.user).branch
            entries = LoanAC.objects.filter(branch=branch)

            if somities.exists():
                entries = entries.filter(customer__group__in=somities)

            if loan_category:
                entries = entries.filter(loan_category=loan_category)

            if loan_scheme != 'all':
                entries = entries.filter(loan_scheme=loan_scheme)
            
            if start_date and end_date:
                entries = entries.filter(date__range=[start_date, end_date])

            if account_number:
                entries = entries.filter(customer__account_number__icontains=account_number)

            if status != 'all':
                entries = entries.filter(status=status)



            entries = entries.annotate(
                collection_profit=ExpressionWrapper(
                    F('paid_amount') * F('profit_percent') / 100,
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                collection_principal=ExpressionWrapper(
                    F('paid_amount') - (F('collection_profit')),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                closing_principal=ExpressionWrapper(
                    F('loan_amount') - (F('collection_principal')),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                closing_profit=ExpressionWrapper(
                    F('profit_taka') - (F('collection_profit')),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                closing_total=ExpressionWrapper(
                    F('total_amount') - (F('paid_amount')),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
            )

            # Aggregate totals
            totals = entries.aggregate(
                total_amount=Sum('total_amount'),
                total_loan_amount=Sum('loan_amount'),
                total_profit_amount=Sum('profit_taka'),

                total_collection_profit=Sum('collection_profit'),
                total_collection_principal=Sum('collection_principal'),
                total_collection_total=Sum('paid_amount'),

                total_closing_principal=Sum('closing_principal'),
                total_closing_profit=Sum('closing_profit'),
                total_closing_total=Sum('closing_total'),
            )
            # Aggregate totals
            # totals = entries.aggregate(total_amount=Sum('loan_amount'))


            return render(request, 'report/loanOC_print.html', {'entries': entries, 'branch': branch, 'totals': totals, 'status': status})
    else:
        form = LoanOCReportForm(user=request.user)

    return render(request, 'report/loanOC.html', {'form': form})


@login_required
def balance_sheet(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    today = date.today()

    total_daily_loan_amount = LoanAC.objects.filter(branch=branch,loan_scheme='daily').aggregate(total_loan=Sum('loan_amount'))['total_loan'] or 0
    total_weekly_loan_amount = LoanAC.objects.filter(branch=branch,loan_scheme='weekly').aggregate(total_loan=Sum('loan_amount'))['total_loan'] or 0
    total_monthly_loan_amount = LoanAC.objects.filter(branch=branch,loan_scheme='monthly').aggregate(total_loan=Sum('loan_amount'))['total_loan'] or 0

    total_cc_loan_amount = Loan_CC.objects.filter(branch=branch,loan_scheme='monthly').aggregate(total_loan=Sum('loan_amount'))['total_loan'] or 0
    total_special_loan_amount = Loan_Special.objects.filter(branch=branch).aggregate(total_loan=Sum('amount'))['total_loan'] or 0
    cash_in_bank = Bank.objects.filter(branch=branch).aggregate(total_loan=Sum('balance'))['total_loan'] or 0
    cash_in_hand = 0
    total_asset = (
        total_daily_loan_amount + total_weekly_loan_amount + total_monthly_loan_amount + 
        total_cc_loan_amount + total_special_loan_amount + cash_in_bank + cash_in_hand)
    

    general_savings_daily = GeneralAC.objects.filter(customer__branch=branch, customer__customer_type='daily').aggregate(total=Sum('balance'))['total'] or 0
    general_savings_weekly = GeneralAC.objects.filter(customer__branch=branch, customer__customer_type='weekly').aggregate(total=Sum('balance'))['total'] or 0
    general_savings_monthly = GeneralAC.objects.filter(customer__branch=branch, customer__customer_type='monthly').aggregate(total=Sum('balance'))['total'] or 0

    special_savings_daily = SavingsAC.objects.filter(customer__branch=branch, customer__customer_type='daily').aggregate(total=Sum('balance'))['total'] or 0
    special_savings_weekly = SavingsAC.objects.filter(customer__branch=branch, customer__customer_type='weekly').aggregate(total=Sum('balance'))['total'] or 0
    special_savings_monthly = SavingsAC.objects.filter(customer__branch=branch, customer__customer_type='monthly').aggregate(total=Sum('balance'))['total'] or 0

    share_balance = ShareAC.objects.filter(customer__branch=branch).aggregate(total=Sum('balance'))['total'] or 0
    share_profit_balance = ShareAC.objects.filter(customer__branch=branch).aggregate(total=Sum('profit_balance'))['total'] or 0

    dps_balance = DPS.objects.filter(branch=branch).aggregate(total=Sum('total_amount'))['total'] or 0
    fdr_balance = FDR.objects.filter(customer__branch=branch).aggregate(total=Sum('balance_amount'))['total'] or 0
    director_balance = Director.objects.filter(branch=branch).aggregate(total=Sum('balance'))['total'] or 0
    outloan_balance = OutLoan.objects.filter(branch=branch).aggregate(total=Sum('balance'))['total'] or 0
    staff_balance = CustomUser.objects.filter(branch=branch).aggregate(total=Sum('balance'))['total'] or 0

    logs = UserLog.objects.filter(branch=branch).exclude(action__isnull=True).exclude(action__exact='').order_by('-id')
    receive_logs = logs.filter(cashflow_type2='receive').values('action').annotate(total_amount=Sum('amount')).order_by('action')
    payment_logs = logs.filter(cashflow_type2='payment').values('action').annotate(total_amount=Sum('amount')).order_by('action')
    total_receive = receive_logs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    total_payment = payment_logs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00

    accumulated_profit_loss = total_receive - total_payment

    total_capital = (
        Decimal(general_savings_daily) + Decimal(general_savings_weekly) + Decimal(general_savings_monthly) +
        Decimal(special_savings_daily) + Decimal(special_savings_weekly) + Decimal(special_savings_monthly) +
        Decimal(share_balance) + Decimal(share_profit_balance) + Decimal(dps_balance) + Decimal(fdr_balance) +
        Decimal(director_balance) + Decimal(outloan_balance) + Decimal(staff_balance) + Decimal(accumulated_profit_loss) 
    )

    
    context = {
        'today': today,
        'total_daily_loan_amount': total_daily_loan_amount,
        'total_weekly_loan_amount': total_weekly_loan_amount,
        'total_monthly_loan_amount': total_monthly_loan_amount,
        'total_cc_loan_amount': total_cc_loan_amount,
        'total_special_loan_amount': total_special_loan_amount,
        'cash_in_hand': cash_in_hand,
        'cash_in_bank': cash_in_bank,
        'total_asset': total_asset,
        'branch': branch,

        'general_savings_daily': general_savings_daily,
        'general_savings_weekly': general_savings_weekly,
        'general_savings_monthly': general_savings_monthly,
        'special_savings_daily': special_savings_daily,
        'special_savings_weekly': special_savings_weekly,
        'special_savings_monthly': special_savings_monthly,
        'share_balance': share_balance,
        'share_profit_balance': share_profit_balance,
        'dps_balance': dps_balance,
        'fdr_balance': fdr_balance,
        'director_balance': director_balance,
        'outloan_balance': outloan_balance,
        'staff_balance': staff_balance,
        'accumulated_profit_loss': accumulated_profit_loss,
        'total_capital': total_capital,
    }
    return render(request, 'report/balance_sheet.html', context)



@login_required
def user_log(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    logs_actions = UserLog.objects.filter(branch=branch).exclude(logs_action__isnull=True).exclude(logs_action__exact='').order_by('-id')
    return render(request, 'report/user_log.html', {'logs_actions': logs_actions})


@login_required
def user_entry_summary(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = UESReportForm(request.POST, user=request.user)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            staff = form.cleaned_data['staff']

            logs = UserLog.objects.filter(branch=branch).exclude(action__isnull=True).exclude(action__exact='').order_by('-id')

            if start_date and end_date:
                end_date = end_date + timedelta(days=1)
                logs = logs.filter(timestamp__gte=start_date, timestamp__lt=end_date)

            if staff:
                logs = logs.filter(processed_by=staff)

            total_cash_in = logs.filter(transaction_type='cash_in').aggregate(Sum('amount'))['amount__sum'] or 0.00
            total_cash_out = logs.filter(transaction_type='cash_out').aggregate(Sum('amount'))['amount__sum'] or 0.00

            

            context ={
                'total_cash_in': total_cash_in,
                'total_cash_out': total_cash_out,
                'logs': logs, 'branch': branch, 
                'staff':staff, 'start_date':start_date, 
                'end_date':end_date
            }
            return render(request, 'report/ues_print.html', context)
    else:
        form = UESReportForm(user=request.user)

    return render(request, 'report/ues.html', {'form': form})

@login_required
def user_wise_entry_summary(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = UWESReportForm(request.POST, user=request.user)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Get all users who have logs within the date range
            logs = UserLog.objects.filter(branch=branch).exclude(action__isnull=True).exclude(action__exact='')

            if start_date and end_date:
                end_date = end_date + timedelta(days=1)
                logs = logs.filter(timestamp__gte=start_date, timestamp__lt=end_date)
            
            users = CustomUser.objects.filter(id__in=logs.values('processed_by')).distinct()

            # Initialize dictionaries for totals
            staff_data = []
            grand_total_cash_in = 0
            grand_total_cash_out = 0

            for user in users:
                user_logs = logs.filter(processed_by=user)
                total_cash_in = user_logs.filter(transaction_type='cash_in').aggregate(Sum('amount'))['amount__sum'] or 0.00
                total_cash_out = user_logs.filter(transaction_type='cash_out').aggregate(Sum('amount'))['amount__sum'] or 0.00
                balance = Decimal(total_cash_in) - Decimal(total_cash_out)

                staff_data.append({
                    'staff': user,
                    'total_cash_in': total_cash_in,
                    'total_cash_out': total_cash_out,
                    'balance': balance
                })

                grand_total_cash_in += Decimal(total_cash_in)
                grand_total_cash_out += Decimal(total_cash_out)

            grand_balance = grand_total_cash_in - grand_total_cash_out
            

            context = {
                'staff_data': staff_data,
                'grand_total_cash_in': grand_total_cash_in,
                'grand_total_cash_out': grand_total_cash_out,
                'grand_balance': grand_balance,
                'branch': branch,
                'start_date': start_date,
                'end_date': end_date
            }

            return render(request, 'report/uwes_print.html', context)
    else:
        form = UWESReportForm(user=request.user)

    return render(request, 'report/uwes.html', {'form': form})


@login_required
def general_ledger(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = GeneralLedgerForm(request.POST, user=request.user)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            staff = form.cleaned_data['staff']
            account_number = form.cleaned_data['account_number']
            action = form.cleaned_data['action']

            # Initial queryset
            logs = UserLog.objects.filter(branch=branch).exclude(action__isnull=True).exclude(action__exact='').order_by('-id')

            # Apply date filters
            if start_date and end_date:
                end_date = end_date + timedelta(days=1)
                logs = logs.filter(timestamp__gte=start_date, timestamp__lt=end_date)

            # Apply staff filter
            if staff:
                logs = logs.filter(processed_by=staff)

            # Apply account_number filter (assuming it's related to Customer model)
            if account_number:
                logs = logs.filter(customer__account_no=account_number)

            # Apply action filter
            if action:
                logs = logs.filter(action=action)

            # Calculate totals
            total_cash_in = logs.filter(transaction_type='cash_in').aggregate(Sum('amount'))['amount__sum'] or 0.00
            total_cash_out = logs.filter(transaction_type='cash_out').aggregate(Sum('amount'))['amount__sum'] or 0.00

            

            context = {
                'total_cash_in': total_cash_in,
                'total_cash_out': total_cash_out,
                'logs': logs,
                'branch': branch,
                'staff': staff,
                'start_date': start_date,
                'end_date': end_date - timedelta(days=1),
                'account_number': account_number,
                'action': action
            }

            return render(request, 'report/general_ledger_print.html', context)
    else:
        form = GeneralLedgerForm(user=request.user)

    return render(request, 'report/general_ledger.html', {'form': form})

@login_required
def ReceivePayment(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = ReceivePaymentReportForm(request.POST, user=request.user)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Initial queryset
            logs = UserLog.objects.filter(branch=branch).exclude(action__isnull=True).exclude(action__exact='').order_by('-id')

            # Apply date filters
            if start_date and end_date:
                end_date = end_date + timedelta(days=1)
                logs = logs.filter(timestamp__gte=start_date, timestamp__lt=end_date)

            # Aggregate by action for receive and payment
            receive_logs = logs.filter(cashflow_type2='receive').values('action').annotate(total_amount=Sum('amount')).order_by('action')
            payment_logs = logs.filter(cashflow_type2='payment').values('action').annotate(total_amount=Sum('amount')).order_by('action')

            # Calculate totals
            total_receive = receive_logs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
            total_payment = payment_logs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00

            total_payment = float(total_payment)
            total_receive = float(total_receive)

            context = {
                'total_receive': total_receive,
                'total_payment': total_payment,
                'receive_logs': receive_logs,
                'payment_logs': payment_logs,
                'branch': branch,
                'start_date': start_date,
                'end_date': end_date - timedelta(days=1),
                'final_balance': total_receive - total_payment,
            }

            return render(request, 'report/ReceivePayment_print.html', context)
    else:
        form = ReceivePaymentReportForm(user=request.user)

    return render(request, 'report/ReceivePayment.html', {'form': form})


@login_required
def ProfitLoss(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = ProfitLossReportForm(request.POST, user=request.user)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Initial queryset
            logs = UserLog.objects.filter(branch=branch).exclude(action__isnull=True).exclude(action__exact='').order_by('-id')

            # Apply date filters
            if start_date and end_date:
                end_date = end_date + timedelta(days=1)
                logs = logs.filter(timestamp__gte=start_date, timestamp__lt=end_date)

            # Aggregate by action for receive and payment
            receive_logs = logs.filter(cashflow_type2='receive').values('action').annotate(total_amount=Sum('amount')).order_by('action')
            payment_logs = logs.filter(cashflow_type2='payment').values('action').annotate(total_amount=Sum('amount')).order_by('action')

            # Calculate totals
            total_receive = receive_logs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
            total_payment = payment_logs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00

            total_payment = float(total_payment)
            total_receive = float(total_receive)
            
            context = {
                'total_receive': total_receive,
                'total_payment': total_payment,
                'receive_logs': receive_logs,
                'payment_logs': payment_logs,
                'branch': branch,
                'start_date': start_date,
                'end_date': end_date - timedelta(days=1),
                'final_balance': total_receive - total_payment,
            }

            return render(request, 'report/ProfitLoss_print.html', context)
    else:
        form = ProfitLossReportForm(user=request.user)

    return render(request, 'report/ProfitLoss.html', {'form': form})







@login_required
def monthly_top_sheet_report(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            selected_month = int(form.cleaned_data['month'])
            selected_year = int(form.cleaned_data['year'])
            report_type = form.cleaned_data['report_type']
            
            # Prepare month and year range
            start_date = datetime(selected_year, selected_month, 1)
            end_date = datetime(selected_year, selected_month + 1, 1) if selected_month < 12 else datetime(selected_year + 1, 1, 1)
            
            # Query logs and filter by branch
            logs = UserLog.objects.filter(timestamp__range=(start_date, end_date), branch=branch).exclude(action=None)
            
            # Separate logs by income and expense if report_type is "all"
            income_logs = logs.filter(cashflow_type1='income')
            expense_logs = logs.filter(cashflow_type1='expense')
            
            # Aggregate amounts by action and day
            def aggregate_logs(logs):
                data = {}
                for log in logs:
                    action = log.action or 'Unknown'
                    day = log.timestamp.day
                    amount = log.amount or 0
                    if action not in data:
                        data[action] = [0] * monthrange(selected_year, selected_month)[1]
                    data[action][day - 1] += amount
                totals = [sum(day[i] for day in data.values()) for i in range(monthrange(selected_year, selected_month)[1])]
                total_sum = sum(totals)
                return data, totals, total_sum
            
            if report_type == 'all':
                income_data, income_totals, income_sum = aggregate_logs(income_logs)
                expense_data, expense_totals, expense_sum = aggregate_logs(expense_logs)
            elif report_type == 'income':
                income_data, income_totals, income_sum = aggregate_logs(income_logs)
                expense_data, expense_totals, expense_sum = None, None, None
            else:
                expense_data, expense_totals, expense_sum = aggregate_logs(expense_logs)
                income_data, income_totals, income_sum = None, None, None

            # Convert month number to name
            selected_month_name = start_date.strftime('%B')

            context = {
                'form': form,
                'income_data': income_data,
                'expense_data': expense_data,
                'income_totals': income_totals,
                'expense_totals': expense_totals,
                'income_sum': income_sum,
                'expense_sum': expense_sum,
                'selected_month_name': selected_month_name,
                'selected_year': selected_year,
                'branch': branch,
                'days': range(1, monthrange(selected_year, selected_month)[1] + 1),
                'report_type': report_type,
            }
            return render(request, 'report/monthly_top_sheet_print.html', context)
    else:
        form = ReportForm()

    return render(request, 'report/monthly_top_sheet_filter.html', {'form': form})


@login_required
def monthly_wise_top_sheet_report(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = MonthWiseTopSheetForm(request.POST)
        if form.is_valid():
            selected_year = int(form.cleaned_data['year'])
            report_type = form.cleaned_data['report_type']
            
            # Prepare start and end dates for the year
            start_date = datetime(selected_year, 1, 1)
            end_date = datetime(selected_year + 1, 1, 1)
            
            # Query logs and filter by branch
            logs = UserLog.objects.filter(timestamp__range=(start_date, end_date), branch=branch).exclude(action=None)
            
            # Separate logs by income and expense if report_type is "all"
            income_logs = logs.filter(cashflow_type1='income')
            expense_logs = logs.filter(cashflow_type1='expense')
            
            # Aggregate amounts by action and month
            def aggregate_logs_by_month(logs):
                data = {}
                for log in logs:
                    action = log.action or 'Unknown'
                    month = log.timestamp.month
                    amount = log.amount or 0
                    if action not in data:
                        data[action] = [0] * 12
                    data[action][month - 1] += amount
                totals = [sum(month[i] for month in data.values()) for i in range(12)]
                total_sum = sum(totals)
                return data, totals, total_sum
            
            if report_type == 'all':
                income_data, income_totals, income_sum = aggregate_logs_by_month(income_logs)
                expense_data, expense_totals, expense_sum = aggregate_logs_by_month(expense_logs)
            elif report_type == 'income':
                income_data, income_totals, income_sum = aggregate_logs_by_month(income_logs)
                expense_data, expense_totals, expense_sum = None, None, None
            else:
                expense_data, expense_totals, expense_sum = aggregate_logs_by_month(expense_logs)
                income_data, income_totals, income_sum = None, None, None

            context = {
                'form': form,
                'income_data': income_data,
                'expense_data': expense_data,
                'income_totals': income_totals,
                'expense_totals': expense_totals,
                'income_sum': income_sum,
                'expense_sum': expense_sum,
                'selected_year': selected_year,
                'branch': branch,
                'report_type': report_type,
            }
            return render(request, 'report/monthly_wise_top_sheet_print.html', context)
    else:
        form = MonthWiseTopSheetForm()

    return render(request, 'report/monthly_wise_top_sheet_filter.html', {'form': form})









from django.db.models import Sum

@login_required
def account_statement(request):
    branch = ActiveBranch.objects.get(user=request.user).branch
    if request.method == 'POST':
        form = AccountStatementForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            account_number = form.cleaned_data['account_number']
            account_type = form.cleaned_data['account_type']

            customer = Customer.objects.get(account_no=account_number)
            if end_date:
                end_date = end_date + timedelta(days=1)
            date_filter = {}
            if start_date and end_date:
                date_filter = {'created_at__range': (start_date, end_date)}



            # Filter transactions based on the date range or return all transactions if no dates are provided
            general_trans = GeneralTransactionHistory.objects.filter(general__customer=customer, **date_filter)
            special_trans = SavingsTransactionHistory.objects.filter(general__customer=customer, **date_filter)
            share_trans = ShareACTransactionHistory.objects.filter(share_ac__customer=customer, **date_filter)
            fdr_trans = FDRTransactionHistory.objects.filter(fdr__customer=customer, **date_filter)

            date_filter = {}
            if start_date and end_date:
                date_filter = {'Date__range': (start_date, end_date)} 
            loan_trans = LoanCollection.objects.filter(loan__customer=customer, **date_filter)
            cc_loan_trans = Loan_CC_Collection.objects.filter(loan_cc__customer=customer, **date_filter)


            date_filter = {}
            if start_date and end_date:
                date_filter = {'date__range': (start_date, end_date)}

            dps_trans = DPSTransactionHistory.objects.filter(dps__customer=customer, **date_filter)

            # Summing up deposits and withdrawals
            general_deposit_sum = general_trans.filter(transaction_type='deposit').aggregate(Sum('Amount'))['Amount__sum'] or 0
            general_withdraw_sum = general_trans.filter(transaction_type='withdraw').aggregate(Sum('Amount'))['Amount__sum'] or 0

            special_deposit_sum = special_trans.filter(transaction_type='deposit').aggregate(Sum('Amount'))['Amount__sum'] or 0
            special_withdraw_sum = special_trans.filter(transaction_type='withdraw').aggregate(Sum('Amount'))['Amount__sum'] or 0

            share_deposit_sum = share_trans.filter(transaction_type='deposit').aggregate(Sum('Amount'))['Amount__sum'] or 0
            share_withdraw_sum = share_trans.filter(transaction_type='withdraw').aggregate(Sum('Amount'))['Amount__sum'] or 0

            loan_collection_sum = loan_trans.aggregate(Sum('Amount'))['Amount__sum'] or 0
            cc_loan_collection_sum = cc_loan_trans.aggregate(Sum('Amount'))['Amount__sum'] or 0

            fdr_deposit_sum = fdr_trans.filter(transaction_type='deposit').aggregate(Sum('Amount'))['Amount__sum'] or 0
            fdr_withdraw_sum = fdr_trans.filter(transaction_type='withdraw').aggregate(Sum('Amount'))['Amount__sum'] or 0

            dps_deposit_sum = dps_trans.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0
            dps_withdraw_sum = dps_trans.filter(transaction_type='withdraw').aggregate(Sum('amount'))['amount__sum'] or 0


            total_deposit_sum = general_deposit_sum + special_deposit_sum + share_deposit_sum + fdr_deposit_sum + dps_deposit_sum
            total_withdraw_sum = general_withdraw_sum + special_withdraw_sum + share_withdraw_sum + fdr_withdraw_sum + dps_withdraw_sum

            context = {
                'general_trans': general_trans,
                'savings_trans': special_trans,
                'share_ac_trans': share_trans,
                'loan_collections': loan_trans,
                'loan_cc_collections': cc_loan_trans,
                'fdr_transaction_history': fdr_trans,
                'dps_transaction_history': dps_trans,
                'branch': branch,
                'customer': customer,
                'general_deposit_sum': general_deposit_sum,
                'general_withdraw_sum': general_withdraw_sum,
                'special_deposit_sum': special_deposit_sum,
                'special_withdraw_sum': special_withdraw_sum,
                'share_deposit_sum': share_deposit_sum,
                'share_withdraw_sum': share_withdraw_sum,
                'loan_collection_sum': loan_collection_sum,
                'cc_loan_collection_sum': cc_loan_collection_sum,
                'fdr_deposit_sum': fdr_deposit_sum,
                'fdr_withdraw_sum': fdr_withdraw_sum,
                'dps_deposit_sum': dps_deposit_sum,
                'dps_withdraw_sum': dps_withdraw_sum,
                'total_deposit_sum': total_deposit_sum,
                'total_withdraw_sum': total_withdraw_sum,
                'account_type' : account_type,
            }

            return render(request, 'report/account_statment_print.html', context)
    else:
        form = AccountStatementForm()

    return render(request, 'report/account_statment.html', {'form': form})



