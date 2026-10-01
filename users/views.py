from http import cookies
from http.client import responses
from django.views import generic
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ResetPasswordForm
from django.core.mail import send_mail
from .models import ForgetPassMailVerify#, FpoEmailVerify
from .models import CustomUser,UserEmailVerify,UserNumberVerify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
import urllib.request
import urllib.parse
from .email import verification_mail
from django.utils.safestring import mark_safe
from datetime import timedelta
import re
import random
from django.urls import reverse
from django.utils.http import urlencode
from landload.models import Tenant
from django.utils import timezone

def generate_otp():
    return str(random.randint(100000, 999999))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('user:login'))

def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        print(email)
        password = request.POST.get('password', None)
        login_as = request.POST.get('login_as', None)

        print(password)
        if email is not None and password is not None:
            try:
                usercheck=CustomUser.objects.get(email=email)
            except:
                try:
                    usercheck=CustomUser.objects.get(email=email,is_active=False)
                except:
                    messages.error(request, 'No account found' )

                    return render(request, 'registration/login.html', {'user': request.user})

            if usercheck.is_verify==False:
                if not usercheck.is_superuser==True:
                    msg="Please Verify your email."
                    messages.error(request, msg)
                    return render(request, 'registration/login.html', {'user': request.user})

            user = authenticate(request, email=email, password=password)
            print('user:',user)
            if user is not None:
                login(request, user)
                print('for checking',user.role,login_as)
                if user.is_superuser:
                    return HttpResponseRedirect(reverse_lazy('customadmin:home'))
                if user.role==login_as:
                    print('login sus')
                    if login_as=='admin':
                        return HttpResponseRedirect(reverse_lazy('customadmin:home'))
                    elif login_as=='landload':
                        return HttpResponseRedirect(reverse_lazy('landload:home'))

                    else:
                        return HttpResponseRedirect(reverse_lazy('tenant:home'))
                else:
                    msg=f'You are not registered as {login_as}'
            else:
                msg='Invalid Password'
                messages.error(request, msg)
                return render(request, 'registration/login.html', {'user': request.user,'email': email,
                'role': login_as})

            messages.error(request, msg)
    return render(request, 'registration/login.html', {'user': request.user})

def adminlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        print(email)
        password = request.POST.get('password', None)

        print(password)
        if email is not None and password is not None:
            user = authenticate(request, email=email, password=password)
            print('user:',user)
            if user.is_superuser:
                login(request, user)
                print('for checking')
                return HttpResponseRedirect(reverse_lazy('customadmin:home'))
            else:
                messages.error('You Are not registered as admin')
    return render(request, 'registration_old/login.html', {'user': request.user})

def signup(request):
    form=CustomUserCreationForm()
    if request.method=="POST":
        form=CustomUserCreationForm(request.POST)
        email=request.POST.get('email')
        existing_user = CustomUser.objects.filter(email=email).first()
        
        if existing_user:
            email_verify = UserEmailVerify.objects.filter(user=existing_user, verify=False).first()
            if email_verify:
                url = reverse('user:resend_verification')
                query_string = urlencode({'email': email})
                full_url = f"{url}?{query_string}"
                messages.error(request, 
                    f'Account already exists but not verified yet. <a href="{full_url}">Click here to resend verification email</a>')
                return render(request, "registration/signup.html", {'form': form})
            else:
                messages.error(request, 'Email already registered and verified. Try logging in.')
                return render(request, "registration/signup.html", {'form': form})
        if form.is_valid():
            
            signup_as = form.cleaned_data['role']
            preobj=form.save(commit=False)
            preobj.is_landload=True if signup_as=='landload' else False
            preobj.is_active=False
            preobj.save()
            if signup_as=='tenant':
                Tenant.objects.create(user=preobj)
            otp = generate_otp()
            email1 = CustomUser.objects.get(email=email)
            UserNumberVerify.objects.create(user=preobj)
            messages.success(request,'Please Verify your email.')
            token = get_random_string(16)
            UserEmailVerify(user=email1, link=token,otp=otp,verify=False).save()
            temp_url=redirect('user:userverify', id=token)
            token = 'http://'+str(get_current_site(request).domain)+str(temp_url.url)
            verification_mail(token, email,otp,preobj)
            msg = 'The activation link has been send to your Email.'
            # return redirect('user:login')
            return redirect('user:verify_otp', id=preobj.id)
        else:
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    return render(request,'registration/signup.html',{'form':form})

def resend_verification(request):
    email = request.GET.get('email')
    user = CustomUser.objects.filter(email=email).first()
    
    if user:
        otp = generate_otp()
        token = get_random_string(16)
        # link = request.build_absolute_uri(reverse('verify_otp_link', args=[user.id]))
        
        # Update or create OTP record
        obj, created = UserEmailVerify.objects.update_or_create(
            user=user, verify=False,
            defaults={'otp': otp, 'link': token}
        )
        temp_url=redirect('user:userverify', id=token)
        token = 'http://'+str(get_current_site(request).domain)+str(temp_url.url)
        verification_mail(token, email,otp,user)
        messages.success(request, "Verification email resent.")
    
    return redirect('user:verify_otp', id=user.id)

