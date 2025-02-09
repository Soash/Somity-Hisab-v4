from django.contrib.auth.backends import BaseBackend
from .models import Customer
from django.contrib.auth.backends import ModelBackend
from .models import Customer

class CustomerBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            customer = Customer.objects.get(account_no=username)
            if customer.check_password(password):
                return customer
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None


from django.contrib.auth.backends import BaseBackend
from .models import Customer

class CustomerBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Customer.objects.get(account_no=username)  # Ensure `account_no` is the correct field
            if user and user.password == password:
                return user
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None

