from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
import requests 
import openpyxl
from app1.models import ActiveBranch, Customer
from sms.models import SMSReport

from environ import Env
env = Env()
Env.read_env()

sms_url=env('SMS_URL')
api_key = env('API_Key')
client_id = env('Client_ID')
sender_id = env('Sender_ID')
SMS = env('SMS')


@login_required
@permission_required('sms.add_smsreport', raise_exception=True)
def sms_single(request):
    if request.method == "POST":
        msg = request.POST.get('sms_body')
        
        to_numbers = request.POST.get('mobile').replace(' ', '')
        phone_numbers = to_numbers.split(',')

        response_texts = []
        for number in phone_numbers:
            
            last_11_digits = str(number)[-11:]
            number = "88" + last_11_digits
            
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "senderId": sender_id,
                "is_Unicode": True,
                "message": msg,
                "mobileNumbers": number, 
                "apiKey": api_key,
                "clientId": client_id
            }
            response = requests.post(url=sms_url, headers=headers, json=payload)
            response_data = response.json()

            # Extract the relevant information
            if response_data.get("ErrorCode") == 0 and "Data" in response_data:
                for data in response_data["Data"]:
                    message_error_description = data.get("MessageErrorDescription", "No description")
                    mobile_number = data.get("MobileNumber", "No mobile number")
                    print(f"MessageErrorDescription: {message_error_description}, MobileNumber: {mobile_number}")
                    response_texts.append(f"Message Description: {message_error_description}, Mobile Number: {mobile_number}")
            else:
                print("Error in response or unexpected format.")

            SMSReport.objects.create(
                sms_type="Single SMS",
                mobile_number=number,
                sms_body=msg,
                sent_by=request.user.username)

        context = {
            'response_texts': response_texts
        }
        return render(request, 'sms/sms_single.html', context)
    else:
        return render(request, 'sms/sms_single.html')


@login_required
@permission_required('sms.add_smsreport', raise_exception=True)
def sms_bulk(request):
    if request.method == "POST":
        msg = request.POST.get('sms_body')
        file = request.FILES['filename']

        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        phone_numbers = []
        for row in sheet.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True):
            if row[0]:
                phone_numbers.append(str(row[0]).strip())

        response_texts = []
        for number in phone_numbers:
            last_11_digits = str(number)[-11:]
            number = "88" + last_11_digits
            
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "senderId": sender_id,
                "is_Unicode": True,
                "message": msg,
                "mobileNumbers": number, 
                "apiKey": api_key,
                "clientId": client_id
            }
            response = requests.post(url=sms_url, headers=headers, json=payload)
            response_data = response.json()

            # Extract the relevant information
            if response_data.get("ErrorCode") == 0 and "Data" in response_data:
                for data in response_data["Data"]:
                    message_error_description = data.get("MessageErrorDescription", "No description")
                    mobile_number = data.get("MobileNumber", "No mobile number")
                    print(f"MessageErrorDescription: {message_error_description}, MobileNumber: {mobile_number}")
                    response_texts.append(f"Message Description: {message_error_description}, Mobile Number: {mobile_number}")
            else:
                print("Error in response or unexpected format.")
                
            SMSReport.objects.create(
                sms_type="Bulk SMS",
                mobile_number=number,
                sms_body=msg,
                sent_by=request.user.username)

        context = {'response_text': response_texts}
        return render(request, 'sms/sms_bulk.html', context)
    else:
        return render(request, 'sms/sms_bulk.html')


@login_required
@permission_required('sms.add_smsreport', raise_exception=True)
def sms_customer(request):
    response_texts = [] 
    if request.method == "POST":
        customer_type = request.POST.get('type')
        msg = request.POST.get('sms_body')


        branch = ActiveBranch.objects.get(user=request.user).branch
        customers = Customer.objects.filter(branch=branch)

        if customer_type == "only_active_member":
            customers = customers.filter(status='Active')
        elif customer_type == "all_dps":
            customers = customers.filter(dps__isnull=False).distinct()
        elif customer_type == "only_active_dps":
            customers = customers.filter(dps__status='active').distinct()
        elif customer_type == "all_loan":
            customers = customers.filter(loanac__isnull=False).distinct()
        elif customer_type == "only_active_loan":
            customers = customers.filter(loanac__status='active').distinct()
        elif customer_type == "all_fdr":
            customers = customers.filter(fdr__isnull=False).distinct()
        elif customer_type == "only_active_fdr":
            customers = customers.filter(fdr__status='active').distinct()

        
        for customer in customers:
            number = customer.mobile_number
            last_11_digits = str(number)[-11:]
            number = "88" + last_11_digits
            
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "senderId": sender_id,
                "is_Unicode": True,
                "message": msg,
                "mobileNumbers": number, 
                "apiKey": api_key,
                "clientId": client_id
            }
            response = requests.post(url=sms_url, headers=headers, json=payload)
            response_data = response.json()

            # Extract the relevant information
            if response_data.get("ErrorCode") == 0 and "Data" in response_data:
                for data in response_data["Data"]:
                    message_error_description = data.get("MessageErrorDescription", "No description")
                    mobile_number = data.get("MobileNumber", "No mobile number")
                    print(f"MessageErrorDescription: {message_error_description}, MobileNumber: {mobile_number}")
                    response_texts.append(f"Message Description: {message_error_description}, Mobile Number: {mobile_number}")
            else:
                print("Error in response or unexpected format.")
                
            SMSReport.objects.create(
                sms_type=customer_type,
                mobile_number=number,
                sms_body=msg,
                sent_by=request.user.username
            )

    context = {
        'response_texts': response_texts
    }
    return render(request, 'sms/sms_customer.html', context)


@login_required
@permission_required('sms.add_smsreport', raise_exception=True)
def sms_report(request):
    sms_reports = SMSReport.objects.all().order_by('id')

    context = {
        'sms_reports': sms_reports
    }
    return render(request, 'sms/sms_report.html', context)


