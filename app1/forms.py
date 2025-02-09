from django import forms
from .models import BankTransaction, Customer, DPS, DPSDeposit, DPSWithdraw, LoanAC, LoanCollection, LoanFine, Loan_CC, Loan_CC_Collection, Loan_Special, Loan_Special_Collection
from .models import ActiveBranch, GeneralDeposit, GeneralWithdraw, SavingsDeposit, SavingsWithdraw, FDR
from primary_setup.models import Bank, Somity

from django import forms
from .models import Customer, Somity, ActiveBranch

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ['branch']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CustomerForm, self).__init__(*args, **kwargs)
        
        if user:
            active_branch = ActiveBranch.objects.filter(user=user).first()
            if active_branch:
                # Filter groups based on the active branch
                self.fields['group'].queryset = Somity.objects.filter(branch=active_branch.branch)
            else:
                self.fields['group'].queryset = Somity.objects.none()
        
        self.fields['general_savings_amount'].initial = 0
        self.fields['special_savings_amount'].initial = 0
        
        self.fields['general_savings_amount'].required = True
        self.fields['special_savings_amount'].required = True

    def save(self, commit=True):
        customer = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            customer.password = password  # Save the password as plain text
        if commit:
            customer.save()
        return customer


class GeneralDepositForm(forms.ModelForm):
    class Meta:
        model = GeneralDeposit
        fields = [
            'Amount', 'Note'
        ]

class GeneralWithdrawForm(forms.ModelForm):
    class Meta:
        model = GeneralWithdraw
        fields = [
            'Amount', 'Note'
        ]  



class SavingsDepositForm(forms.ModelForm):
    class Meta:
        model = SavingsDeposit
        fields = [
            'Amount', 'Note'
        ] 

class SavingsWithdrawForm(forms.ModelForm):
    class Meta:
        model = SavingsWithdraw
        fields = [
            'Amount', 'Note'
        ]  



class LoanACForm(forms.ModelForm):
    class Meta:
        model = LoanAC
        fields = [
            'date', 'loan_scheme', 'loan_amount', 'profit_percent', 'profit_taka', 
            'number_of_installments', 'installment_sequence', 'installment_amount',
            'total_amount', 'start_installment', 'fine_per_missed_installment', 
            'loan_category', 'insurance_fee', 'loan_form_fee', 'share', 'stamp_fee',
            'risk_fee', 'other_fee', 'stamp_information', 'bank_and_cheque_information'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
            'loan_amount': forms.NumberInput(attrs={'placeholder': 'Input Loan Amount'}),
            'profit_taka': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'installment_amount': forms.NumberInput(attrs={'readonly': 'readonly', 'placeholder': 'In installment amount'}),
            'total_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'installment_sequence': forms.TextInput(attrs={'readonly': 'readonly'}),
            'fine_per_missed_installment': forms.NumberInput(attrs={'placeholder': 'If miss to submit installment fine will apply'}),
            'insurance_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'loan_form_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'share': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'stamp_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'risk_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'other_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'stamp_information': forms.Textarea(attrs={'placeholder': 'Input stamp information', 'rows': 3}),
            'bank_and_cheque_information': forms.Textarea(attrs={'placeholder': 'Bank and Cheque Information', 'rows': 3}),
        }

class LoanCollectionForm(forms.ModelForm):
    class Meta:
        model = LoanCollection
        fields = ['Amount', 'Date', 'Note', 'fine']
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }

    def __init__(self, *args, loan=None, **kwargs):
        super().__init__(*args, **kwargs)

class LoanFineForm(forms.ModelForm):
    class Meta:
        model = LoanFine
        fields = ['Amount', 'Date', 'Note']
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }



class Loan_CC_Form(forms.ModelForm):
    class Meta:
        model = Loan_CC
        fields = [
            'date', 'loan_scheme', 'loan_amount', 'profit_percent', 'profit_taka', 
            'number_of_installments', 'installment_sequence', 'installment_amount',
            'total_amount', 'start_installment', 'fine_per_missed_installment', 
            'loan_category', 'insurance_fee', 'loan_form_fee', 'share', 'stamp_fee',
            'risk_fee', 'other_fee', 'stamp_information', 'bank_and_cheque_information'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
            'loan_amount': forms.NumberInput(attrs={'placeholder': 'Input Loan Amount'}),
            'profit_taka': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'installment_amount': forms.NumberInput(attrs={'readonly': 'readonly', 'placeholder': 'In installment amount'}),
            'total_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'installment_sequence': forms.TextInput(attrs={'readonly': 'readonly'}),
            'fine_per_missed_installment': forms.NumberInput(attrs={'placeholder': 'If miss to submit installment fine will apply'}),
            'insurance_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'loan_form_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'share': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'stamp_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'risk_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'other_fee': forms.NumberInput(attrs={'placeholder': 'Input amount or keep blank'}),
            'stamp_information': forms.Textarea(attrs={'placeholder': 'Input stamp information', 'rows': 3}),
            'bank_and_cheque_information': forms.Textarea(attrs={'placeholder': 'Bank and Cheque Information', 'rows': 3}),
        }

