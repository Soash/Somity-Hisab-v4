from django.db import models
import random
import string
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from otrans.models import Passbook
from django.contrib.auth.models import Group
from primary_setup.models import Branch, FDRScheme, Somity, LoanCategory, Holiday, CustomUser, DPSScheme, Bank
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, PermissionsMixin, Group


class ActiveBranch(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, default=1)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CustomerManager(BaseUserManager):
    def create_user(self, account_no, password, **extra_fields):
        if not account_no:
            raise ValueError('The Account Number must be set')
        if not password:
            raise ValueError('The Password must be set')

        user = self.model(account_no=account_no, **extra_fields)
        user.password = password  # Store the password as plain text
        user.save(using=self._db)
        return user

    def create_superuser(self, account_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(account_no, password, **extra_fields)


class Customer(AbstractBaseUser):
    CUSTOMER_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('half_monthly', 'Half Monthly'),
        ('monthly', 'Monthly'),
        ('half_yearly', 'Half Yearly'),
        ('yearly', 'Yearly'),
    ]
    RELIGION_CHOICES = [
        ('islam', 'Islam'),
        ('hinduism', 'Hinduism'),
        ('buddhism', 'Buddhism'),
        ('christianity', 'Christianity'),
        ('other', 'Other'),
    ]
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    group = models.ForeignKey(Somity, on_delete=models.CASCADE)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES)
    joining_date = models.DateField()
    account_no = models.CharField(max_length=20, unique=True)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    admission_form_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pass_book = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    special_savings_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    password = models.CharField(max_length=100)  # Consider removing this field if using Django's built-in password management
    general_savings_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    add_share_ac = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nominee = models.CharField(max_length=100, blank=True, null=True)

    customer_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    national_id_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES, default='Islam')
    customer_father = models.CharField(max_length=100, blank=True, null=True)
    customer_mother = models.CharField(max_length=100, blank=True, null=True)
    secondary_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()

    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    signature_card = models.ImageField(upload_to='signature_cards/', blank=True, null=True)
    national_id_copy = models.ImageField(upload_to='national_id_copies/', blank=True, null=True)

    current_village = models.CharField(max_length=100, blank=True, null=True)
    current_post_office = models.CharField(max_length=100, blank=True, null=True)
    current_thana = models.CharField(max_length=100, blank=True, null=True)
    current_district = models.CharField(max_length=100, blank=True, null=True)

    permanent_village = models.CharField(max_length=100, blank=True, null=True)
    permanent_post_office = models.CharField(max_length=100, blank=True, null=True)
    permanent_thana = models.CharField(max_length=100, blank=True, null=True)
    permanent_district = models.CharField(max_length=100, blank=True, null=True)

    nominee_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_relation = models.CharField(max_length=100, blank=True, null=True)
    nominee_father = models.CharField(max_length=100, blank=True, null=True)
    nominee_mother = models.CharField(max_length=100, blank=True, null=True)
    nominee_national_id = models.CharField(max_length=20, blank=True, null=True)
    nominee_mobile_number = models.CharField(max_length=15, blank=True, null=True)
    nominee_address = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')

    USERNAME_FIELD = 'account_no'
    REQUIRED_FIELDS = ['customer_name']

    objects = CustomerManager()

    # groups = models.ManyToManyField(Group, related_name='customer_set', blank=True)
    # user_permissions = models.ManyToManyField(Permission, related_name='customer_set', blank=True)

    def __str__(self):
        return self.customer_name
    def check_password(self, raw_password):
        return self.password == raw_password


@receiver(post_save, sender=Customer)
def create_general_ac(sender, instance, created, **kwargs):
    if created:
        # print('ok')
        GeneralAC.objects.create(customer=instance, balance=instance.general_savings_amount)
        SavingsAC.objects.create(customer=instance, balance=instance.special_savings_amount)
        
        if instance.add_share_ac == 'Yes':
            ShareAC.objects.create(
                customer=instance,
                nominee=instance.nominee,
                balance=instance.previous_balance,
            )

        if instance.pass_book:
            # print('ok')
            Passbook.objects.create(
                customer=instance,
                Amount=instance.pass_book,
                Account=instance.account_no,
                branch=instance.branch
            )


