from django.urls import path
from . import views

urlpatterns = [
    path('select-somity/', views.select_somity, name='select_somity'),
    path('select-somity-loan-cc/', views.select_somity_loan_cc, name='select_somity_loan_cc'),
    path('loan_collection_sheet_filter/', views.loan_collection_sheet_filter, name='loan_collection_sheet_filter'),
    path('collection_sheet_filter/', views.collection_sheet_filter, name='collection_sheet_filter'),
    path('collection_sheet_filter2/', views.collection_sheet_filter2, name='collection_sheet_filter2'),

    path('savings_collection_sheet/<int:somity_id>/', views.savings_collection_sheet, name='savings_collection_sheet'),
    path('cc_loan_collection_sheet/<int:somity_id>/', views.cc_loan_collection_sheet, name='cc_loan_collection_sheet'),
    
    path('loan_collection_sheet/<int:somity_id>/<str:scheme>', views.loan_collection_sheet, name='loan_collection_sheet'),
    path('collection_sheet_1/<int:somity_id>/<str:date>', views.collection_sheet, name='collection_sheet'),
    path('collection_sheet_2/<int:somity_id>/', views.collection_sheet2, name='collection_sheet2'),
]

