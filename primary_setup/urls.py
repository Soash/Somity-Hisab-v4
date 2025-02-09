from django.urls import path
from . import views

urlpatterns = [
    path('branch-list/', views.branch_list, name='branch_list'),
    path('branch-list/edit/<int:pk>', views.branch_list_edit, name='branch_list_edit'),
]