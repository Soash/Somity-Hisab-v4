from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    branch_short_name = models.CharField(max_length=50)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Somity(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='somity')
    group_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.group_name


class Bank(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='bank')
    bank_name = models.CharField(max_length=100)
    account_no = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.bank_name


class CustomUser(AbstractUser):
    # group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, verbose_name="User Type", related_name='customuser_set')
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name='users', blank=True, null=True)
    somity_group = models.ManyToManyField('Somity', blank=True)

    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    house_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    travel_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mobile_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    internet_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mobile = models.CharField(max_length=20, blank=True, null=True)


class Holiday(models.Model):
    event_name = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.event_name


class LoanCategory(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='Loan', null=True, blank=True)
    category_name = models.CharField(max_length=255)
    profit_rate = models.IntegerField()
    loan_duration = models.IntegerField()
    max_loan_amount = models.IntegerField()

    def __str__(self):
        return self.category_name


class Director(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='director')
    director_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    address = models.CharField(max_length=20, null=True, blank=True)
    profession = models.CharField(max_length=100)
    email = models.EmailField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    photo = models.ImageField(upload_to='director_photos', null=True, blank=True)

    def __str__(self):
        return self.director_name
    


class OutLoan(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='outloan')
    account_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    profession = models.CharField(max_length=50)
    address = models.CharField(max_length=20, null=True, blank=True)
    balance = models.FloatField()
    profit = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return f"{self.account_name}"
    

class VoucherCategory(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    CATEGORY_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    category_type = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    category_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return self.category_name
    

class FDRScheme(models.Model):
    SCHEME_TYPE_CHOICES = (
        ('FIXED', 'Fixed Profit'),
        ('MONTHLY', 'Monthly Profit'),
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='FDR_Scheme')
    scheme_name = models.CharField(max_length=100)
    scheme_type = models.CharField(max_length=50, choices=SCHEME_TYPE_CHOICES)
    duration = models.IntegerField()
    profit_percent = models.FloatField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.scheme_name
    


class DPSScheme(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='DPS_Scheme')
    scheme_name = models.CharField(max_length=100)
    payment_sequence = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return self.scheme_name






class SMSSetting(models.Model):
    STATUS_CHOICES = [
        ('on', 'On'),
        ('off', 'Off'),
    ]
    LANG_CHOICES = [
        ('bangla', 'Bangla'),
        ('english', 'English'),
    ]
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    language = models.CharField(max_length=20, choices=LANG_CHOICES, default='bangla')
    title = models.CharField(max_length=100)
    # content_english = models.TextField()
    content_bengali = models.TextField()

    def __str__(self):
        return f"{self.title}"

