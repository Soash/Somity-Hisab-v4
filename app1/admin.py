from django.contrib import admin
from .models import Customer, ActiveBranch, DPSDeposit, GeneralTransactionHistory, LoanAC, InstallmentSchedule, LoanCollection, DPS, DPSInstallmentSchedule, Logo, Package
from .models import GeneralAC, GeneralWithdraw, GeneralDeposit, FDR, FDRTransactionHistory, SavingsAC, ShareAC
from django.contrib import admin
from .models import ProfitHistory

class ActiveBranchAdmin(admin.ModelAdmin):
    list_display = ('branch', 'user')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('account_no', 'customer_name', 'branch', 'processed_by')
    search_fields = ('account_no',)

from django.contrib import admin
from .models import Customer

# class CustomerAdmin(admin.ModelAdmin):
#     form = CustomerAdminForm
#     list_display = ('account_no', 'customer_name', 'mobile_number', 'branch', 'status')
#     search_fields = ('account_no', 'customer_name', 'mobile_number')



class GeneralACAdmin(admin.ModelAdmin):
    list_display = ('customer', 'customer__account_no', 'status')
    search_fields = ('customer__account_no',)
    

class SavingsACAdmin(admin.ModelAdmin):
    list_display = ('id','customer', 'status')

class ShareACAdmin(admin.ModelAdmin):
    list_display = ('customer', 'balance')

class GeneralDepositAdmin(admin.ModelAdmin):
    list_display = ('VoucherID', 'Amount', 'Note', 'created_at', 'processed_by', 'general')
    search_fields = ('VoucherID',)
    # list_filter = ('created_at', 'processed_by')
    # ordering = ('-created_at',)

class GeneralWithdrawAdmin(admin.ModelAdmin):
    list_display = ('VoucherID', 'Amount', 'Note', 'created_at', 'processed_by', 'general')
    search_fields = ('VoucherID',)
    # list_filter = ('created_at', 'processed_by')
    # ordering = ('-created_at',)


class GeneralTransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('general', 'transaction_type', 'Amount', 'current_balance', 'created_at', 'VoucherID',)
    list_filter = ('transaction_type',)
    search_fields = ('general__id', 'VoucherID',)


admin.site.register(GeneralTransactionHistory, GeneralTransactionHistoryAdmin)


class FDRAdmin(admin.ModelAdmin):
    list_display = ('opening_amount', 'duration', 'monthly_profit_percentage', 'last_profit_added')

class FDRTransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('fdr', 'transaction_type', 'created_at')


class ProfitHistoryAdmin(admin.ModelAdmin):
    list_display = ('fdr', 'profit_added', 'available_profit', 'added_on')
    list_filter = ('added_on', 'fdr')
    search_fields = ('fdr__transaction_id', 'profit_added', 'available_profit')




class LoanACAdmin(admin.ModelAdmin):
    list_display = ('customer', 'customer__account_no',)
    search_fields = ('customer__account_no',)

class LoanCollectionAdmin(admin.ModelAdmin):
    list_display = ('loan', 'Amount', 'VoucherID')
    search_fields = ('VoucherID',)

    def get_customer_account_id(self, obj):
        return obj.loan.customer.account_no if obj.loan and obj.loan.customer else "N/A"
    get_customer_account_id.short_description = 'Customer Account ID'



class DPSAdmin(admin.ModelAdmin):

    list_display = ('customer', 'branch', 'created_date', 'total_amount', 'processed_by')
    search_fields = ('customer__name', 'transaction_id')
    list_filter = ('branch', 'created_date')




class DPSInstallmentScheduleAdmin(admin.ModelAdmin):
    list_display = ('dps', 'installment_number', 'amount', 'due_date', 'skipped_due_date', 'installment_status')
    list_editable = ('installment_status',)  



class InstallmentScheduleAdmin(admin.ModelAdmin):
    list_display = ('loan', 'installment_number', 'amount', 'due_date', 'skipped_due_date', 'installment_status')
    list_editable = ('installment_status',)  




admin.site.register(Customer, CustomerAdmin)
admin.site.register(GeneralAC, GeneralACAdmin)
admin.site.register(SavingsAC, SavingsACAdmin)
admin.site.register(ShareAC, ShareACAdmin)
admin.site.register(DPS, DPSAdmin)
admin.site.register(ActiveBranch, ActiveBranchAdmin)
admin.site.register(LoanAC, LoanACAdmin)
admin.site.register(DPSDeposit)
admin.site.register(InstallmentSchedule, InstallmentScheduleAdmin)
admin.site.register(LoanCollection, LoanCollectionAdmin)
admin.site.register(DPSInstallmentSchedule, DPSInstallmentScheduleAdmin)
admin.site.register(FDR, FDRAdmin)
admin.site.register(GeneralDeposit, GeneralDepositAdmin)
admin.site.register(GeneralWithdraw, GeneralWithdrawAdmin)
admin.site.register(FDRTransactionHistory, FDRTransactionHistoryAdmin)
admin.site.register(ProfitHistory, ProfitHistoryAdmin)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'status', 'start_date', 'expired_date', 'billing_cycle', 'package_name', 'limit_customer')
    search_fields = ('client_id', 'package_name')
    list_filter = ('status', 'billing_cycle')
    
@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('id', 'somity_name', 'uploaded_at')
    
    