from decimal import Decimal
from django import template
from django.db.models import Sum

register = template.Library()

@register.filter
def calculate_percentage(paid_amount, profit_percent):
    try:
        x = (paid_amount * profit_percent) / 100
        return round(x, 2)
    except (TypeError, ZeroDivisionError):
        return 0
    
@register.filter
def calculate_principal(paid_amount, profit_percent):
    try:
        x = paid_amount - ((paid_amount * profit_percent) / 100)
        return round(x, 2)
    except (TypeError, ZeroDivisionError):
        return 0

@register.filter(name='sum')
def sum_list(value):
    return sum(value)

@register.filter
def split(value, delimiter=' '):
    print(delimiter)
    return value.split(delimiter)



@register.filter(name='has_permission')
def has_permission(user, perm_name):
    return user.has_perm(perm_name)




@register.filter
def sum_amounts(transactions, transaction_type):
    total = 0
    for transaction in transactions:
        if transaction.transaction_type == transaction_type:
            total += transaction.Amount
    return total


@register.filter
def sum_loan(queryset, field_name):
    total = Decimal('0.00')
    for obj in queryset:
        value = getattr(obj, field_name, None)
        if value:
            total += value
    return total



@register.filter
def sum_amounts_dps(transactions, transaction_type):
    total = 0
    for transaction in transactions:
        if transaction.transaction_type == transaction_type:
            total += transaction.amount
    return total