class GeneralAC(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Close', 'Close'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    regular_target = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_withdraw = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.customer.customer_name} - {self.status}"

class GeneralDeposit(models.Model):
    general = models.ForeignKey(GeneralAC, on_delete=models.CASCADE, related_name='general_deposit')

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)

    VoucherID = models.CharField(max_length=50, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DPS Deposit : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

class GeneralWithdraw(models.Model):
    general = models.ForeignKey(GeneralAC, on_delete=models.CASCADE, related_name='general_withdraw')

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)

    VoucherID = models.CharField(max_length=50, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DPS Deposit : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

class GeneralTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    general = models.ForeignKey(GeneralAC, on_delete=models.CASCADE, related_name='general_transaction_history')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    VoucherID = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.Amount} on {self.created_at}"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)




class SavingsAC(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Close', 'Close'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    regular_target = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_withdraw = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.customer.customer_name} - {self.status}"

class SavingsDeposit(models.Model):
    general = models.ForeignKey(SavingsAC, on_delete=models.CASCADE, related_name='savings_general_deposit')

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)

    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DPS Deposit : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

class SavingsWithdraw(models.Model):
    general = models.ForeignKey(SavingsAC, on_delete=models.CASCADE, related_name='savings_general_withdraw')

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)

    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DPS Deposit : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

class SavingsTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    general = models.ForeignKey(SavingsAC, on_delete=models.CASCADE, related_name='savings_transaction_history')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    VoucherID = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.Amount} on {self.created_at}"




class LoanAC(models.Model):
    LOAN_SCHEME_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('half_monthly', 'Half Monthly'),
        ('monthly', 'Monthly'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    date = models.DateField()

    loan_scheme = models.CharField(max_length=100, choices=LOAN_SCHEME_CHOICES,)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    profit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    profit_taka = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    number_of_installments = models.IntegerField()

    installment_sequence = models.CharField(max_length=100, blank=True, null=True)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_installment = models.IntegerField(default=0)
    fine_per_missed_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    loan_category = models.ForeignKey(LoanCategory, on_delete=models.CASCADE, blank=True, null=True)

    insurance_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan_form_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    share = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    risk_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_information = models.TextField(blank=True, null=True)
    bank_and_cheque_information = models.TextField(blank=True, null=True)
    transaction_id = models.CharField(max_length=15, unique=True, editable=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='active')

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def due(self):
        return self.total_amount - self.paid_amount
    @property
    def due_profit(self):
        return self.profit_taka - (self.paid_amount/(1+self.profit_percent))
    @property
    def due_principal(self):
        return self.loan_amount - (self.paid_amount - (self.paid_amount/(1+self.profit_percent)))
    @property
    def paid_installments(self):
        return self.installment_schedules.filter(installment_status='paid').count()
    
    @property
    def missed_installments(self):
        return self.installment_schedules.filter(installment_status='due').count()
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        if not self.start_date:
            self.start_date = self.date + timedelta(days=self.start_installment)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Loan : {self.transaction_id}"


    def generate_installment_schedule(self):
        schedule = []
        current_date = self.start_date
        skipped_date = None
        installment_seq = int(self.installment_sequence)
        for i in range(self.number_of_installments):
            # Determine the due date for each installment
            current_date += timedelta(days=installment_seq)
            
            # Check if the due date is in the past
            if current_date < date.today():
                installment_status = 'due'
            else:
                installment_status = '---'

            # Create an installment schedule
            schedule.append(InstallmentSchedule(
                loan=self,
                installment_number=i + 1,
                due_date=current_date,
                amount=self.installment_amount,
                skipped_due_date=skipped_date,
                installment_status=installment_status
            ))

        InstallmentSchedule.objects.bulk_create(schedule)
        self.end_date = schedule[-1].due_date if schedule else self.start_date
        self.save()
        return schedule


    # def generate_installment_schedule(self):
    #     schedule = []
        
    #     start_date = self.date + timedelta(days=self.start_installment)
    #     current_date = start_date
    #     holidays = Holiday.objects.values_list('date', flat=True)

    #     for i in range(self.number_of_installments):
    #         skipped_date = None

    #         # Determine the next installment date
    #         if self.loan_scheme == 'daily':
    #             current_date += timedelta(days=1)
    #         elif self.loan_scheme == 'weekly':
    #             current_date += timedelta(weeks=1)
    #         elif self.loan_scheme == 'half_monthly':
    #             current_date += timedelta(weeks=2)
    #         elif self.loan_scheme == 'monthly':
    #             current_date += timedelta(weeks=4)

    #         # Skip weekends and holidays
    #         while current_date.weekday() == 4 or current_date in holidays:  # 4 is Friday
    #             skipped_date = current_date
    #             current_date += timedelta(days=1)

    #         # Create an installment schedule
    #         schedule.append(InstallmentSchedule(
    #             loan=self,
    #             installment_number=i + 1,
    #             due_date=current_date,
    #             amount=self.installment_amount,
    #             skipped_due_date=skipped_date
    #         ))

    #     InstallmentSchedule.objects.bulk_create(schedule)
    #     self.end_date = schedule[-1].due_date if schedule else self.start_date
    #     self.save()
    #     return schedule

class InstallmentSchedule(models.Model):
    STATUS_CHOICES = [
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('---', '---'),
    ]
    loan = models.ForeignKey(LoanAC, on_delete=models.CASCADE, related_name='installment_schedules')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    skipped_due_date = models.DateField(blank=True, null=True)
    installment_status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='---')
    fine_applied = models.BooleanField(default=False)

    def __str__(self):
        return f"Installment {self.installment_number} for Loan {self.loan.transaction_id} - Due {self.due_date}"

    @property
    def is_skipped(self):
        return self.skipped_due_date is not None

