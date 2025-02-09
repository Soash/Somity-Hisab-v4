from django import template
from app1.models import DPS, GeneralAC, LoanAC, SavingsAC
from django.db import models

register = template.Library()

@register.simple_tag
def customer_balance(customer):
    try:
        account = GeneralAC.objects.get(customer=customer)
        return account.balance
    except GeneralAC.DoesNotExist:
        return "N/A"

@register.simple_tag
def customer_regular_target(customer):
    try:
        account = GeneralAC.objects.get(customer=customer)
        return account.regular_target
    except GeneralAC.DoesNotExist:
        return "N/A"
    
@register.simple_tag
def savings_balance(customer):
    try:
        account = SavingsAC.objects.get(customer=customer)
        return account.balance
    except SavingsAC.DoesNotExist:
        return "N/A"
    
@register.simple_tag
def savings_target(customer):
    try:
        account = SavingsAC.objects.get(customer=customer)
        return account.regular_target
    except SavingsAC.DoesNotExist:
        return "N/A"



@register.simple_tag
def total_dps_installments(customer):
    total_installments = DPS.objects.filter(customer=customer).aggregate(total=models.Sum('amount_per_installments'))['total']
    return total_installments if total_installments else ""

@register.simple_tag
def total_dps_balance(customer):
    total_balance = DPS.objects.filter(customer=customer).aggregate(total=models.Sum('balance'))['total']
    return total_balance if total_balance else ""



@register.simple_tag
def total_loan(customer):
    total = LoanAC.objects.filter(customer=customer).aggregate(total=models.Sum('total_amount'))['total']
    return total if total else ""

@register.simple_tag
def loan_paid(customer):
    total = LoanAC.objects.filter(customer=customer).aggregate(total=models.Sum('paid_amount'))['total']
    return total if total else ""

@register.simple_tag
def loan_due(customer):
    loans = LoanAC.objects.filter(customer=customer)
    total_due = sum(loan.due for loan in loans)
    return total_due if total_due else ""

@register.simple_tag
def loan_inst(customer):
    total = LoanAC.objects.filter(customer=customer).aggregate(total=models.Sum('installment_amount'))['total']
    return total if total else ""

@register.simple_tag
def loan_number_of_installments(customer):
    loans = LoanAC.objects.filter(customer=customer)
    
    if not loans.exists():
        return ""
    
    no_inst = sum(loan.number_of_installments for loan in loans)
    paid_inst = sum(loan.paid_installments for loan in loans)
    
    return f'{paid_inst}/{no_inst}'








@register.simple_tag
def total_customer_balance(customers):
    total = GeneralAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('balance'))['total']
    return total if total else 0

@register.simple_tag
def total_customer_target(customers):
    total = GeneralAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('regular_target'))['total']
    return total if total else 0

@register.simple_tag
def total_ss_balance(customers):
    total = SavingsAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('balance'))['total']
    return total if total else 0

@register.simple_tag
def total_ss_target(customers):
    total = SavingsAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('regular_target'))['total']
    return total if total else 0



@register.simple_tag
def sum_total_loan(customers):
    total = LoanAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('total_amount'))['total']
    return total if total else 0

@register.simple_tag
def sum_loan_paid(customers):
    total = LoanAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('paid_amount'))['total']
    return total if total else 0

@register.simple_tag
def sum_loan_inst(customers):
    total = LoanAC.objects.filter(customer__in=customers).aggregate(total=models.Sum('installment_amount'))['total']
    return total if total else 0

@register.simple_tag
def sum_loan_due(customers):
    loans = LoanAC.objects.filter(customer__in=customers)
    total = sum(loan.due for loan in loans)
    return total if total else 0


@register.simple_tag
def sum_dps_balance(customers):
    total = DPS.objects.filter(customer__in=customers).aggregate(total=models.Sum('balance'))['total']
    return total if total else 0

@register.simple_tag
def sum_dps_target(customers):
    total = DPS.objects.filter(customer__in=customers).aggregate(total=models.Sum('amount_per_installments'))['total']
    return total if total else 0

