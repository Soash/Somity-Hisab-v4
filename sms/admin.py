from django.contrib import admin
from .models import DomainReport, SMSReport

@admin.register(SMSReport)
class SMSReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'sms_type', 'mobile_number', 'sent_by', 'sms_body')  # Fields to display in the list view
    search_fields = ('mobile_number', 'sms_type', 'sent_by')  # Fields to search in the admin interface
    list_filter = ('sms_type', 'date')  # Add filters for the list view
    ordering = ('-date',)  # Order by date descending

# admin.site.register(DomainReport)