from django.shortcuts import render,redirect
from landload.models import TenentProfileVerify,Property,Rooms,Tenant,AddressHistory,DocumentOthers,\
    professionHistory
from landload.forms import TenantInviteReadOnlyForm,TenantStep1Form,AddressHistoryForm,TenantProfessionForm,\
        TenantBankForm,TenantDocumentsForm
from users.models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
# Create your views here.
@login_required(login_url='/')
def index(request):
    tenant=Tenant.objects.filter(user=request.user).first()
    is_locked=False if tenant.is_agree else True
    if is_locked:
        return redirect('tenant:tenant_step1')
    return render(request,'tenant/index.html',{"is_locked":is_locked})


@login_required(login_url='/')
def tenantverify(request, id):
    if (TenentProfileVerify.objects.filter(link=id,verify=False).exists()):
        obj = TenentProfileVerify.objects.get(link=id,verify=False)
        logout(request)
        if request.method == "POST":
            try:
                print('8'*100)
                password = request.POST.get('password1')
                con_pass = request.POST.get('password2')
                if password == con_pass:
                    change_pass = CustomUser.objects.get(email=obj.user)
                    change_pass.set_password(password)
                    change_pass.save()
                    obj.verify=True
                    obj.save()
                    try:
                        newuser = authenticate(request, email=obj.user, password=password)
                    except Exception as e :
                        print(e)
                    if newuser is not None:
                        login(request, newuser)
                        messages.success(request,'Password Set successfully')
                        return redirect('tenant:home')
                else:
                    messages.error(request, 'Password not match')
                    return redirect('tenant:home')
            except Exception as e :
                print(e)
            
        return render(request,'registration/tenant_set_pass.html')
    else:
        messages.error(request, f'Invalid Token')
        return redirect('tenant:home')


# def tenantverify(request, id):
#     if (TenentProfileVerify.objects.filter(link=id).exists()):
#         obj = TenentProfileVerify.objects.get(link=id)
#         property = Property.objects.filter(landload=obj.tenant.landload,is_active=True)
#         room = Rooms.objects.filter(property=obj.tenant.property)
#         form=TenantInviteReadOnlyForm(instance=obj.tenant)
#         if request.method == "POST":
#             post_data = request.POST.copy()
#             post_data['is_active']=True
#             form = TenantInviteReadOnlyForm(post_data, request.FILES, instance=obj.tenant)
#             if form.is_valid():
#                 user = obj.tenant.user
#                 user.first_name = form.cleaned_data.get('first_name', user.first_name)
#                 user.middle_name = form.cleaned_data.get('middle_name', user.middle_name)
#                 user.last_name = form.cleaned_data.get('last_name', user.last_name)
#                 user.email = form.cleaned_data.get('email', user.email)
#                 user.phone_number = form.cleaned_data.get('phone_number', user.phone_number)
#                 password = request.POST.get('password1')
#                 con_pass = request.POST.get('password2')
#                 user.is_verify=True
#                 user.is_active=True
#                 print(password,con_pass)
#                 # print(obj.user)
#                 if password == con_pass:
#                     user.set_password(password)
#                 else:
#                     messages.error(request, 'Password not match')
#                     return redirect('tenant:home')
#                 user.save()
#                 obj1=form.save(commit=False)
#                 obj1.user=user
#                 obj1.save()
#                 obj.verify = True
#                 obj.save()
#                 messages.success(request, f'Profile has been Created successfully!')
#                 return redirect('tenant:home')
#             else:
#                 print(form.errors)
#                 messages.error(request, f'{form.errors}')

#         return render(request,'tenant/tenant_profile.html',{'form':form,'property':property,'tenant_obj':obj.tenant,'room':room})
#     else:
#         messages.error(request, f'Invalid token')
#         return redirect('tenant:home')


@login_required
def tenant_step1(request):
    tenant = Tenant.objects.filter(user=request.user, is_active=True).first()
    form = TenantStep1Form(instance=tenant)
    is_locked=False if tenant.is_agree else True
    if not tenant:
        tenant = Tenant(user=request.user)
    if not tenant.property:
        return render(request, 'tenant/onboad_message.html', {'tenant_obj':tenant,"is_locked":is_locked})
    if request.method == 'POST':
        print('*'*1000)
        agree_data=request.POST.get('agree')
        print(agree_data)
        if agree_data:
            tenant.is_agree=True if agree_data else False
            tenant.save()
            messages.success(request,'On boading completed')
            return redirect('tenant:home')
        # form = TenantStep1Form(request.POST, instance=tenant)
        # if form.is_valid():
        #     tenant = form.save(commit=False)
        #     tenant.user = request.user
        #     tenant.landload = tenant.property.landload
        #     tenant.save()
        #     request.session['tenant_id'] = tenant.id
    
    form = TenantStep1Form(instance=tenant)
    formaddress=AddressHistoryForm()
    form2=TenantProfessionForm(instance=tenant)
    addhistory=AddressHistory.objects.filter(tenant=tenant)
    professhistory=professionHistory.objects.filter(tenant=tenant)
    form3=TenantBankForm(instance=tenant)
    form4=TenantDocumentsForm(instance=tenant)

    return render(request, 'tenant/step1.html', {'tenant_obj':tenant,'form': form,'form2':form2,'form3':form3,\
                                                  'step': 1,"is_locked":is_locked,'is_onbonding':True,'formaddress':formaddress,\
                                                    'form4':form4,'addhistory':addhistory,'professhistory':professhistory,'tenant':tenant})