class LoanCollection(models.Model):
    loan = models.ForeignKey(LoanAC, on_delete=models.CASCADE, related_name='loan_collection', default=1)

    Date = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Note = models.CharField(max_length=200, null=True, blank=True)
    VoucherID = models.CharField(max_length=50, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    principal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Collection for : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if self.Date is None:
            self.Date = timezone.now().date()
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        if self.loan:
            profit_percent = self.loan.profit_percent
            self.profit = (profit_percent / 100) * self.Amount
            self.principal = self.Amount - self.profit
        super().save(*args, **kwargs)

class LoanFine(models.Model):
    loan = models.ForeignKey(LoanAC, on_delete=models.CASCADE, related_name='loan_fine', default=1)

    Date = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Fine : {self.loan} - {self.Amount} tk"




class Loan_CC(models.Model):
    SCHEME_CHOICES = [
        ('monthly', 'Monthly'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    date = models.DateField()

    loan_scheme = models.CharField(max_length=100, choices=SCHEME_CHOICES,)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    profit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    profit_taka = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    number_of_installments = models.IntegerField()

    installment_sequence = models.CharField(max_length=100, blank=True, null=True)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_installment = models.IntegerField(default=0)
    fine_per_missed_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    loan_category = models.ForeignKey(LoanCategory, on_delete=models.CASCADE, blank=True, null=True)

    insurance_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan_form_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    share = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    risk_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_information = models.TextField(blank=True, null=True)
    bank_and_cheque_information = models.TextField(blank=True, null=True)
    transaction_id = models.CharField(max_length=15, unique=True, editable=False)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='active')

    @property
    def due(self):
        return self.total_amount - self.paid_amount
    @property
    def due_profit(self):
        return self.profit_taka - (self.paid_amount/(1+self.profit_percent))
    @property
    def due_principal(self):
        return self.loan_amount - (self.paid_amount - (self.paid_amount/(1+self.profit_percent)))

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        if not self.start_date:
            self.start_date = self.date + timedelta(days=self.start_installment)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"Loan : {self.transaction_id}"
    
    def generate_installment_schedule(self):
        schedule = []
        
        start_date = self.date + timedelta(days=self.start_installment)
        current_date = start_date
        holidays = Holiday.objects.values_list('date', flat=True)

        for i in range(self.number_of_installments):
            skipped_date = None

            # Determine the next installment date
            if self.loan_scheme == 'monthly':
                current_date += timedelta(weeks=4)

            # Skip weekends and holidays
            while current_date.weekday() == 4 or current_date in holidays:  # 4 is Friday
                skipped_date = current_date
                current_date += timedelta(days=1)

            # Create an installment schedule
            schedule.append(Loan_CC_InstallmentSchedule(
                loan_cc=self,
                installment_number=i + 1,
                due_date=current_date,
                amount=self.installment_amount,
                skipped_due_date=skipped_date
            ))

        Loan_CC_InstallmentSchedule.objects.bulk_create(schedule)
        self.end_date = schedule[-1].due_date if schedule else self.start_date
        self.save()
        return schedule

class Loan_CC_InstallmentSchedule(models.Model):
    STATUS_CHOICES = [
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('---', '---'),
    ]
    loan_cc = models.ForeignKey(Loan_CC, on_delete=models.CASCADE, related_name='loan_cc_installment_schedules')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    skipped_due_date = models.DateField(blank=True, null=True)
    installment_status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='---')
    fine_applied = models.BooleanField(default=False)

    def __str__(self):
        return f"Installment {self.installment_number} for Loan {self.loan.transaction_id} - Due {self.due_date}"

    @property
    def is_skipped(self):
        return self.skipped_due_date is not None
    
    def __str__(self):
        return f"Installment for Loan: {self.loan_cc}"

class Loan_CC_Collection(models.Model):
    loan_cc = models.ForeignKey(Loan_CC, on_delete=models.CASCADE, related_name='loan_cc_collection')

    Date = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Fine = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)
    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Collection for : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)




