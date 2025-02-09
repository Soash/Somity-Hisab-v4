from django import template
from app1.models import DPS, GeneralAC, SavingsAC
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
    # Sum up the amount_per_installments for all DPS accounts of a customer
    total_installments = DPS.objects.filter(customer=customer).aggregate(total=models.Sum('amount_per_installments'))['total']
    return total_installments if total_installments else 0

@register.simple_tag
def total_dps_balance(customer):
    # Sum up the balance for all DPS accounts of a customer
    total_balance = DPS.objects.filter(customer=customer).aggregate(total=models.Sum('balance'))['total']
    return total_balance if total_balance else 0




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
def sum_dps_balance(customers):
    total = DPS.objects.filter(customer__in=customers).aggregate(total=models.Sum('balance'))['total']
    return total if total else 0

@register.simple_tag
def sum_dps_target(customers):
    total = DPS.objects.filter(customer__in=customers).aggregate(total=models.Sum('amount_per_installments'))['total']
    return total if total else 0

