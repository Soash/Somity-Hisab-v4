from django import template
from app1.models import DPS, GeneralAC, Loan_CC, LoanAC, SavingsAC
from django.db import models
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def savings_balance(customer):
    try:
        account = GeneralAC.objects.get(customer=customer)
        return account.balance
    except GeneralAC.DoesNotExist:
        return 0

@register.simple_tag
def savings_target(customer):
    try:
        account = GeneralAC.objects.get(customer=customer)
        return account.regular_target
    except GeneralAC.DoesNotExist:
        return 0

@register.simple_tag
def special_balance(customer):
    try:
        account = SavingsAC.objects.get(customer=customer)
        return account.balance
    except SavingsAC.DoesNotExist:
        return 0

@register.simple_tag
def special_target(customer):
    try:
        account = SavingsAC.objects.get(customer=customer)
        return account.regular_target
    except SavingsAC.DoesNotExist:
        return 0


@register.simple_tag
def total_data_count(customer):
    loan_count = LoanAC.objects.filter(customer=customer).count()
    cc_loan_count = Loan_CC.objects.filter(customer=customer).count()
    dps_count = DPS.objects.filter(customer=customer).count()
    x = loan_count + cc_loan_count + dps_count + 2
    return x

@register.simple_tag
def add_loan(customer):
    loans = LoanAC.objects.filter(customer=customer)
    
    details_html = ""
    for loan in loans:
        print(loan.total_amount, loan.paid_amount, loan.due, loan.installment_amount)
        details_html += f'''<tr>
        <td>Loan</td>
        <td class="total">{loan.total_amount}</td>
        <td class="balance">{loan.paid_amount}</td> 
        <td class="due">{loan.due}</td>
        <td class="inst">{loan.installment_amount}</td>
        <td></td><td></td><td></td><td></td><td></td><td></td><td></td>
        </tr>'''
    return mark_safe(details_html)

@register.simple_tag
def add_dps(customer):
    dps = DPS.objects.filter(customer=customer)
    
    details_html = ""
    for info in dps:
        details_html += f'''<tr>
        <td>DPS</td>
        <td class="total">{info.total_amount}</td>
        <td class="balance">{info.balance}</td> 
        <td class="due">{info.due}</td>
        <td class="inst">{info.amount_per_installments}</td>
        <td></td><td></td><td></td><td></td><td></td><td></td><td></td>
        </tr>'''
    return mark_safe(details_html)

@register.simple_tag
def add_cc_loan(customer):
    cc_loan = Loan_CC.objects.filter(customer=customer)
    
    details_html = ""
    for info in cc_loan:
        details_html += f'''<tr>
        <td>CC Loan</td>
        <td class="total">{info.total_amount}</td>
        <td class="balance"></td> 
        <td class="due">{info.due}</td>
        <td class="inst">{info.installment_amount}</td>
        <td></td><td></td><td></td><td></td><td></td><td></td><td></td>
        </tr>'''
    return mark_safe(details_html)