class Loan_CC_CollectionForm(forms.ModelForm):
    class Meta:
        model = Loan_CC_Collection
        fields = ['Amount', 'Fine', 'Date', 'Note']
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }

    def __init__(self, *args, loan_cc=None, **kwargs):
        super().__init__(*args, **kwargs)



class LoanSpecialForm(forms.ModelForm):
    class Meta:
        model = Loan_Special
        fields = ['start_date', 'end_date', 'amount', 'profit']
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }

    def __init__(self, *args, loan_cc=None, **kwargs):
        super().__init__(*args, **kwargs)

class LoanSpecialCollectionForm(forms.ModelForm):
    class Meta:
        model = Loan_Special_Collection
        fields = ['Amount', 'Date', 'Note']
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text', 'placeholder': 'yyyy-mm-dd'}),
        }
        labels = {
            'Amount': 'Paid Interest',
        }

    def __init__(self, *args, loan=None, **kwargs):
        super().__init__(*args, **kwargs)



class DPSForm(forms.ModelForm):
    class Meta:
        model = DPS
        fields = [
            'created_date', 
            'dps_opening_charge',
            'dps_scheme',
            'start_installment', 
            'amount_per_installments', 
            'leger_no',
            'number_of_installments', 
            'installment_sequence', 
            'profit_percent',
            'profit_taka', 
            'fine_per_missed_installment', 
            'total_amount',
        ]
        widgets = {
            'created_date': forms.DateInput(attrs={'type': 'text'}),
            'dps_opening_charge': forms.NumberInput(attrs={'placeholder': 'Opening Charge'}),
            'dps_scheme': forms.Select(attrs={'placeholder': 'Select DPS Scheme'}),
            'start_installment': forms.NumberInput(attrs={'placeholder': 'Start Installment'}),
            'amount_per_installments': forms.NumberInput(attrs={'placeholder': 'Input Amount Per Installment'}),
            'leger_no': forms.NumberInput(attrs={'placeholder': 'Leger No.'}),
            'installment_sequence': forms.TextInput(attrs={'readonly': 'readonly'}),
            'total_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'number_of_installments': forms.NumberInput(attrs={'placeholder': 'Input Number of Installments'}),
            'profit_percent': forms.NumberInput(attrs={'placeholder': 'Input Profit Percentage'}),
            'profit_taka': forms.NumberInput(attrs={'readonly': 'readonly', 'placeholder': 'Profit in Taka'}),
            'fine_per_missed_installment': forms.NumberInput(attrs={'placeholder': 'Fine per Missed Installment'}),
        }

class DPSDepositForm(forms.ModelForm):
    class Meta:
        model = DPSDeposit
        fields = [
            'Date', 'Amount', 'Fine', 'Note'
        ]
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'text'}),
        }    
        
    def __init__(self, *args, dps=None, **kwargs):
        super().__init__(*args, **kwargs)
    
class DPSWithdrawForm(forms.ModelForm):
    class Meta:
        model = DPSWithdraw
        fields = ['Date', 'Amount', 'Give_Profit', 'Note']
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'date'}),
        }



class FDRForm(forms.ModelForm):
    scheme_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    scheme_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    duration = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    monthly_profit_taka = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    profit_percent = forms.DecimalField(required=False, widget=forms.NumberInput())

    class Meta:
        model = FDR
        fields = [
            'scheme_name',
            'scheme_type',
            'duration',
            'opening_amount',
            'profit_percent',
            'monthly_profit_taka',
            'start_date',
            'note',
            'cheque',
            'nominee',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        scheme = kwargs.pop('scheme', None)
        super(FDRForm, self).__init__(*args, **kwargs)
        if scheme:
            self.fields['scheme_name'].initial = scheme.scheme_name
            self.fields['scheme_type'].initial = scheme.scheme_type
            self.fields['duration'].initial = scheme.duration
            self.fields['profit_percent'].initial = scheme.profit_percent



class BankWithdrawForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ['date', 'bank', 'withdraw_amount', 'note', 'attachment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
            'withdraw_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        active_branch = ActiveBranch.objects.filter(user=self.request.user).first()
        if active_branch:
            self.fields['bank'].queryset = Bank.objects.filter(branch=active_branch.branch)
        else:
            self.fields['bank'].queryset = Bank.objects.none()


class BankDepositForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ['date', 'bank', 'deposit_amount', 'note', 'attachment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
            'withdraw_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        active_branch = ActiveBranch.objects.filter(user=self.request.user).first()
        if active_branch:
            self.fields['bank'].queryset = Bank.objects.filter(branch=active_branch.branch)
        else:
            self.fields['bank'].queryset = Bank.objects.none()



from django import forms
from .models import Customer

class CustomerAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Customer
        fields = '__all__'

