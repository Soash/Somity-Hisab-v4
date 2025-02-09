from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from primary_setup.models import CustomUser, OutLoan
from report.models import UserLog
from .forms import ExpenseForm, GetOutLoanForm, IncomeForm, DepositForm, ReturnOutLoanForm, WithdrawForm, PassbookForm, ssmDepositForm, ssmWithdrawForm
from .models import Expense, GetOutLoan, Income, Deposit, ProfitDistribution, Salary, Withdraw, Passbook, SSM_Deposit, SSM_Withdraw

from app1.models import ActiveBranch, Customer, GeneralAC, GeneralDeposit, GeneralTransactionHistory, ShareAC, ShareACTransactionHistory
from django.shortcuts import get_object_or_404, redirect


@login_required
@permission_required('otrans.view_expense', raise_exception=True)
def general_expense(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('expense_create')

    data = Expense.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.branch = active_branch.branch
            expense.save()
            messages.success(request, 'Expense has been added successfully.')

            UserLog.objects.create(processed_by=request.user, VoucherID=expense.VoucherID, timestamp=expense.ExpenseDate, logs_action='Add General Expense',description=f'Category: {expense.voucher_category}, TrxID: {expense.VoucherID}')
            UserLog.objects.create(processed_by=request.user, VoucherID=expense.VoucherID, timestamp=expense.ExpenseDate, action=f'{expense.voucher_category}',amount=expense.Amount, trx=True)
            
            return redirect('general_expense')
    else:
        form = ExpenseForm(user=request.user)

    context = {
        'form': form,
        'expenses': data,
    }
    return render(request, 'otrans/general_expense.html', context)


@login_required
@permission_required('otrans.view_income', raise_exception=True)
def general_income(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('general_income')

    data = Income.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.save(commit=False)
            data.branch = active_branch.branch
            data.save()
            messages.success(request, 'income has been added successfully.')

            
            UserLog.objects.create(processed_by=request.user, VoucherID=data.VoucherID, timestamp=data.IncomeDate, logs_action='Add General Expense',description=f'Category: {data.voucher_category}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user, VoucherID=data.VoucherID, timestamp=data.IncomeDate, action=f'{data.voucher_category}',amount=data.Amount)

            return redirect('general_income')
    else:
        form = IncomeForm(user=request.user)

    context = {
        'form': form,
        'data': data,
    }
    return render(request, 'otrans/general_income.html', context)


@login_required
@permission_required('otrans.view_deposit', raise_exception=True)
def director_deposit(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('director_deposit')

    data = Deposit.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.save(commit=False)
            data.processed_by = request.user
            data.branch = active_branch.branch
            data.save()

            director = data.director
            director.balance = (director.balance or 0) + data.Amount
            director.save()

            messages.success(request, 'Transaction successfully.')

            UserLog.objects.create(processed_by=request.user,logs_action='Deposit from Director',description=f'Director: {director}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Deposit from Director',amount=data.Amount)

            return redirect('director_deposit')
    else:
        form = DepositForm(user=request.user)

    context = {
        'form': form,
        'data': data,
    }
    return render(request, 'otrans/dir_deposit.html', context)


@login_required
@permission_required('otrans.view_withdraw', raise_exception=True)
def director_withdraw(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('director_withdraw')

    data = Withdraw.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.save(commit=False)
            data.processed_by = request.user
            data.branch = active_branch.branch
            data.save()

            director = data.director
            if director.balance > data.Amount:
                director.balance = director.balance - data.Amount
                director.save()
            else:
                data.delete()
                messages.warning(request, 'Not enough balance.')
                return redirect('director_withdraw')

            messages.success(request, 'Transaction successfully.')

            UserLog.objects.create(processed_by=request.user,logs_action='Withdraw from Director',description=f'Director: {director}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Withdraw from Director',amount=data.Amount, trx=True)

            return redirect('director_withdraw')
    else:
        form = WithdrawForm(user=request.user)

    context = {
        'form': form,
        'data': data,
    }
    return render(request, 'otrans/dir_withdraw.html', context)


@login_required
@permission_required('otrans.view_passbook', raise_exception=True)
def passbook(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('director_withdraw')

    data = Passbook.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = PassbookForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.save(commit=False)
            data.processed_by = request.user
            data.branch = active_branch.branch
            customer = get_object_or_404(Customer, account_no=data.Account)
            data.customer = customer
            print(customer.customer_type)
            data.Category = customer.customer_type
            data.save()

            messages.success(request, 'Passbook Saved.')

            UserLog.objects.create(processed_by=request.user,logs_action='Add Pass Book',description=f'Account: {customer.account_no}, TrxID: {data.VoucherID}')
            UserLog.objects.create(processed_by=request.user,action=f'Pass Book {customer.customer_type}',amount=data.Amount)

            return redirect('passbook')
    else:
        form = PassbookForm(user=request.user)

    context = {
        'form': form,
        'data': data,
    }
    return render(request, 'otrans/passbook.html', context)


@login_required
@permission_required('otrans.view_ssm_deposit', raise_exception=True)
def ssm_deposit(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    print('ok')
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('ssm_deposit')

    data = SSM_Deposit.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = ssmDepositForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.save(commit=False)
            data.processed_by = request.user
            data.branch = active_branch.branch
            data.save()

            staff = data.staff
            staff.balance = (staff.balance or 0) + data.Amount
            staff.save()

            messages.success(request, 'Transaction successfully.')

            UserLog.objects.create(processed_by=request.user,logs_action='Staff Security Money Deposit',description=f'Staff: {staff}, Amount: {data.Amount}')
            UserLog.objects.create(processed_by=request.user,action=f'Staff Security Money Deposit',amount=data.Amount)

            return redirect('ssm_deposit')
    else:
        form = ssmDepositForm(user=request.user)

    context = {
        'form': form,
        'data': data,
    }
    return render(request, 'otrans/ssm_deposit.html', context)


@login_required
@permission_required('otrans.view_ssm_withdraw', raise_exception=True)
def ssm_withdraw(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    
    if not active_branch:
        messages.error(request, 'No active branch set.')
        return redirect('ssm_withdraw')

    data = SSM_Withdraw.objects.filter(branch=active_branch.branch)

    if request.method == 'POST':
        form = ssmWithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.save(commit=False)
            data.processed_by = request.user
            data.branch = active_branch.branch
            data.save()

            staff = data.staff
            if staff.balance > data.Amount:
                staff.balance = staff.balance - data.Amount
                staff.save()
            else:
                data.delete()
                messages.warning(request, 'Not enough balance.')
                return redirect('ssm_withdraw')
            
            UserLog.objects.create(processed_by=request.user,logs_action='Staff Security Money Withdraw',description=f'Staff: {staff}, Amount: {data.Amount}')
            UserLog.objects.create(processed_by=request.user,action=f'Staff Security Money Withdraw',amount=data.Amount, trx=True)

            messages.success(request, 'Transaction successfully.')
            return redirect('ssm_withdraw')
    else:
        form = ssmWithdrawForm(user=request.user)

    context = {
        'form': form,
        'data': data,
    }
    return render(request, 'otrans/ssm_withdraw.html', context)


@login_required
@permission_required('otrans.delete_expense', raise_exception=True)
def expense_delete(request, pk):
    data = get_object_or_404(Expense, pk=pk)
    user_logs = UserLog.objects.filter(VoucherID=data.VoucherID)  # Use filter() instead of get()
    
    if request.method == 'GET':
        data.delete()
        user_logs.delete()  # This will delete all related UserLog entries
        messages.success(request, 'Expense has been deleted successfully.')
        return redirect('general_expense')



@login_required
@permission_required('otrans.delete_income', raise_exception=True)
def income_delete(request, pk):
    data = get_object_or_404(Income, pk=pk)
    user_logs = UserLog.objects.filter(VoucherID=data.VoucherID)
    if request.method == 'GET':
        data.delete()
        user_logs.delete()
        messages.success(request, 'Income has been deleted successfully.')
        return redirect('general_income')


@login_required
@permission_required('otrans.delete_passbook', raise_exception=True)
def passbook_delete(request, pk):
    data = get_object_or_404(Passbook, pk=pk)
    if request.method == 'GET':
        data.delete()
        messages.success(request, 'Passbook has been deleted successfully.')
        return redirect('passbook')


@login_required
def expense_print(request, pk):
    data = get_object_or_404(Expense, pk=pk)
    return render(request, 'otrans/general_expense_print.html', {'data': data})

@login_required
def income_print(request, pk):
    data = get_object_or_404(Income, pk=pk)
    return render(request, 'otrans/general_income_print.html', {'data': data})

@login_required
def deposit_print(request, pk):
    data = get_object_or_404(Deposit, pk=pk)
    return render(request, 'otrans/dir_deposit_print.html', {'data': data})

@login_required
def ssm_deposit_print(request, pk):
    data = get_object_or_404(SSM_Deposit, pk=pk)
    return render(request, 'otrans/ssm_deposit_print.html', {'data': data})

@login_required
def withdraw_print(request, pk):
    data = get_object_or_404(Withdraw, pk=pk)
    return render(request, 'otrans/dir_withdraw_print.html', {'data': data})

@login_required
def ssm_withdraw_print(request, pk):
    data = get_object_or_404(Withdraw, pk=pk)
    return render(request, 'otrans/ssm_withdraw_print.html', {'data': data})

@login_required
def passbook_print(request, pk):
    data = get_object_or_404(Passbook, pk=pk)
    return render(request, 'otrans/passbook_print.html', {'data': data})




@login_required
@permission_required('otrans.view_getoutloan', raise_exception=True)
def get_out_loan(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    data = GetOutLoan.objects.filter(branch=active_branch.branch).order_by('-id')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        account_id = request.GET.get('account_id')
        try:
            out_loan = OutLoan.objects.get(pk=account_id, branch=active_branch.branch)
            balance = out_loan.balance
        except OutLoan.DoesNotExist:
            balance = 0.0
        return JsonResponse({'balance': balance})

    if request.method == 'POST':
        form = GetOutLoanForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.processed_by = request.user
            deposit.branch = active_branch.branch

            # Convert deposit_amount to Decimal
            deposit_amount = Decimal(form.cleaned_data['deposit_amount'])
            profit = Decimal(form.cleaned_data['profit'])

            # Update the current amount for the GetOutLoan
            deposit.current_amount += deposit_amount
        

            # Update the balance in the OutLoan account, converting Decimal to float
            out_loan = deposit.account
            out_loan.balance += float(deposit_amount)
            out_loan.profit += float(profit)
            out_loan.save()

            deposit.profit = out_loan.profit
            deposit.save()

            UserLog.objects.create(processed_by=request.user,logs_action='Out Loan Received',description=f'TrxID: {deposit.VoucherID}, Amount: {deposit_amount}')
            UserLog.objects.create(processed_by=request.user,action=f'Out Loan Received',amount=deposit_amount)

            return redirect('get_out_loan')
    else:
        form = GetOutLoanForm()

    context = {
        'data': data,
        'form': form,
    }
    return render(request, 'otrans/get_out_loan.html', context)


@login_required
@permission_required('otrans.view_getoutloan', raise_exception=True)
def return_out_loan(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    branch = active_branch.branch
    data = GetOutLoan.objects.filter(branch=branch).order_by('-id')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        account_id = request.GET.get('account_id')
        try:
            out_loan = OutLoan.objects.get(pk=account_id, branch=active_branch.branch)
            balance = out_loan.balance
        except OutLoan.DoesNotExist:
            balance = 0.0
        return JsonResponse({'balance': balance})

    if request.method == 'POST':
        form = ReturnOutLoanForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.processed_by = request.user
            deposit.branch = active_branch.branch

            # Convert deposit_amount to Decimal
            deposit_amount = Decimal(form.cleaned_data['deposit_amount'])
            profit = Decimal(form.cleaned_data['profit'])

            total = deposit_amount + profit

            # Update the balance in the OutLoan account, converting Decimal to float
            out_loan = deposit.account
            out_loan.balance -= float(deposit_amount)
            out_loan.profit -= float(profit)
            out_loan.save()
            
            deposit.current_amount = out_loan.balance
            deposit.profit = out_loan.profit
            deposit.save()

            UserLog.objects.create(processed_by=request.user,logs_action='Out Loan Paid',description=f'TrxID: {deposit.VoucherID}, Amount: {total}')
            UserLog.objects.create(processed_by=request.user,action=f'Out Loan Installment Paid',amount=deposit_amount, trx=True)
            UserLog.objects.create(processed_by=request.user,action=f'Out Loan Insterest Paid',amount=profit, trx=True)

            return redirect('return_out_loan')
    else:
        form = ReturnOutLoanForm()

    context = {
        'data': data,
        'form': form,
    }

    return render(request, 'otrans/return_out_loan.html', context)



















@login_required
@permission_required('otrans.view_salary', raise_exception=True)
def staff_salary_sheet(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    branch = active_branch.branch
    data = Salary.objects.filter(branch=branch)

    if request.method == 'POST':
        year = request.POST.get('year')
        month = request.POST.get('month')
        date = request.POST.get('date')

        users = CustomUser.objects.filter(branch=branch)

        context ={
            'year': year,
            'month': month,
            'date': date,
            'staff': users,
            'branch': branch
        }
        return render(request, 'otrans/staff_salary_input.html', context)

    context = {
        'data': data,
    }
    return render(request, 'otrans/staff_salary_sheet.html', context)

@login_required
@permission_required('otrans.view_salary', raise_exception=True)
def save_salary(request):
    if request.method == 'POST':
        active_branch = ActiveBranch.objects.filter(user=request.user).first()
        branch = active_branch.branch
        year = request.POST.get('year')
        month = request.POST.get('month')
        current_date = request.POST.get('date')

        # Get the list of selected staff IDs
        selected_staff_ids = request.POST.getlist('staff_ids')

        for staff_id in selected_staff_ids:
            staff = CustomUser.objects.get(id=staff_id)
            basic_salary = staff.basic_salary
            others = Decimal(request.POST.get(f'others_{staff_id}', '0'))
            bonus = Decimal(request.POST.get(f'bonus_{staff_id}', '0'))
            deduction = Decimal(request.POST.get(f'deduction_{staff_id}', '0'))

            # Create and save the Salary object
            salary = Salary(
                branch=branch,
                date=current_date,
                year=year,
                month=month,
                staff_name=staff.username,
                basic_salary=basic_salary,
                others=others,
                bonus=bonus,
                deduction=deduction,
                processed_by=request.user.username
            )
            salary.save()

        UserLog.objects.create(processed_by=request.user,logs_action='Salary Distribution',description=f'Year: {year}, Month: {month}, Date: {current_date}')
        return redirect('staff_salary_sheet')

    return render(request, 'otrans/staff_salary_sheet.html')

@login_required
@permission_required('otrans.view_salary', raise_exception=True)
def delete_salary(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    salary.delete()
    return redirect('staff_salary_sheet')


@login_required
def profit_generate_monthly(request):
    if request.method == 'GET' and 'financial_year' in request.GET:
        financial_year = request.GET.get('financial_year')
        year = request.GET.get('year')
        profit_percentage = request.GET.get('profit_percentage')
        profit_type = request.GET.get('profit_type')
        date = request.GET.get('date')

        active_branch = ActiveBranch.objects.filter(user=request.user).first()
        branch = active_branch.branch

        total_share_accounts = ShareAC.objects.filter(customer__branch=branch).count()

        if profit_type == 'General_Account_Daily':
            total_customers = Customer.objects.filter(branch=branch, customer_type='daily')
        elif profit_type == 'General_Account_Weekly':
            total_customers = Customer.objects.filter(branch=branch, customer_type='weekly')
        elif profit_type == 'General_Account_Monthly':
            total_customers = Customer.objects.filter(branch=branch, customer_type='monthly')
        elif profit_type == 'Share_Account':
            total_customers = Customer.objects.filter(branch=branch, customer_type='monthly')
        else:
            total_customers = []

        

        random_customer = Customer.objects.filter(branch=branch).order_by('?').first()
        profit_rate = round(float(profit_percentage) / 12, 2)

        if profit_type == 'Share_Account':
            total_customers = Customer.objects.filter(branch=branch)
            total_ac = total_share_accounts
        else:
            total_ac = total_active_customers

        total_active_customers = total_customers.filter(status='Active').count()
        context = {
            'financial_year': financial_year,
            'year': year,
            'profit_percentage': profit_percentage,
            'profit_type': profit_type,
            'date': date,
            'total_customers': total_customers.count(),
            'total_active_customers': total_active_customers,
            'total_share_accounts': total_share_accounts,
            'random_customer': random_customer,
            'profit_rate': profit_rate,
            'total_ac': total_ac
        }
        return render(request, 'otrans/profit_generate_monthly.html', context)

    elif request.method == 'POST':
        active_branch = ActiveBranch.objects.filter(user=request.user).first()
        branch = active_branch.branch
        date = request.POST.get('date')
        financial_year = request.POST.get('financial_year')
        year = request.POST.get('year')
        profit_type = request.POST.get('profit_type')
        profit_percentage = float(request.POST.get('profit_percentage'))
        process_by = request.user.username

        if profit_type == 'General_Account_Daily':
            total_customers = Customer.objects.filter(branch=branch, customer_type='daily', status='Active')
        elif profit_type == 'General_Account_Weekly':
            total_customers = Customer.objects.filter(branch=branch, customer_type='weekly', status='Active')
        elif profit_type == 'General_Account_Monthly':
            total_customers = Customer.objects.filter(branch=branch, customer_type='monthly', status='Active')
        elif profit_type == 'Share_Account':
            total_customers = Customer.objects.filter(branch=branch, status='Active')
        else:
            total_customers = []

        total_profit_amount = 0
        total_ac = 0

        for customer in total_customers:
            if profit_type == 'Share_Account':
                accounts = ShareAC.objects.filter(customer=customer)
            else:
                accounts = GeneralAC.objects.filter(customer=customer)

            for account in accounts:
                balance = account.balance
                profit_percentage_decimal = Decimal(profit_percentage)
                profit_amount = round((balance * profit_percentage_decimal) / 100, 2)
                account.balance += profit_amount
                account.save()

                if profit_type == 'Share_Account':
                    ShareACTransactionHistory.objects.create(share_ac=account,transaction_type='deposit',Amount=profit_amount,
                            processed_by=request.user,note='Profit Distribution',balance=account.balance)
                    UserLog.objects.create(processed_by=request.user,action=f'Deposit Share AC',amount=profit_amount, customer=account.customer)
                else:
                    GeneralDeposit.objects.create(general=account,Amount=profit_amount,processed_by=request.user)
                    GeneralTransactionHistory.objects.create(general=account,transaction_type='deposit',Amount=profit_amount,processed_by=request.user,note='Profit Distribution',current_balance=account.balance)
                    UserLog.objects.create(processed_by=request.user,action=f'Deposit General AC {account.customer.customer_type}',amount=profit_amount,customer=account.customer)

                total_profit_amount += profit_amount
                total_ac += 1

        UserLog.objects.create(processed_by=request.user,logs_action='Profit Generate Monthly', description=f'')
        UserLog.objects.create(processed_by=request.user,action='Profit Generate Monthly',amount=total_profit_amount,trx=True)

        ProfitDistribution.objects.create(
            date=date,
            financial_year=financial_year,
            year=year,
            profit_type=profit_type,
            profit_percentage=profit_percentage,
            total_account=total_ac,
            profit_amount=total_profit_amount,
            process_by=process_by,
            branch=branch
        )
        return redirect('profit_distribution_history')

    return render(request, 'otrans/profit_generate_monthly_search.html')


@login_required
def profit_distribution_history(request):
    active_branch = ActiveBranch.objects.filter(user=request.user).first()
    branch = active_branch.branch
    profit_distributions = ProfitDistribution.objects.filter(branch=branch).order_by('-date')
    context = {
        'profit_distributions': profit_distributions,
    }
    return render(request, 'otrans/profit_distribution_history.html', context)

