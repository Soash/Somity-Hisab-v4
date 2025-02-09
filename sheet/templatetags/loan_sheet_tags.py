from django import template
from app1.models import DPS, GeneralAC, Loan_CC, LoanAC, SavingsAC
from django.db import models

register = template.Library()
    

@register.filter
def due_profit(loan):
    return loan.due * (loan.profit_percent / 100)

@register.filter
def due_principal(loan):
    due_profit = loan.due * (loan.profit_percent / 100)
    return loan.due - due_profit


@register.filter
def total_total_amount(loans):
    return sum(loan.total_amount for loan in loans)

@register.filter
def total_paid_amount(loans):
    return sum(loan.paid_amount for loan in loans)

@register.filter
def total_installment_amount(loans):
    return sum(loan.installment_amount for loan in loans)

@register.filter
def total_due_principal(loans):
    total_due_principal = 0
    for loan in loans:
        due_profit = loan.due * (loan.profit_percent / 100)
        total_due_principal += loan.due - due_profit
    return total_due_principal

@register.filter
def total_due_profit(loans):
    return sum(loan.due * (loan.profit_percent / 100) for loan in loans)

