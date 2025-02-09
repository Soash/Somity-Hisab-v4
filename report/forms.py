from django import forms
from primary_setup.models import CustomUser, DPSScheme, LoanCategory, Somity, FDRScheme, VoucherCategory
from app1.models import ActiveBranch
from report.models import UserLog

class GroupSelectionForm(forms.Form):
    group = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        if branch:
            self.fields['group'].queryset = Somity.objects.filter(branch=branch)

class GroupSchemeSelectionForm(forms.Form):
    group = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(), 
        widget=forms.CheckboxSelectMultiple,
        label="Select Somity/Group"
    )
    scheme = forms.ChoiceField(
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('half_monthly', 'Half Monthly'),
            ('monthly', 'Monthly')
        ],
        label="Select Loan Scheme"
    )

    def __init__(self, *args, **kwargs):
        branch = kwargs.pop('branch', None)
        super(GroupSchemeSelectionForm, self).__init__(*args, **kwargs)
        if branch:
            self.fields['group'].queryset = Somity.objects.filter(branch=branch)



class CustomerSearchForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))
    somity = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        if branch:
            self.fields['somity'].queryset = Somity.objects.filter(branch=branch)



class FixedDepositReportForm(forms.Form):
    somity = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    scheme_name = forms.ModelChoiceField(
        queryset=FDRScheme.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('all', 'All'), ('active', 'Active'), ('closed', 'Closed')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No.'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FixedDepositReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['somity'].queryset = Somity.objects.filter(branch=active_branch)
            self.fields['scheme_name'].queryset = FDRScheme.objects.filter(branch=active_branch)


class DPSReportForm(forms.Form):
    somity = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    scheme_name = forms.ModelChoiceField(
        queryset=DPSScheme.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('all', 'All'), ('active', 'Active'), ('closed', 'Closed')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No.'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DPSReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['somity'].queryset = Somity.objects.filter(branch=active_branch)
            self.fields['scheme_name'].queryset = DPSScheme.objects.filter(branch=active_branch)


class ShareReportForm(forms.Form):
    somity = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No.'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ShareReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['somity'].queryset = Somity.objects.filter(branch=active_branch)


class VoucherReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=True
    )
    status = forms.ChoiceField(
        choices=[('Income', 'Income'), ('Expense', 'Expense')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    voucher_category = forms.ModelChoiceField(
        queryset=VoucherCategory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
    )
    # user = forms.ModelChoiceField(
    #     queryset=CustomUser.objects.none(),
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     required=False,
    # )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(VoucherReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['voucher_category'].queryset = VoucherCategory.objects.filter(branch=active_branch)
            # self.fields['user'].queryset = CustomUser.objects.filter(branch=active_branch)



class LoanOCReportForm(forms.Form):
    somity = forms.ModelMultipleChoiceField(
        queryset=Somity.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    loan_category = forms.ModelChoiceField(
        queryset=LoanCategory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    loan_scheme = forms.ChoiceField(
        choices=[('all', 'All'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('half_monthly', 'Half Monthly'), ('monthly', 'Monthly')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('all', 'All'), ('active', 'Active'), ('paid', 'Paid')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No.'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LoanOCReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['somity'].queryset = Somity.objects.filter(branch=active_branch)
            self.fields['loan_category'].queryset = LoanCategory.objects.filter(branch=active_branch)


class UESReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    staff = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UESReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['staff'].queryset = CustomUser.objects.filter(branch=active_branch)
    

class UWESReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UWESReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
    

class GeneralLedgerForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    staff = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No.'}),
        required=False
    )
    action = forms.ChoiceField(
        choices=[('', 'Select Action')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(GeneralLedgerForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch
            self.fields['staff'].queryset = CustomUser.objects.filter(branch=active_branch)

        # Populate the action field with unique actions from UserLog
        unique_actions = UserLog.objects.exclude(action__isnull=True).exclude(action__exact='').values_list('action', flat=True).distinct()
        action_choices = [(action, action) for action in unique_actions]
        self.fields['action'].choices += action_choices
    

class ReceivePaymentReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReceivePaymentReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch

class ProfitLossReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfitLossReportForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.get(user=user).branch


from django import forms
import calendar
from datetime import datetime

MONTH_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
YEAR_CHOICES = [(str(year), str(year)) for year in range(2020, datetime.now().year + 1)]

class ReportForm(forms.Form):
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label='Month',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        label='Year',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    report_type = forms.ChoiceField(
        choices=[('all', 'All'), ('income', 'Income'), ('expense', 'Expense')],
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class MonthWiseTopSheetForm(forms.Form):
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        label='Year',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    report_type = forms.ChoiceField(
        choices=[('all', 'All'), ('income', 'Income'), ('expense', 'Expense')],
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )



from django import forms

class AccountStatementForm(forms.Form):
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No.'}),
        required=True
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date From'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Date To'}),
        required=False
    )
    
    ACCOUNT_TYPE_CHOICES = [
        ('all', 'All Types'),
        ('general', 'General Savings'),
        ('special', 'Special Savings'),
        ('share', 'Share AC'),
        ('fdr', 'FDR Account'),
        ('dps', 'DPS Savings'),
        ('loan', 'Loan Investment'),
        ('cc_loan', 'CC Loan'),
        # ('special_loan', 'Special Loan'),
    ]
    
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