def verify_otp(request, id):
    user = CustomUser.objects.get(id=id)
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_number')
        print('eeeeeeeeeeee:',entered_otp)
        try:
            otp_obj = UserEmailVerify.objects.filter(user=user, verify=False).latest('created_at')
            if otp_obj.otp == entered_otp:
                
                otp_obj.verify = True
                otp_obj.save()
                user.is_active = True
                user.is_verify= True
                user.save()
                messages.success(request, "Email verified successfully!")
                return redirect('user:login')
                
            else:
                messages.error(request, "Invalid OTP.")
        except UserEmailVerify.DoesNotExist:
            messages.error(request, "OTP verification failed.")
    return render(request, 'registration/otpverify.html', {'user': user})

def forgetpassword(request):
    form = ResetPasswordForm()
    msg = 'Enter your email and we will send you instructions to reset your password'
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        email = request.POST.get('forgot-password-email')
        # email = request.POST.get('email')
        # print(print'the email is',email)
        if (CustomUser.objects.filter(email=email).exists()):
            email = CustomUser.objects.get(email=email)
            token = get_random_string(16)
            # print('token is',token)
            ForgetPassMailVerify(user_id=email.id, link=token).save()
            # token = 'http://127.0.0.1:8000/user/forgetpassword/' + token
            temp_url=redirect('user:create_password', id=token)
            token = 'http://'+str(get_current_site(request).domain)+str(temp_url.url)
            # print('the whole url is ',token)

            email_send(token, email,email_message='Please verify your email for changing the password',email_subject='Reset Password')
            msg = 'The activation link has been send to your Email.'
            messages.success(request,msg)
        else:
            messages.error(request, 'email is not exists')
        # print('the email is', email)

    # return render(request,'user_basic.html')
    return render(request, 'registration/password_reset.html',
                  {'form': form, 'msg': msg})
    # return render(request, 'html/ltr/vertical-menu-template/page-auth-forgot-password-v1.html',
    #               {'form': form, 'msg': msg})
def email_send(token, email,email_message,email_subject):
    # send_mail(
    #     email_subject,
    #     email_message +' '+ token,
    #     # 'radiantinfonet901@gmail.com',
    #     # 'mohdkaif@radiantinfonet.com',
    #     # 'support@radiantinfonet.com',
    #     # 'admin@navankur.org',
    #     'support@navankur.org',
    #     # 'kkaifkhan1040@gmail.com',
    #     [email],  #target email
    #     # fail_silently=False,
    # )
    email = EmailMessage(
    email_subject,
    email_message +' '+ token,
    'support@navankur.org',
    [email],
    # from_email='mohdkaif@radiantinfonet.com',
    headers={'Message-ID': '1'},

)
    email.send(fail_silently=False)
def create_password(request, id):
    if (ForgetPassMailVerify.objects.filter(link=id).exists()):
        obj = ForgetPassMailVerify.objects.get(link=id)
        if timezone.now() - obj.created_at > timedelta(hours=24):
            messages.error(request, 'This link has expired.')
            return redirect('user:forgetpassword')

        if obj.verify == False:
            if request.method == 'POST':
                password = request.POST.get('reset-password-new')
                con_pass = request.POST.get('reset-password-confirm')
                print(password,con_pass)
                # print(obj.user)
                if password == con_pass:
                    change_pass = CustomUser.objects.get(email=obj.user)
                    change_pass.set_password(password)
                    change_pass.save()
                    obj.verify = True
                    obj.save()
                    messages.success(request, 'Password change successfully!Please Login')
                    return redirect('user:login')
                else:
                    messages.error(request, 'Password not match')
            return render(request, 'registration/reset-password.html')
            # return render(request, 'html/ltr/vertical-menu-template/page-auth-reset-password-v1.html')
        messages.error(request, 'This link not valid')
    return redirect('user:forgetpassword')

def userverify(request, id):
    if (UserEmailVerify.objects.filter(link=id).exists()):
        obj = UserEmailVerify.objects.get(link=id)
        obj.verify = True
        obj.save()
        obj1 = CustomUser.objects.get(email=obj.user.email)
        msg = 'Thank you! Your email address is now verified Please login'
        # if obj1.role=="tenant":
        obj1.is_active = True
        obj1.is_verify = True
        obj1.save()
            # msg='Email verified successfully Please login'
        messages.success(request, msg)
    return redirect('user:login')

def checkemail(request):
    # email_template = "email/invitation.html"
    # context_data = {'data': 'kaifkhan'}
    # objectdata_rendered = Template(objectdata.body).render(Context(context_data))
    return render(request,'email/tenant_invitation.html',#{'object':objectdata,"data":"kaif","objectdata_rendered":objectdata_rendered}
                  )
