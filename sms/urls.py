from django.urls import path
from . import views

urlpatterns = [
    path('sms_single/', views.sms_single, name='sms_single'),
    path('sms_bulk/', views.sms_bulk, name='sms_bulk'),
    path('sms_customer/', views.sms_customer, name='sms_customer'),
    path('sms_report/', views.sms_report, name='sms_report'),
]