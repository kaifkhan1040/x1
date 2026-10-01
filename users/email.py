import logging
import os
import os.path
# Sending Email
from threading import Thread
from django.conf import settings
from django.core.mail import EmailMultiAlternatives,get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from landload.models import EmailSettings
from babel.numbers import get_currency_symbol
from landload.models import LandlordProfile
# from landload.models import EmailTemplate
logger = logging.getLogger(__name__)


def send(
    to,
    subject,
    html_body,
    text_body=None,
    attachments=[],
    from_email=None,
    cc=None,
    bcc=None,
    smtp_config=None,
):
    if not (isinstance(to, list) or isinstance(to, tuple)):
        to = [to]

    # Remove empty items
    to = [x for x in to if x not in (None, "")]

    if text_body is None:
        text_body = strip_tags(html_body)

    # Convert CC into a list
    if cc and not (isinstance(cc, list) or isinstance(cc, tuple)):
        cc = [cc]

    # Convert BCC into a list
    if bcc and not (isinstance(bcc, list) or isinstance(bcc, tuple)):
        bcc = [bcc]

    # if bcc is None, set a default email as bcc
    if not bcc:
        bcc = []

    try:
        connection = None
        if smtp_config:
            if smtp_config['email_host_password']:
            
                connection = get_connection(
                    host=smtp_config['email_host'],
                    port=smtp_config['email_port'],
                    username=smtp_config['email_host_user'],
                    password=smtp_config['email_host_password'],
                    use_tls=smtp_config.get('use_tls', True),
                    fail_silently=False,
                )
        msg = EmailMultiAlternatives(subject, text_body, to=to,connection=connection)
        if cc:
            msg.cc = cc

        if bcc:
            msg.bcc = bcc
        if smtp_config:
            if smtp_config['from_email']:
                from_email=smtp_config['from_email']
        if from_email:
            msg.from_email = from_email

        msg.attach_alternative(html_body, "text/html")
        for attachment in attachments:
            if attachment:
                # Try to get only filename from full-path
                try:
                    attachment.open()
                except Exception as e:
                    print(str(e))
                attachment_name = os.path.split(attachment.name)[-1]
                msg.attach(attachment_name or attachment.name, attachment.read())
        msg.send()
        return True
    except Exception:
        logger.exception("Unable to send the mail.")
        return False


def send_from_template(to, subject, template, context,mail_setting, **kwargs):
    # print template
    html_body = render_to_string(template, context)
    print("html body: " + html_body)
    print(mail_setting)
    smtp_config=None
    if mail_setting:
        smtp_config = {
            'email_host': mail_setting.email_host,
            'email_port': mail_setting.email_port,
            'email_host_user': mail_setting.email_host_user,
            'email_host_password': mail_setting.email_host_password,
            'from_email':mail_setting.from_email,
            'use_tls': mail_setting.use_tls
        }
    send(to, subject, html_body,from_email='MISU HOUSING',smtp_config=smtp_config, **kwargs)
    return print('send') 

def account_activation_mail(name,email):
    '''just for customized the email via admin'''
    mail_list, email_subject = email, 'Your Account Has Been Approved!'
    email_template = "email/activate.html"
    # objectdata=Email.object.get(id=2)
    context = {
        "data": name,
        # "object":objectdata
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context),
    ).start()

def get_symbol(currency_code):
    try:
        return get_currency_symbol(currency_code, locale='en')
    except:
        return '' 
    
def tenant_invitation_email(name,email,landload,token,tenant,landload_id=None):
    print('&'*1000,landload_id)
    '''just for customized the email via admin'''
    mail_list, email_subject,mail_setting = email, 'Invitation to Complete Your Tenant Profile',None
    email_template = "email/tenant_invitation.html"
    data=LandlordProfile.objects.filter(landlord=landload).first()
    symbol = get_symbol(landload.country.currency)
    if landload_id:
        landload_mail=EmailSettings.objects.filter(landlord=landload_id).first()
        print('landload mail=================>',landload_mail)
        if landload_mail:
            mail_setting=landload_mail
    # objectdata=Email.object.get(id=2)
    context = {
        "name": name,
        "email":email,
        'landload':landload,
        'token':token,
        'tenant':tenant,
        'symbol':symbol
        # "object":objectdata
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context,mail_setting),
    ).start()

