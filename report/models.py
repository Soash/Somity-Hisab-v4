from django.db import models
from django.utils import timezone
from primary_setup.models import Branch, CustomUser
from app1.models import ActiveBranch, Customer, LoanAC
import socket
from django.db.models import Sum

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return str(e)



from django.utils import timezone

class UserLog(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('cash_in', 'Cash In'),
        ('cash_out', 'Cash Out'),
    ]
    CASHFLOW1_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    CASHFLOW2_TYPE_CHOICES = [
        ('receive', 'Receive'),
        ('payment', 'Payment'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    loan = models.ForeignKey(LoanAC, on_delete=models.CASCADE, null=True, blank=True)
    
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=300, null=True, blank=True)
    logs_action = models.CharField(max_length=300, null=True, blank=True)

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, null=True, blank=True)
    cashflow_type1 = models.CharField(max_length=10, choices=CASHFLOW1_TYPE_CHOICES, null=True, blank=True)
    cashflow_type2 = models.CharField(max_length=10, choices=CASHFLOW2_TYPE_CHOICES, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    timestamp = models.DateField(null=True, blank=True)  # Allowing manual input but can be auto-set
    ip_address = models.CharField(max_length=300, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    VoucherID = models.CharField(max_length=50, null=True, blank=True)
    
    trx = models.BooleanField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto set timestamp only if it's not provided
        if self.timestamp is None:
            self.timestamp = timezone.now()

        if not self.ip_address:
            self.ip_address = get_ip_address()

        if not self.branch and self.action not in [1, 2]:
            active_branch = ActiveBranch.objects.filter(user=self.processed_by).first()
            self.branch = active_branch.branch if active_branch else None

        if not self.logs_action:
            if not self.transaction_type and not self.cashflow_type1 and not self.cashflow_type2:
                self.transaction_type = 'cash_in'
                self.cashflow_type1 = 'income'
                self.cashflow_type2 = 'receive'
            if self.trx:
                self.transaction_type = 'cash_out'
                self.cashflow_type1 = 'expense'
                self.cashflow_type2 = 'payment'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.processed_by.username if self.processed_by else 'Unknown'} - {self.transaction_type} at {self.timestamp}"
    
    @staticmethod
    def get_sum_of_amounts_by_action():
        """
        Returns a dictionary with the sum of amounts for each unique action.
        """
        return UserLog.objects.values('action').annotate(total_amount=Sum('amount')).order_by('action')



