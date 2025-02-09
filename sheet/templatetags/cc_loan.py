from django import template
from app1.models import DPS, GeneralAC, Loan_CC, SavingsAC
from django.db import models

register = template.Library()
    
@register.simple_tag
def cc_loan_amount(customer):
    total = Loan_CC.objects.filter(customer=customer).aggregate(total=models.Sum('total_amount'))['total']
    return total if total else 0

@register.simple_tag
def cc_loan_paid(customer):
    total = Loan_CC.objects.filter(customer=customer).aggregate(total=models.Sum('paid_amount'))['total']
    return total if total else 0

@register.simple_tag
def cc_loan_due(customer):
    loans = Loan_CC.objects.filter(customer=customer)
    total_due = sum(loan.due for loan in loans)
    return total_due if total_due else 0

@register.simple_tag
def cc_loan_installment(customer):
    total = Loan_CC.objects.filter(customer=customer).aggregate(total=models.Sum('installment_amount'))['total']
    return total if total else 0

@register.simple_tag
def total_cc_loan_amount(customers):
    total = Loan_CC.objects.filter(customer__in=customers).aggregate(total=models.Sum('total_amount'))['total']
    return total if total else 0

@register.simple_tag
def total_cc_paid_amount(customers):
    total = Loan_CC.objects.filter(customer__in=customers).aggregate(total=models.Sum('paid_amount'))['total']
    return total if total else 0

@register.simple_tag
def total_cc_installment_amount(customers):
    total = Loan_CC.objects.filter(customer__in=customers).aggregate(total=models.Sum('installment_amount'))['total']
    return total if total else 0

@register.simple_tag
def total_cc_due_amount(customers):
    loans = Loan_CC.objects.filter(customer__in=customers)
    total_due = sum(loan.due for loan in loans)
    return total_due if total_due else 0

