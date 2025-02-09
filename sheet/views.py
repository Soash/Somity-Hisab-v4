from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app1.models import ActiveBranch, Customer, LoanAC
from primary_setup.models import Somity

@login_required
def select_somity(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch
    somities = Somity.objects.filter(branch=active_branch)
    if request.method == 'POST':
        selected_somity = request.POST.get('somity')
        return redirect('savings_collection_sheet', selected_somity)
    return render(request, 'sheet/select_somity.html', {'somities': somities})

@login_required
def savings_collection_sheet(request, somity_id):
    somity = Somity.objects.get(id=somity_id)
    customers = Customer.objects.filter(group=somity)
    context={
        'customers': customers,
        'somity': somity,
    }
    return render(request, 'sheet/savings_collection_sheet.html', context)

@login_required
def select_somity_loan_cc(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch
    somities = Somity.objects.filter(branch=active_branch)
    if request.method == 'POST':
        selected_somity = request.POST.get('somity')
        return redirect('cc_loan_collection_sheet', selected_somity)
    return render(request, 'sheet/select_somity.html', {'somities': somities})

@login_required
def cc_loan_collection_sheet(request, somity_id):
    somity = Somity.objects.get(id=somity_id)
    customers = Customer.objects.filter(group=somity, loan_cc__isnull=False)
    context={
        'customers': customers,
        'somity': somity,
    }
    return render(request, 'sheet/cc_loan_collection_sheet.html', context)

@login_required
def loan_collection_sheet_filter(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch
    somities = Somity.objects.filter(branch=active_branch)

    if request.method == 'POST':
        selected_somity = request.POST.get('somity')
        selected_scheme = request.POST.get('scheme')
        return redirect('loan_collection_sheet', selected_somity, selected_scheme)
    
    return render(request, 'sheet/loan_collection_sheet_filter.html', {'somities': somities})

@login_required
def loan_collection_sheet(request, somity_id, scheme):
    somity = Somity.objects.get(id=somity_id)
    loans = LoanAC.objects.filter(customer__group=somity, loan_scheme=scheme)
    
    context = {
        'loans': loans,
        'somity': somity,
        'scheme': scheme,
    }
    
    return render(request, 'sheet/loan_collection_sheet.html', context)

@login_required
def collection_sheet_filter(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch
    somities = Somity.objects.filter(branch=active_branch)

    if request.method == 'POST':
        selected_somity = request.POST.get('somity')
        selected_date = request.POST.get('date')
        return redirect('collection_sheet', selected_somity, selected_date)
    
    return render(request, 'sheet/collection_sheet_filter.html', {'somities': somities})

@login_required
def collection_sheet(request, somity_id, date):
    somity = Somity.objects.get(id=somity_id)
    customers = Customer.objects.filter(group=somity).order_by('account_no')
    context={
        'customers': customers,
        'somity': somity,
        'date': date,
    }
    return render(request, 'sheet/collection_sheet.html', context)

@login_required
def collection_sheet_filter2(request):
    active_branch = ActiveBranch.objects.get(user=request.user).branch
    somities = Somity.objects.filter(branch=active_branch)
    if request.method == 'POST':
        selected_somity = request.POST.get('somity')
        return redirect('collection_sheet2', selected_somity)
    return render(request, 'sheet/select_somity.html', {'somities': somities})

@login_required
def collection_sheet2(request, somity_id):
    somity = Somity.objects.get(id=somity_id)
    customers = Customer.objects.filter(group=somity).order_by('account_no')
    context={
        'customers': customers,
        'somity': somity,
    }
    return render(request, 'sheet/collection_sheet2.html', context)



