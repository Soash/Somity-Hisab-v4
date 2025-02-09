from django.contrib import admin
from .models import Branch, Somity, Bank, CustomUser, Holiday, LoanCategory, Director, OutLoan, VoucherCategory, FDRScheme, DPSScheme
from django.contrib.auth.admin import UserAdmin
from .models import SMSSetting


class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch_short_name', 'mobile_no', 'email', 'telephone', 'address')


class SomityAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'branch')
    list_filter = ('branch',)


class BankAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_name', 'account_no', 'branch')
    list_filter = ('branch',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username','balance')
    list_filter = ()
    filter_vertical = ('somity_group',)

    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_active', 'is_staff', 'is_superuser')}),
        ('Personal info', {'fields': (('first_name', 'national_id'), ('email', 'mobile'), ('father_name', 'mother_name'), 'address')}),
        # ('Organization', {'fields': (('group', 'branch'), 'date_joined', ('somity_group',))}),
        ('Organization', {'fields': (('branch'), 'date_joined', ('somity_group',))}),
        ('Allowances', {'fields': (('basic_salary', 'house_rent'), ('medical_allowance', 'travel_allowance'), ('mobile_allowance', 'internet_allowance'))}),
        # ('Permissions', {'fields': ('user_permissions', 'groups')}),
        ('Permissions', {'fields': ('groups',)}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2', 'is_active', 'is_staff')}),
        ('Personal info', {'fields': (('first_name', 'national_id'), ('email', 'mobile'), ('father_name', 'mother_name'), 'address')}),
        ('Organization', {'fields': (('branch'), 'date_joined', ('somity_group',))}),
        ('Allowances', {'fields': (('basic_salary', 'house_rent'), ('medical_allowance', 'travel_allowance'), ('mobile_allowance', 'internet_allowance'))}),
        # ('Permissions', {'fields': ('user_permissions', 'groups')}),
        ('Permissions', {'fields': ('groups',)}),
    )


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'date')
    ordering = ('date',)


class LoanCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'category_name', 'profit_rate', 'loan_duration', 'max_loan_amount')


class DirectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'director_name', 'designation', 'mobile_number', 'profession', 'email', 'balance', 'status')
    list_filter = ('branch',)


class OutLoanAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'company_name', 'mobile_number', 'profession', 'balance', 'profit', 'status')


class VoucherCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_type', 'category_name', 'status')


class FDRSchemeAdmin(admin.ModelAdmin):
    list_display = ('scheme_name', 'branch', 'scheme_type', 'duration', 'profit_percent', 'note')


class DPSSchemeAdmin(admin.ModelAdmin):
    list_display = ('scheme_name', 'payment_sequence', 'status', 'branch')



class SMSSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'language', 'content_bengali')
    # save_on_top = True



admin.site.register(Branch, BranchAdmin)
admin.site.register(Somity, SomityAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(LoanCategory, LoanCategoryAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(OutLoan, OutLoanAdmin)
admin.site.register(VoucherCategory, VoucherCategoryAdmin)
admin.site.register(FDRScheme, FDRSchemeAdmin)
admin.site.register(DPSScheme, DPSSchemeAdmin)
admin.site.register(SMSSetting, SMSSettingAdmin)

