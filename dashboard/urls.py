from django.urls import path
from . import views

urlpatterns = [
    path('monthly_dashboard/<str:start_date>/<str:end_date>/', views.today_dashboard, name='today_dashboard'),
    path('today_dashboard/', views.today_dashboard, name='today_dashboard_no_date'),
    path('monthly_dashboard/', views.monthly_dashboard, name='monthly_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('general_savings_collection/', views.general_savings_collection, name='general_savings_collection'),
    path('special_savings_collection/', views.special_savings_collection, name='special_savings_collection'),
    path('installments_collection/', views.installments_collection, name='installments_collection'),
    path('cc_loan_collection/', views.cc_loan_collection, name='cc_loan_collection'),
    path('dps_collection/', views.dps_collection, name='dps_collection'),
    path('fdr_collection/', views.fdr_collection, name='fdr_collection'),
    path('share_collection/', views.share_collection, name='share_collection'),
    path('savings_withdraw_collection/', views.savings_withdraw_collection, name='savings_withdraw_collection'),
    path('dps_withdraw_collection/', views.dps_withdraw_collection, name='dps_withdraw_collection'),
    path('fdr_withdraw_collection/', views.fdr_withdraw_collection, name='fdr_withdraw_collection'),
]
