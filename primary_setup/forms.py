from django import forms
from app1.models import Branch

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'branch_short_name', 'mobile_no', 'email', 'telephone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_short_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super(BranchForm, self).save(commit=False)
        for field in self.Meta.fields:
            if getattr(instance, field) is None:
                setattr(instance, field, "")
        if commit:
            instance.save()
        return instance


















