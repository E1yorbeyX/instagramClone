from datetime import date
import re
import phonenumbers
import threading
from django.core.mail import EmailMessage
from decouple import config
from twilio.rest import Client
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError

email_regex = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")
phone_regex = re.compile(r"(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")
username_regex = re.compile(r"^[a-z0-9_-]{3,15}$")

def check_email_or_phone(email_or_phone):
    try:
       phone_number = phonenumbers.parse(email_or_phone)
    except:
        pass
    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = "email"
    elif phonenumbers.is_valid_number(phone_number):
        email_or_phone = "phone"
    else:
        data = {  # Xatolik ma'lumotlari.
            "success": False,  # Amal muvaffaqiyatsiz.
            "message": "Email yoki telefon raqamingiz notogri"  # Xatolik xabari.
        }
        raise ValidationError(data)

    return email_or_phone

def check_user_input(userinput):
    try:
       phone_number = phonenumbers.parse(email_or_phone)
    except:
        pass
    if re.fullmatch(email_regex, userinput):
        userinput="email"
    elif re.fullmatch(phone_regex, userinput):
        userinput="phone"
    elif re.fullmatch(username_regex, userinput):
        userinput="username"
    else:
        data = {
            "success":False,
            "message":"Bu joyga email, telefon raqam yoki username kiritishingiz mumkin"
        }
        raise ValidationError(data)
    
    return userinput

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Email:
    @staticmethod
    def send_mail(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type')=="html":
            email.content_type="html"
        EmailThread(email).start()

def send_mail(email, code):
    html_content = render_to_string(
        'email/authenticated/activate_account.html',
        {"code":code}
    )
    Email.send_mail(
        {
            "subject":"Ro'yxatdan o'tish",
            "to_email":email,
            "body":html_content,
            "content_type":"html"   
        }
    )

def send_number(phone, code):
    account_sid = config("account_sid")
    auth_token = config("auth_token")
    client = Client(account_sid, auth_token)
    client.message.create(
        body = f"Salom og'a sizga tasdiqlash kodi tayyorladik ishlatib kuring {code}\n",
        from_ = "+9998942014721",
        to = f"{phone}"
    )