from django.contrib import admin
from .models import Expense, Income, Deposit, Withdraw, Passbook

# @admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('branch', 'somity', 'category', 'CustomerName', 'Amount', 'ExpenseDate', 'VoucherID')

# @admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('branch', 'somity', 'category', 'CustomerName', 'Amount', 'IncomeDate', 'VoucherID')

# @admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('branch', 'Amount', 'Date', 'VoucherID')

# @admin.register(Withdraw)
class Withdrawadmin(admin.ModelAdmin):
    list_display = ('branch', 'Amount', 'Date', 'VoucherID')

# @admin.register(Passbook)
class Passbookadmin(admin.ModelAdmin):
    list_display = ('branch', 'Account', 'Amount', 'Date',)