def submit_step(request, step):
    if request.method == 'POST':
        tenant = Tenant.objects.filter(user=request.user, is_active=True).first()
        post_data = request.POST.copy()
        post_data['is_active']=True
        if step == '1':
            form = TenantStep1Form(request.POST, instance=tenant)
            first_name=request.POST.get('first_name')
            middle_name=request.POST.get('middle_name')
            last_name=request.POST.get('last_name')
            email=request.POST.get('email')
            phone_number=request.POST.get('phone_number')
            user=CustomUser.objects.get(id=request.user.id)
            user.first_name=first_name if first_name else request.user.first_name
            user.middle_name=middle_name if middle_name else request.user.middle_name
            user.last_name=last_name if last_name else request.user.last_name
            user.email=email if email else request.user.email
            user.phone_number=phone_number if phone_number else request.user.phone_number
            user_data=user.save()
            AddressHistory.objects.filter(tenant=tenant).delete()
            if form.is_valid():
                tenant = form.save()
                other_landlord_name = []
                other_landlord_contact = []
                other_history_email = []
                other_history_from_date = []
                other_history_to_date = []
                other_line1 = []
                other_line2 = []
                other_city = []
                other_country = []
                other_postcode = []

                for key in post_data:
                    if 'landlord_name' in key:
                        other_landlord_name.append(post_data[key])
                    if 'landlord_contact' in key:
                        other_landlord_contact.append(post_data[key])
                    if 'history_email' in key:
                        other_history_email.append(post_data[key])
                    if 'history_from_date' in key:
                        other_history_from_date.append(post_data[key])
                    if 'history_to_date' in key:
                        other_history_to_date.append(post_data[key])
                    if 'line1' in key:
                        other_line1.append(post_data[key])
                    if 'line2' in key:
                        other_line2.append(post_data[key])
                    if 'city' in key:
                        other_city.append(post_data[key])
                    if 'country' in key:
                        other_country.append(post_data[key])
                    if 'postcode' in key:
                        other_postcode.append(post_data[key])

                for landlord_name, landlord_contact,history_email,history_from_date,history_to_date, \
                    line1,line2,city,country,postcode in zip(other_landlord_name, other_landlord_contact,other_history_email,
                                                                         other_history_from_date,other_history_to_date,
                                                                         other_line1,other_line2,other_city,other_country,other_postcode):
                    if landlord_name.strip() or landlord_contact.strip() or history_email or history_from_date or \
                        history_to_date or line1 or line2 or city or country or postcode:
                        AddressHistory.objects.update_or_create(
                            tenant=tenant,
                            landlord_name=landlord_name,landlord_contact=landlord_contact,
                            landlord_email=history_email,from_date=history_from_date,
                            to_date=history_to_date,line1=line1,line2=line2,city=city,country=country,
                            postcode=postcode
                        )

                return JsonResponse({'success': True,"formid":'formid'})
            else:
                print('error',form.errors)
                return JsonResponse({'success': False,"formid":form.errors})
            
        elif step == '2':
            form = TenantProfessionForm(request.POST, instance=tenant)

            if form.is_valid():
                professionHistory.objects.filter(tenant=tenant).delete()
                tenant = form.save()
                other_employer_name = []
                other_employer_address = []
                other_employment_From = []
                other_employment_to = []
                other_salary = []
                for key in post_data:
                    if 'history_employer_name' in key:
                        other_employer_name.append(post_data[key])
                    if 'history_employer_address' in key:
                        other_employer_address.append(post_data[key])
                    if 'history_employment_From' in key:
                        other_employment_From.append(post_data[key])
                    if 'history_employment_to' in key:
                        other_employment_to.append(post_data[key])
                    if 'history_salary' in key:
                        other_salary.append(post_data[key])

                for employer_name, employer_address,employment_From,employment_to,salary \
                    in zip(other_employer_name, other_employer_address,other_employment_From,
                        other_employment_to,other_salary):
                    
                    if employer_name.strip() or employer_address.strip() or employment_From or employment_to or \
                        salary:
                        professionHistory.objects.update_or_create(
                            tenant=tenant,
                            history_employer_name=employer_name,history_employer_address=employer_address,
                            history_employment_From=employment_From,history_employment_to=employment_to,
                            history_salary=salary
                        )
                return JsonResponse({'success': True,"formid":'formid'})
            else:
                print('error',form.errors)
                return JsonResponse({'success': False,"formid":form.errors})
            
        elif step == '3':
            form = TenantBankForm(request.POST, instance=tenant)
            if form.is_valid():
                tenant = form.save()
                return JsonResponse({'success': True,"formid":'formid'})
            else:
                print('error',form.errors)
                return JsonResponse({'success': False,"formid":form.errors})
        elif step == '4':
            form = TenantDocumentsForm(request.POST,request.FILES, instance=tenant)
            if form.is_valid():
                other_document_type = []
                other_upload_document = []
                tenant = form.save()
                DocumentOthers.objects.filter(tenant=tenant).delete()
                for key in post_data:
                    if 'document_type' in key:
                        other_document_type.append(post_data[key])
                for key in request.FILES:
                    if 'upload_document' in key:
                        other_upload_document.append(request.FILES[key]) 
                for _type, _doc in zip(other_document_type, other_upload_document):
                    if _type.strip() or _doc.strip():
                        DocumentOthers.objects.create(
                            tenant=tenant,
                            document_type=_type,
                            upload_document=_doc    
                        )
                return JsonResponse({'success': True,"formid":'formid'})
            else:
                print('error',form.errors)
                return JsonResponse({'success': False,"formid":form.errors})

