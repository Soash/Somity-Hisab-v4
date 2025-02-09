from django.urls import path
from . import views

urlpatterns = [
    path('daily-loan-report/', views.daily_loan_report, name='daily_loan_report'),
    path('weekly-loan-report/', views.weekly_loan_report, name='weekly_loan_report'),
    path('monthly-loan-report/', views.monthly_loan_report, name='monthly_loan_report'),
    path('report/loan-due-list/', views.loan_due_list, name='loan_due_list'),
    path('report/loan-recovery-percentage/', views.loan_recovery_percentage, name='loan_recovery_percentage'),
    path('customer-report', views.customer_report, name='customer_report'),
    path('customer-balance', views.customer_balance, name='customer_balance'),
    path('bank-transactions', views.bank_transactions, name='bank_transactions'),

    path('monthly_top_sheet_report/', views.monthly_top_sheet_report, name='monthly_top_sheet_report'),
    path('monthly_wise_top_sheet_report/', views.monthly_wise_top_sheet_report, name='monthly_wise_top_sheet_report'),

    path('fixed_deposit_report/', views.fixed_deposit_report, name='fixed_deposit_report'),
    path('dps_report/', views.dps_report, name='dps_report'),
    path('share_report/', views.share_report, name='share_report'),
    path('voucher_report/', views.voucher_report, name='voucher_report'),
    path('loanOC_report/', views.loanOC_report, name='loanOC_report'),
    path('balance_sheet/', views.balance_sheet, name='balance_sheet'),
    path('user_log/', views.user_log, name='user_log'),
    path('user_entry_summary/', views.user_entry_summary, name='user_entry_summary'),
    path('user_wise_entry_summary/', views.user_wise_entry_summary, name='user_wise_entry_summary'),
    path('general_ledger/', views.general_ledger, name='general_ledger'),
    path('ReceivePayment/', views.ReceivePayment, name='ReceivePayment'),
    path('ProfitLoss/', views.ProfitLoss, name='ProfitLoss'),
    path('account_statement/', views.account_statement, name='account_statement'),
]