def verification_mail(token,email,otp,landload):
    mail_list, email_subject,mail_setting = email, 'Registration Verification',None
    if landload.role=='landload':
        email_subject='Misu Housing - Landlord Signup Verification'
    elif landload.role=='tenant':
        email_subject='Misu Housing - Tenant Signup Verification'
    
    print("pass1")
    # if obj.status == "Waiting":
    #     mail_list = obj.doctors_call.user.email
    #     print("mail_list", mail_list)
    #     email_subject = f"patient {obj.patients_call.user} schedule a {'Emergency' if obj.call_type == 'Emergency' else ''} meeting with you."
    
    email_template = "email/verification.html"
    # context = {
    #     "data": token,
    #     # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    # }
    # email_template = "email/customemail.html"
    # objectdata=EmailTemplate.objects.get(id=2)
    context = {
        "data": token,
        "otp":otp,
        "landload":landload
        # "object":objectdata
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context,mail_setting),
    ).start()


def sent_invitation(token,email):
    mail_list, email_subject = email.email, 'Landload Registration Invitation'
    print("pass1")
    # if obj.status == "Waiting":
    #     mail_list = obj.doctors_call.user.email
    #     print("mail_list", mail_list)
    #     email_subject = f"patient {obj.patients_call.user} schedule a {'Emergency' if obj.call_type == 'Emergency' else ''} meeting with you."
    
    email_template = "email/invitation.html"
    # context = {
    #     "data": token,
    #     # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    # }
    # email_template = "email/customemail.html"
    # objectdata=EmailTemplate.objects.get(id=2)
    context = {
        "token": token,
        "obj":email
        # "object":objectdata
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context),
    ).start()
# from django.template import Template, Context
# def verification_mail(token,email):
#     mail_list, email_subject = email, 'Registration Verification'
#     print("pass1")
#     # if obj.status == "Waiting":
#     #     mail_list = obj.doctors_call.user.email
#     #     print("mail_list", mail_list)
#     #     email_subject = f"patient {obj.patients_call.user} schedule a {'Emergency' if obj.call_type == 'Emergency' else ''} meeting with you."
    
#     # email_template = "email/verification.html"
#     # context = {
#     #     "data": token,
#     #     # "base_url": settings.DOMAIN + settings.MEDIA_URL,
#     # }
#     email_template = "email/customemail.html"
#     objectdata=EmailTemplate.objects.get(id=2)
#     context_data = {
#         # "data": token,
#         "data":token
        
#         # "base_url": settings.DOMAIN + settings.MEDIA_URL,
#     }
#     objectdata_rendered = Template(objectdata.body).render(Context(context_data))
#     context={
#         "objectdata_rendered":objectdata_rendered
#     }
#     Thread(
#         target=send_from_template,
#         args=(mail_list, email_subject, email_template, context),
#     ).start()

def leave_aproved_mail(name,email,obj):
    mail_list, email_subject = email, 'Your Leave Has Been Approved!'
    email_template = "email/leave_aproved.html"
    context = {
        "user": name,
        'obj':obj
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context),
    ).start()

def leave_reject_mail(name,email,obj):
    mail_list, email_subject = email, 'Your Leave Has Been Rejected!'
    email_template = "email/leave_reject.html"
    context = {
        "user": name,
        'obj':obj
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context),
    ).start()

def apply_user_leave(obj, superuser):
    print('email run')
    mail_list, email_subject = superuser.email, 'You have new leave request!'
    email_template = "email/apply_leave.html"
    context = {
        'obj':obj,
        "superuser":superuser,
        
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context),
    ).start()

# def account_activation_mail(name,email):
#     '''just for customized the email via admin'''
#     mail_list, email_subject = email, 'Your Account Has Been Approved!'
#     email_template = "email/customemail.html"
#     objectdata=Email.object.get(id=2)
#     context = {
#         "data": name,
#         "object":objectdata
        
#         # "base_url": settings.DOMAIN + settings.MEDIA_URL,
#     }
#     Thread(
#         target=send_from_template,
#         args=(mail_list, email_subject, email_template, context),
#     ).start()


def account_rejected_mail(name,email):
    mail_list, email_subject = email, 'Update on Your Account Application'
    email_template = "email/reject_account.html"
    context = {
        "data": name,
        # "base_url": settings.DOMAIN + settings.MEDIA_URL,
    }
    Thread(
        target=send_from_template,
        args=(mail_list, email_subject, email_template, context),
    ).start()
    