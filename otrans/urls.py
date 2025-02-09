from django.urls import path
from . import views

urlpatterns = [
    path('general_expense/', views.general_expense, name='general_expense'),
    path('general_income/', views.general_income, name='general_income'),
    path('director_deposit/', views.director_deposit, name='director_deposit'),
    path('director_withdraw/', views.director_withdraw, name='director_withdraw'),
    path('passbook/', views.passbook, name='passbook'),
    path('ssm_deposit/', views.ssm_deposit, name='ssm_deposit'),
    path('ssm_withdraw/', views.ssm_withdraw, name='ssm_withdraw'),
    path('get_out_loan/', views.get_out_loan, name='get_out_loan'),
    path('return_out_loan/', views.return_out_loan, name='return_out_loan'),
    path('staff_salary_sheet/', views.staff_salary_sheet, name='staff_salary_sheet'),
    path('save_salary/', views.save_salary, name='save_salary'),
    path('delete_salary/<int:pk>/', views.delete_salary, name='delete_salary'),
    path('profit_generate_monthly/', views.profit_generate_monthly, name='profit_generate_monthly'),

    path('expense/print/<int:pk>/', views.expense_print, name='expense_print'),
    path('income/print/<int:pk>/', views.income_print, name='income_print'),
    path('deposit/print/<int:pk>/', views.deposit_print, name='deposit_print'),
    path('withdraw/print/<int:pk>/', views.withdraw_print, name='withdraw_print'),
    path('passbook/print/<int:pk>/', views.passbook_print, name='passbook_print'),
    path('ssm_deposit/print/<int:pk>/', views.ssm_deposit_print, name='ssm_deposit_print'),
    path('ssm_withdraw/print/<int:pk>/', views.ssm_withdraw_print, name='ssm_withdraw_print'),

    path('expense/delete/<int:pk>/', views.expense_delete, name='expense_delete'),
    path('income/delete/<int:pk>/', views.income_delete, name='income_delete'),
    path('passbook/delete/<int:pk>/', views.passbook_delete, name='passbook_delete'),
    path('profit-distribution-history/', views.profit_distribution_history, name='profit_distribution_history'),
]