class Loan_Special(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='active')
    transaction_id = models.CharField(max_length=15, unique=True, editable=False)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Special Loan : {self.transaction_id}"

class Loan_Special_Collection(models.Model):
    loan = models.ForeignKey(Loan_Special, on_delete=models.CASCADE, related_name='loan_sp_collection')

    Amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Paid Intererst")
    Date = models.DateField(blank=True, null=True)
    Note = models.CharField(max_length=200, null=True, blank=True)
    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Collection for : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)




class DPS(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    created_date = models.DateField()
    dps_scheme = models.ForeignKey(DPSScheme, on_delete=models.CASCADE, default=1)

    amount_per_installments = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.IntegerField()

    profit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    profit_taka = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_per_missed_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    dps_opening_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    dps_closing_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    start_installment = models.IntegerField(default=0)
    leger_no = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    installment_sequence = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=15, unique=True, editable=False)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='active')

    @property
    def paid_installments(self):
        return self.dps_installment_schedules.filter(installment_status='paid').count()
    
    @property
    def due(self):
        return self.total_amount - self.balance

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        if not self.start_date:
            self.start_date = self.created_date + timedelta(days=self.start_installment)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"DPS : {self.transaction_id}"


    def generate_installment_schedule(self):
        schedule = []
        
        start_date = self.created_date + timedelta(days=self.start_installment)
        current_date = start_date
        holidays = Holiday.objects.values_list('date', flat=True)

        # Determine the interval based on the DPS scheme's payment sequence
        if self.dps_scheme.payment_sequence:
            interval_days = self.dps_scheme.payment_sequence
        else:
            interval_days = 1  # Default to daily if no payment_sequence is provided

        for i in range(self.number_of_installments):
            skipped_date = None

            # Determine the next installment date based on the payment sequence
            current_date += timedelta(days=int(interval_days))

            # Skip weekends and holidays
            while current_date.weekday() in [4] or current_date in holidays:  # 5 is Saturday, 6 is Sunday
                skipped_date = current_date
                current_date += timedelta(days=1)

            # Create an installment schedule
            schedule.append(DPSInstallmentSchedule(
                dps=self,
                installment_number=i + 1,
                due_date=current_date,
                amount=self.amount_per_installments,
                skipped_due_date=skipped_date
            ))

        # Bulk create the schedule and update end_date
        DPSInstallmentSchedule.objects.bulk_create(schedule)
        self.end_date = schedule[-1].due_date if schedule else self.start_date
        self.save()
        return schedule

class DPSInstallmentSchedule(models.Model):
    STATUS_CHOICES = [
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('---', '---'),
    ]
    dps = models.ForeignKey(DPS, on_delete=models.CASCADE, related_name='dps_installment_schedules')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    skipped_due_date = models.DateField(blank=True, null=True)
    installment_status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='---')


    def __str__(self):
        return f"Installment {self.installment_number} for DPS {self.dps.transaction_id} - Due {self.due_date}"

    @property
    def is_skipped(self):
        return self.skipped_due_date is not None
    
class DPSDeposit(models.Model):
    dps = models.ForeignKey(DPS, on_delete=models.CASCADE, related_name='dps_deposit')

    Date = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Note = models.CharField(max_length=200, null=True, blank=True)

    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"DPS Deposit : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        if self.Date is None:
            self.Date = timezone.now().date()
        super().save(*args, **kwargs)

