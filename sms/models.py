from django.db import models

class SMSReport(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    sms_type = models.CharField(max_length=50)  # Type of the SMS, e.g., 'All Customer'
    mobile_number = models.CharField(max_length=15)
    sms_body = models.TextField()
    sent_by = models.CharField(max_length=150)  # Store the username of the user who sent the SMS

    def __str__(self):
        return f"SMS to {self.mobile_number} on {self.date}"


class DomainReport(models.Model):
    date = models.DateTimeField(null=True, blank=True)

