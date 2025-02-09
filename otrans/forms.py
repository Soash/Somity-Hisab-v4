from django import forms
from .models import Expense, Income, Deposit, Withdraw, Passbook, SSM_Deposit, SSM_Withdraw
from primary_setup.models import Somity, Director, CustomUser, VoucherCategory
from app1.models import ActiveBranch
import random
import string


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'somity', 'voucher_category', 'CustomerName', 'Amount',
            'ExpenseBy', # 'IsCalculateWithLossProfit', 
            'ExpenseDate', 'Note'
        ]

        widgets = {
            'ExpenseDate': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'somity': 'Somity',
            'CustomerName': 'Customer Name',
            'Amount': 'Expense Amount',
            'ExpenseBy': 'Expense By',
            #'IsCalculateWithLossProfit': 'Is calculate with Loss/Profit ?',
            'ExpenseDate': 'Expense Date',
            'Note': 'Additional Note',
            'voucher_category': 'Voucher Category'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()

            self.fields['somity'].queryset = Somity.objects.filter(branch=active_branch.branch)

            self.fields['voucher_category'].queryset = VoucherCategory.objects.filter(
                branch=active_branch.branch, 
                category_type='EXPENSE'
            )
   
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'



class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            'somity', 'voucher_category', 'CustomerName', 'Amount',
            'IncomeBy', #'IsCalculateWithLossProfit', 
            'IncomeDate', 'Note'
        ]
        widgets = {
            'IncomeDate': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'somity': 'Somity',
           'voucher_category': 'Voucher Category',
            'CustomerName': 'Customer Name',
            'Amount': 'Income Amount',
            'IncomeBy': 'Income By',
            #'IsCalculateWithLossProfit': 'Is calculate with Loss/Profit ?',
            'IncomeDate': 'Income Date',
            'Note': 'Additional Note'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(IncomeForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()

            self.fields['somity'].queryset = Somity.objects.filter(branch=active_branch.branch)
            self.fields['voucher_category'].queryset = VoucherCategory.objects.filter(
                branch=active_branch.branch, 
                category_type='INCOME'
            )
 
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'



class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = [
            'director', 'Amount', 'Date', 'Note'
        ]
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'director': 'Director',
            'Amount': 'Deposit Amount',
            'Date': 'Date',
            'Note': 'Additional Note'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DepositForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()
            if active_branch:
                self.fields['director'].queryset = Director.objects.filter(branch=active_branch.branch)
            else:
                self.fields['director'].queryset = Director.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if value in [None, '']:
                cleaned_data[field] = ''
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'



class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = [
            'director', 'Amount', 'Date', 'Note'
        ]
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'director': 'Director',
            'Amount': 'Withdraw Amount',
            'Date': 'Date',
            'Note': 'Additional Note'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(WithdrawForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()
            if active_branch:
                self.fields['director'].queryset = Director.objects.filter(branch=active_branch.branch)
            else:
                self.fields['director'].queryset = Director.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if value in [None, '']:
                cleaned_data[field] = ''
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'
    


class PassbookForm(forms.ModelForm):
    class Meta:
        model = Passbook
        fields = [
            'Date', 'Account', 'Amount',  'Note'
        ]
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'Account': 'Account',
            'Amount': 'Amount',
            'Date': 'Date',
            'Note': 'Note'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PassbookForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if value in [None, '']:
                cleaned_data[field] = ''
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'
    


class ssmDepositForm(forms.ModelForm):
    class Meta:
        model = SSM_Deposit
        fields = [
            'staff', 'Amount', 'Date', 'Note'
        ]
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'staff': 'Staff',
            'Amount': 'Deposit Amount',
            'Date': 'Date',
            'Note': 'Additional Note'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ssmDepositForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()
            if active_branch:
                self.fields['staff'].queryset = CustomUser.objects.filter(branch=active_branch.branch)
            else:
                self.fields['staff'].queryset = CustomUser.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if value in [None, '']:
                cleaned_data[field] = ''
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'




class ssmWithdrawForm(forms.ModelForm):
    class Meta:
        model = SSM_Withdraw
        fields = [
            'staff', 'Amount', 'Date', 'Note'
        ]
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'staff': 'Staff',
            'Amount': 'Withdraw Amount',
            'Date': 'Date',
            'Note': 'Additional Note'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ssmWithdrawForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()
            if active_branch:
                self.fields['staff'].queryset = CustomUser.objects.filter(branch=active_branch.branch)
            else:
                self.fields['staff'].queryset = CustomUser.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if value in [None, '']:
                cleaned_data[field] = ''
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.VoucherID:
            instance.VoucherID = self.generate_voucher_id()
        if commit:
            instance.save()
        return instance

    def generate_voucher_id(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'vch{random_string}'







from django import forms
from .models import GetOutLoan

class GetOutLoanForm(forms.ModelForm):
    class Meta:
        model = GetOutLoan
        fields = ['date', 'account', 'current_amount', 'deposit_amount', 'profit', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'text'}),
            'note': forms.TextInput(attrs={'type': 'text'}),
            'current_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
        labels = {
            'profit': 'Deposit Profit',
        }




class ReturnOutLoanForm(forms.ModelForm):
    class Meta:
        model = GetOutLoan
        fields = ['date', 'account', 'current_amount', 'deposit_amount', 'profit', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'text'}),
            'note': forms.TextInput(attrs={'type': 'text'}),
            'current_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
        labels = {
            'deposit_amount': 'Withdraw Amount',
            'profit': 'Withdraw Profit',
        }