class DPSWithdraw(models.Model):
    dps = models.ForeignKey(DPS, on_delete=models.CASCADE, related_name='dps_withdrawals')

    Date = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Note = models.CharField(max_length=200, null=True, blank=True)
    Give_Profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"DPS Withdrawal : {self.VoucherID} - {self.Amount} tk"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

class DPSTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    dps = models.ForeignKey(DPS, on_delete=models.CASCADE, related_name='transaction_history')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    VoucherID = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} on {self.date}"




class FDR(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    scheme  = models.ForeignKey(FDRScheme, on_delete=models.CASCADE, related_name='fdrs')

    start_date = models.DateField()
    end_date = models.DateField()

    opening_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    monthly_profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monthly_profit_taka = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    cheque = models.CharField(max_length=200, null=True, blank=True)
    nominee = models.CharField(max_length=200, null=True, blank=True)

    transaction_id = models.CharField(max_length=15, unique=True, editable=False)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='active')

    last_profit_added = models.DateField(null=True, blank=True)

    @property
    def payable(self):
        return self.monthly_profit_taka - self.paid_profit

    def add_monthly_profit(self):
        monthly_profit = self.monthly_profit_taka / 12

        # specific_date = date(2024, 10, 1)
        specific_date = date.today()

        # if self.last_profit_added and self.last_profit_added.month == date.today().month:
        #     return

        if self.last_profit_added and self.last_profit_added.month == specific_date.month:
            return
        
        self.available_profit += monthly_profit
        # self.last_profit_added = date.today()
        self.last_profit_added = specific_date
        self.save()

        ProfitHistory.objects.create(
            fdr=self,
            profit_added=monthly_profit,
            available_profit=self.available_profit,
            added_on=specific_date,
            current_balance = self.balance_amount,
            current_profit_rate = self.monthly_profit_percentage,
        )

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"FDR : {self.transaction_id}"
    
class FDRTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    fdr = models.ForeignKey(FDR, on_delete=models.CASCADE, related_name='fdr_transaction_history')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.Amount} on {self.created_at}"
    
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)

class ProfitHistory(models.Model):
    fdr = models.ForeignKey('FDR', on_delete=models.CASCADE, related_name='profit_history')
    profit_added = models.DecimalField(max_digits=10, decimal_places=2)
    available_profit = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_profit_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    added_on = models.DateField()

    def __str__(self):
        return f"Profit added: {self.profit_added} on {self.added_on} (FDR: {self.fdr.transaction_id})"
    



class ShareAC(models.Model):
    share_id = models.PositiveIntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    nominee = models.CharField(max_length=255)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    withdraw = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    get_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_withdraw = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.share_id:
            last_share = ShareAC.objects.order_by('-share_id').first()
            self.share_id = (last_share.share_id + 1) if last_share else 1001
        super().save(*args, **kwargs)

class ShareACTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    share_ac = models.ForeignKey(ShareAC, on_delete=models.CASCADE, related_name='share_ac_transaction_history')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.Amount} on {self.created_at}"
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)
    



class BankTransaction(models.Model):
    date = models.DateField()
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='bank_transactions')
    withdraw_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.CharField(max_length=50, blank=True, null=True)
    attachment = models.FileField(upload_to='attachments', blank=True, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    entry_date = models.DateTimeField(default=timezone.now)
    VoucherID = models.CharField(max_length=50, editable=False, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.bank.bank_name} - {self.withdraw_amount}"
    def save(self, *args, **kwargs):
        if not self.VoucherID:
            self.VoucherID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        super().save(*args, **kwargs)






class Package(models.Model):
    client_id = models.CharField(max_length=255, default="1234", blank=True, null=True)
    status = models.CharField(max_length=50, default="Active", blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)
    billing_cycle = models.CharField(max_length=50, default="Monthly", blank=True, null=True)
    package_name = models.CharField(max_length=100, blank=True, null=True)
    limit_customer = models.CharField(max_length=100, default="100", blank=True, null=True)

    def __str__(self):
        return f"{self.package_name} ({self.limit_customer} Members)"


class Logo(models.Model):
    image = models.ImageField(upload_to='logos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    somity_name = models.CharField(max_length=255)  # Added field for somity name

    def __str__(self):
        return f"Logo {self.id} - {self.somity_name}"

    