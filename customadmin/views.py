from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import LandloadEmailVerify
from users.models import CustomUser
from users.email import sent_invitation
from django.contrib.sites.shortcuts import get_current_site
from users.email import account_activation_mail,account_rejected_mail
from landload.models import LandlordProfile

# Create your views here.
def index(request):
    return render(request,'customadmin/index.html')




@login_required(login_url='/user')
def landload_list(request):
    obj=request.GET.get('search')
    data = CustomUser.objects.filter(role='landload').order_by('-id')
    landload_request=CustomUser.objects.filter(role='landload',status='watting').count()
    if obj in ['watting','approved','rejected']:
        data = CustomUser.objects.filter(role='landload',status=obj).order_by('-id')
    landload=CustomUser.objects.filter(role='landload').count()
    tenet=CustomUser.objects.filter(role='tenant').count()
    all_user=CustomUser.objects.all().count()
    return render(request,'customadmin/app-user-list.html',{
        "data":data,"all_user":all_user,"landload":landload,
        "tenet":tenet,"landload_request":landload_request
    })

def payment_token(request,pk):
    obj=LandlordProfile.objects.filter(landlord__id=pk).first()
    if request.method=="POST":
        token = get_random_string(6)
        obj.payment_code=token
        obj.save()
    return render(request,'customadmin/payment_token.html',{'obj':obj})


@login_required(login_url='')
def delete_landload(request,id):
    pass

@login_required(login_url='')
def approve_landload(request,pk):
    obj=CustomUser.objects.get(id=pk)
    obj.is_active=True
    obj.status='approved'
    obj.is_verify=True
    obj.save()
    account_activation_mail(
        obj.first_name+obj.last_name if obj.last_name else "",
        obj.email)
    return JsonResponse(True,safe=False)

@login_required(login_url='/user')
def reject_landload(request,pk):
    obj=CustomUser.objects.get(id=pk)
    obj.is_active=False
    obj.status='rejected'
    obj.save()
    account_rejected_mail(
        obj.first_name+obj.last_name if obj.last_name else "",
        obj.email)
    return JsonResponse(True,safe=False)



def landload(request):
    landload = CustomUser.objects.filter(is_active=True,status='landload') 
    return render(request,'customadmin/landload.html',{'landload':landload})

def add_landload(request):
    token=''
    form=CustomUserCreationForm()
    if request.method=="POST":
        post_data = request.POST.copy()
        post_data['password1'] = "Root@123"
        post_data['password2'] = "Root@123"
        form=CustomUserCreationForm(post_data)
        email=request.POST.get('email')

        if form.is_valid():
            # signup_as = form.cleaned_data['role']
            preobj=form.save(commit=False)
            preobj.is_active=True
            preobj.role='landload'
            preobj.save()
            email1 = CustomUser.objects.get(email=email)
            token = get_random_string(16)
            # print('token is',token)
            LandloadEmailVerify(user_id=email1.id, link=token).save()
            messages.success(request,'Invite has been send.')

            token = 'http://'+str(get_current_site(request).domain)+'/admin/setuplandload/' + token
            sent_invitation(token, email1)
            msg = 'The activation link has been send to your Email.'
            return redirect('customadmin:landload')
        else:
            messages.error(request,form.errors)
    return render(request,'customadmin/add_landload.html',{'form':form})

def delete_landload(request,id):
    leave_type = get_object_or_404(CustomUser, id=id)
    leave_type.is_active = False
    leave_type.save()
    messages.success(request, f'Landload has been deleted successfully!')
    return redirect('customadmin:landload')

def setuplandload(request,id):
    obj = LandloadEmailVerify.objects.get(link=id)
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
        return render(request, 'registration/create_password.html')
        # return render(request, 'html/ltr/vertical-menu-template/page-auth-reset-password-v1.html')
    messages.error(request, 'This link not valid')
    return redirect('user:forgetpassword')