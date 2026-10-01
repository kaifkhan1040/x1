from django.shortcuts import render,get_object_or_404,redirect
from .models import Property,Rooms,Tenant,TenentProfileVerify,Payment,FinancialBreakdown,\
    FinancialOtherModel,PropertyImage,Expenses,EmailSettings,Country,LandlordProfile,LandloadDoucment
from .forms import PropertyForm,PropertyReadOnlyForm,RoomsForm,TenantForm,TenantReadOnlyForm,TenantInviteForm,PaymentForm,\
    PaymentReadOnlyForm,FinancialBreakdownform,MultiImageForm,FinancialBreakdownReadOnlyform,MultiImageReadOnlyForm,ExpensesForm,\
    ExpensesReadOnlyForm,TenantStep1Form,EmailSettingsForm,LandlordProfileForm,IdProffForm
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from babel.numbers import get_currency_symbol

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from users.email import tenant_invitation_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from users.forms import SetLocationForm
from django.core.serializers.json import DjangoJSONEncoder
import json
import pytz
from django.db.models.functions import Cast
from django.utils.timezone import now
import datetime
from django.db.models.functions import ExtractMonth
from django.db.models import Sum
from django.db.models import Sum,IntegerField

def get_symbol(currency_code):
    try:
        return get_currency_symbol(currency_code, locale='en')
    except:
        return '' 
    
def property_earning_report(request,year,pro_id):
    print('%'*1000)
    monthly_totals = [0] * 12  
    monthly_exp = [0] * 12
# query payments grouped by month
    payments = (
        Payment.objects.filter(paid_date__year=year,property=pro_id)
        .annotate(month=ExtractMonth("paid_date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )

    # fill list
    for p in payments:
        monthly_totals[p["month"] - 1] = p["total"]
    exp = (
        Expenses.objects.filter(paid_date__year=year,property=pro_id)
        .annotate(month=ExtractMonth("paid_date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )

    # fill list
    for p in exp:
        monthly_exp[p["month"] - 1] = -p["total"]
    payment_by_year={'data':[{'id':1,"chart_data":monthly_totals}],
                     'earning':[{'id':1,"chart_data":monthly_totals}],
                     'expenses':[{'id':1,"chart_data":monthly_exp}]}
    print('monthly_totals',monthly_totals,'monthly_exp',monthly_exp)
    

    # for i in payments:
    #     print(i.amount)
    return JsonResponse(payment_by_year,safe=False)

def earning_report(request,year):
    print('%'*1000)
    monthly_totals = [0] * 12  
    monthly_exp = [0] * 12
# query payments grouped by month
    payments = (
        Payment.objects.filter(paid_date__year=year)
        .annotate(month=ExtractMonth("paid_date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )

    # fill list
    for p in payments:
        monthly_totals[p["month"] - 1] = p["total"]
    exp = (
        Expenses.objects.filter(paid_date__year=year)
        .annotate(month=ExtractMonth("paid_date"))
        .values("month")
        .annotate(total=Sum("amount"))
    )

    # fill list
    for p in exp:
        monthly_exp[p["month"] - 1] = -p["total"]
    payment_by_year={'data':[{'id':1,"chart_data":monthly_totals}],
                     'earning':[{'id':1,"chart_data":monthly_totals}],
                     'expenses':[{'id':1,"chart_data":monthly_exp}]}
    print('monthly_totals',monthly_totals,'monthly_exp',monthly_exp)
    

    # for i in payments:
    #     print(i.amount)
    return JsonResponse(payment_by_year,safe=False)

def monthly_profit_comparison_by_property(request):
    today = now().date()

    # Current month range
    this_month_start = today.replace(day=1)
    this_month_end = today

    # Last month range
    first_day_this_month = today.replace(day=1)
    last_month_end = first_day_this_month - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    properties_data = []
    properties_data_loss=[]

    # Get all properties for this landlord
    properties =properties = Property.objects.filter(
        id__in=Payment.objects.filter(landload=request.user).values_list('property', flat=True).distinct(),
        landload=request.user  # in case Property also has landload field
    )
    print('properties',properties)
    for prop_id in properties:
        # This month totals
        this_month_payments = Payment.objects.filter(
            property_id=prop_id,
            landload=request.user,
            paid_date__range=[this_month_start, this_month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0

        this_month_expenses = Expenses.objects.filter(
            property_id=prop_id,
            landload=request.user,
            paid_date__range=[this_month_start, this_month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0

        this_month_profit = this_month_payments - this_month_expenses

        # Last month totals
        last_month_payments = Payment.objects.filter(
            property_id=prop_id,
            landload=request.user,
            paid_date__range=[last_month_start, last_month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0

        last_month_expenses = Expenses.objects.filter(
            property_id=prop_id,
            landload=request.user,
            paid_date__range=[last_month_start, last_month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0

        last_month_profit = last_month_payments - last_month_expenses
        print('last_month_profit',last_month_profit)
        # Calculate percentage change
        change = None
        status = 'no-data'
        if last_month_profit > 0:
            raw = (this_month_profit - last_month_profit) / last_month_profit * 100
            change = round(raw, 2)
            if change > 0:
                status = 'increase'
            elif change < 0:
                status = 'decrease'
            else:
                status = 'no-change'
            properties_data.append({
            'property_name': prop_id.short_name,
            'last_month_profit': last_month_profit,
            'this_month_profit': this_month_profit,
            'percent_change': change,
            'change_status': status,
            })

        elif last_month_profit < 0:
            if this_month_profit < 0:
                # Both months losses → compare as % improvement in loss
                raw = (this_month_profit - last_month_profit) / abs(last_month_profit) * 100
                print('loss ma ',raw)
                change = round(raw, 2)
                status = 'loss-change'
            elif this_month_profit >= 0:
                raw = (this_month_profit - last_month_profit) / abs(last_month_profit) * 100
                print('loss ma ',raw)
                change = round(raw, 2)
                status = 'loss-to-profit'
            
            properties_data_loss.append({
            'property_name': prop_id.short_name,
            # 'property_name':prop_name,
            'last_month_profit': last_month_profit,
            'this_month_profit': this_month_profit,
            'percent_change': change,
            'change_status': status,
            })

        else:  # last_month_profit == 0
            if this_month_profit != 0:
                status = 'from-zero'
            else:
                status = 'no-change'

        
    return properties_data,properties_data_loss
# Create your views here.
def index(request):
    data=LandlordProfile.objects.filter(landlord=request.user).first()
    total_earnings = Payment.objects.filter(landload=request.user).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expenses.objects.filter(landload=request.user).aggregate(total=Sum('amount'))['total'] or 0
    profit = total_earnings-total_expenses
    listing=Property.objects.filter(landload=request.user)
    payment=Payment.objects.filter(landload=request.user)
    expense=Expenses.objects.filter(landload=request.user)
    # print(request.user.country)
    profit_by_property,loss_by_property=monthly_profit_comparison_by_property(request)
    print(profit_by_property,'loss',loss_by_property)
   
    try:
        symbol = get_symbol(data.currency)
    except:
        symbol=''
    # print('*'*100,symbol)
    is_locked=data.is_locked if data else True
    if is_locked:
        return redirect('landload:onboading')
    tenants_with_properties = Tenant.objects.filter(
                                    landload=request.user,
                                    room__isnull=False
                                ).count()
    total_rooms = Rooms.objects.filter(
                            property__landload=request.user
                        ).aggregate(
                            total=Sum(Cast('room_count', IntegerField()))
                        )['total'] or 0
    empty=total_rooms-tenants_with_properties
    chart_data = {
        "values": [tenants_with_properties, empty],
    }
    return render(request,'landload/index.html',{'is_dashboard':True,'total_earnings':total_earnings,'total_expenses':total_expenses,
                                                 "profit":profit,'symbol':symbol,'listing':total_rooms,'occupied':tenants_with_properties,
                                                 'empty':empty,"chart_data": json.dumps(chart_data),'payment':payment,'expense':expense,
                                                 'profit_by_property':profit_by_property,'loss_by_property':loss_by_property})

def onboad_step(request, step):
    if request.method == 'POST':
        profile, created  = LandlordProfile.objects.get_or_create(landlord=request.user)
        post_data = request.POST.copy()
        if step == '1':
            post_data['landlord']=request.user
            form1=LandlordProfileForm(post_data, instance=profile)
            if form1.is_valid():
                form1.save()
                return JsonResponse({'success': True,"formid":'formid'})
            else:
            # Return form errors if you want to handle invalid data client‑side
                return JsonResponse({'success': False, 'errors': form1.errors}, status=400)
        elif step =='2':
            try:
                first_name=request.POST.get('first_name')
                middle_name=request.POST.get('middle_name')
                last_name=request.POST.get('last_name')
                email=request.POST.get('email')
                phone_number=request.POST.get('phone_number')
                address=request.POST.get('address')
                billing_address=request.POST.get('billing_address')
                user=CustomUser.objects.get(id=request.user.id)
                user.first_name=first_name if first_name else request.user.first_name
                user.middle_name=middle_name if middle_name else request.user.middle_name
                user.last_name=last_name if last_name else request.user.last_name
                user.email=email if email else request.user.email
                user.phone_number=phone_number if phone_number else request.user.phone_number
                user.address=address if address else request.user.address

                user_data=user.save()
                profile.billing_address=billing_address if billing_address else None
                profile.save()
                return JsonResponse({'success': True,"formid":'formid'})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': e.messages}, status=400)
        elif step =='3':
            try:
                files = request.FILES.getlist('id_proff')
                for file in files:
                    LandloadDoucment.objects.create(
                        landlord=profile,
                        upload_document=file
                    )
                return JsonResponse({'success': True,"formid":'formid'})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': e.messages}, status=400)
            
        elif step =='4':
            selected_plan=request.POST.get('selected_plan')
            profile.subscription=selected_plan
            profile.save()
            return JsonResponse({'success': True,"formid":'formid'})
        elif step =='5':
            code=request.POST.get('payment_code')
            if code==profile.payment_code:
                profile.is_locked=False
                profile.save()
                return JsonResponse({'success': True,"formid":'formid'})
            else:
                return JsonResponse({'success': False, 'errors': 'Payment Code is not Valid'}, status=400)





def locationdetails(request):
    
    country_name = request.GET.get("country")
    try:
        country = Country.objects.get(id=country_name)
        tz_list = pytz.country_timezones.get(country.iso.upper(), ['UTC'])
        # print('time=====>>>>>>>>>>>>>>','name:',country.name,tz_list)
        return JsonResponse({
            "currency": country.currency,
            "timezone": [(tz, tz) for tz in tz_list],
        })
    except Country.DoesNotExist:
        return JsonResponse({"error": "Country not found"}, status=404)
    
def onboading(request):
    docland_image_urls=None
    data=LandlordProfile.objects.filter(landlord=request.user).first()
    is_locked=data.is_locked if data else True
    if is_locked==False:
        return redirect('landload:home')
    form1=LandlordProfileForm(instance=data) if data else LandlordProfileForm()
    idproffform=IdProffForm()
    doclandload=None
    if data:
        doclandload=LandloadDoucment.objects.filter(landlord=data)
        docland_image_urls = list(doclandload.values('id','upload_document'))
    
    return render(request,'landload/onboading.html',{'is_dashboard':True,'is_locked':is_locked,'form1':form1,'profile_data':request.user,
                                                     'idproffform':idproffform,'data':data,'doclandload':doclandload,
                                                     'docland_image_urls':docland_image_urls})



@login_required
def setup_location(request):
    if request.user.role != 'landload':
        return redirect('landload:home')
    if request.user.country:  
        return redirect('landload:home') 

    if request.method == 'POST':
        form = SetLocationForm(request.POST)
        if form.is_valid():
            request.user.country = form.cleaned_data['country']
            request.user.save()
            messages.success(request, f'Location Setup successfully!')
            return redirect('landload:home') 
        else:
            print(form.errors)
    else:
        form = SetLocationForm()
    
    return render(request, 'landload/location_setup.html', {'form': form})
@login_required(login_url='/')
def listing(request):
    query = request.GET.get('q', '')
    property = Property.objects.filter(landload=request.user,is_active=True)
   
    if query:
        property = property.filter(
            Q(short_name__icontains=query) |
            Q(custom_id__icontains=query) |
            Q(property_type__icontains=query) |
            Q(postcode__icontains=query)
        )
    return render(request,'landload/listing.html',{'property':property,'search_field':True,'is_listing':True})

@login_required(login_url='/')
def submit_step(request, step):
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['landload']=request.user
        post_data['is_active']=True
        post_data['status']=True
        if step == '1':
            formidtemp=request.POST.get('formid1')
            form = PropertyForm(post_data)
            if formidtemp:
                prodata=Property.objects.filter(id=formidtemp).first()
                if prodata:
                    form = PropertyForm(post_data,instance=prodata)
        elif step == '2':
            post_data2 = request.POST.copy()
            formid = request.POST.get('formid')  
            # other = request.POST.get('other')  
            # if other:
            #     post_data2['other']=other
            property_instance = get_object_or_404(Property, id=formid)
            post_data2['property']=property_instance
            invoice_data = request.POST

            other_labels = []
            other_amounts = []

            for key in invoice_data:
                if 'label' in key:
                    other_labels.append(invoice_data[key])
                if 'amount' in key:
                    other_amounts.append(invoice_data[key])
            tempdatafi=FinancialBreakdown.objects.filter(property=property_instance).first()
            form = FinancialBreakdownform(post_data2)
            if tempdatafi:
                form = FinancialBreakdownform(post_data2,instance=tempdatafi)
            if form.is_valid():
                financial_obj = form.save()
                print('label:',other_labels,other_amounts)

                for label, amount in zip(other_labels, other_amounts):
                    if label.strip() or amount.strip():
                        FinancialOtherModel.objects.create(
                            financial=financial_obj,
                            lable=label,
                            amount=amount
                        )
                
                return JsonResponse({'success': True,"formid":formid})
            else:
                print('*'*100)
                print(form.errors)

            return JsonResponse({'success': False, 'errors': form.errors})

       

        if form.is_valid():
            temp=form.save()
            if temp.number_of_flat:
                for i in range(int(temp.number_of_flat)):
                    Rooms.objects.create(property=temp,room_count=f"{i+1:02}")
            print('temp id',temp.id)
            return JsonResponse({'success': True,"formid":temp.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        
@login_required(login_url='/')      
def listing_add(request):
    data=LandlordProfile.objects.filter(landlord=request.user).first()
    video_form=''
    print('*'*1000,request.method)
    form = PropertyForm()
    form2 =FinancialBreakdownform()
    form3 = MultiImageForm()
    symbol = get_symbol(data.currency)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++',symbol)
    if request.method == "POST":
        formid = request.POST.get('formid2') 
        print('form id',formid)
        property_obj=get_object_or_404(Property, id=formid)
        form = MultiImageForm(request.POST, request.FILES)

        
            # property_instance = Property.objects.create(name="Sample Property")

        for field in ['outside', 'parking', 'garage', 'garden', 'common_area', 'residence']:
            files = request.FILES.getlist(field)
            for file in files:
                PropertyImage.objects.create(
                    property=property_obj,
                    field_type=field,
                    image=file
                )
   

        return redirect('landload:listing') 
        
        # post_data = request.POST.copy()
        # # print('post')
        # # print(request.POST)
        # post_data['landload']=request.user
        # post_data['is_active']=True
        # post_data['status']=True
        # form = PropertyForm(post_data,request.FILES)

        # if form.is_valid():
        #     # form['landload']=request.user
       
        #     property_obj=form.save()
        #     for i in range(int(property_obj.rooms)):
        #         Rooms.objects.create(property=property_obj)
        #     messages.success(request, f'Property has been Created successfully!')
        #     return redirect('landload:listing')
        # else:
        #     # print('errr',form.errors)
        #     error_messages = '<br>'.join(
        #         [f"{error}" for field_errors in form.errors.values() for error in field_errors]
        #     )
        #     messages.error(request, mark_safe(error_messages))
    return render(request,'landload/add_listing.html',{'form':form,'form2':form2,'video_form': video_form,'is_listing':True,'form3':form3,'symbol':symbol})

@login_required(login_url='/')
def listing_view(request,id):
    form2=FinancialBreakdownReadOnlyform()
    property_obj = get_object_or_404(Property, custom_id=id)
    # property_obj2 = get_object_or_404(FinancialBreakdown, property=property_obj.id)
    property_obj2 = FinancialBreakdown.objects.filter(property__custom_id=id).first()
    property_obj3 = PropertyImage.objects.filter(property__custom_id=id).first()
    form3 = MultiImageReadOnlyForm()
    data=LandlordProfile.objects.filter(landlord=request.user).first()
    symbol = get_symbol(data.currency)
    print('data',property_obj2,property_obj)
    if property_obj2:
        form2=FinancialBreakdownReadOnlyform(instance=property_obj2)
    form = PropertyReadOnlyForm(instance=property_obj)
    return render(request,'landload/add_listing.html',{'form':form,'form2':form2,'is_listing':True,
                                                       'property_id':property_obj.id,'property_obj':property_obj,'more_fun':True,
                                                       'property_obj2':property_obj2,'form3':form3,'symbol':symbol})

@login_required(login_url='/')
def listing_dashboard(request,id):
    form2=FinancialBreakdownReadOnlyform()
    property_obj = get_object_or_404(Property, custom_id=id)
    all_rooms = property_obj.room_set.all().count()
    print('*'*100,all_rooms)
# Occupied rooms (rooms that have at least one tenant)
    occupied_rooms = Rooms.objects.filter(
        property=property_obj,
        tenant__isnull=False   # reverse lookup via Tenant.room
    ).distinct()

    # Empty rooms (rooms without any tenant)
    empty_rooms = Rooms.objects.filter(
        property=property_obj
    ).exclude(
        id__in=occupied_rooms
    )
    print('occ:',occupied_rooms.count(),'emp:',empty_rooms.count())
    # property_obj2 = get_object_or_404(FinancialBreakdown, property=property_obj.id)
    property_obj2 = FinancialBreakdown.objects.filter(property__custom_id=id).first()
    property_obj3 = PropertyImage.objects.filter(property__custom_id=id).first()
    form3 = MultiImageReadOnlyForm()

    print('data',property_obj2,property_obj)
    if property_obj2:
        form2=FinancialBreakdownReadOnlyform(instance=property_obj2)
    form = PropertyReadOnlyForm(instance=property_obj)
    chart_data = {
        "values": [0, 0],
    }
    occupied_vs_advertised=[occupied_rooms.count(),empty_rooms.count()]
    payment=Payment.objects.filter(landload=request.user,property__custom_id=id)
    expense=Expenses.objects.filter(landload=request.user,property__custom_id=id)

    return render(request,'landload/view_listing_dashboad.html',{'form':form,'form2':form2,'is_listing':True,
                                                       'property_id':property_obj.id,"chart_data": json.dumps(chart_data),'property_obj':property_obj,'more_fun':True,
                                                       'property_obj2':property_obj2,'form3':form3,'occupied_vs_advertised':occupied_vs_advertised,
                                                       'total_room':all_rooms,'payment':payment,'expense':expense })

@login_required(login_url='/')
def listing_update(request,id):
    property_obj = get_object_or_404(Property, pk=id)
    outside_images = PropertyImage.objects.filter(property=property_obj, field_type='outside')
    parking_images = PropertyImage.objects.filter(property=property_obj, field_type='parking')
    garage_images = PropertyImage.objects.filter(property=property_obj, field_type='garage')
    garden_images = PropertyImage.objects.filter(property=property_obj, field_type='garden')
    common_area_images = PropertyImage.objects.filter(property=property_obj, field_type='common_area')
    residence_images = PropertyImage.objects.filter(property=property_obj, field_type='residence')
    outside_image_urls = list(outside_images.values('id','image'))
    parking_image_urls = list(parking_images.values('id','image'))
    garage_image_urls = list(garage_images.values('id','image'))
    garden_image_urls = list(garden_images.values('id','image'))
    common_area_image_urls = list(common_area_images.values('id','image'))
    residence_image_urls = list(residence_images.values('id','image'))
    data=LandlordProfile.objects.filter(landlord=request.user).first()
    symbol = get_symbol(data.currency)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++',symbol)
    property_obj2 = FinancialBreakdown.objects.filter(property=id).first()
    form = PropertyForm(instance=property_obj)
    form2=FinancialBreakdownform()
    if property_obj2:
        form2=FinancialBreakdownform(instance=property_obj2)
    form3 = MultiImageForm()
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['landload']=request.user
        post_data['is_active']=True
        post_data['status']=True
        form = PropertyForm(post_data, request.FILES, instance=property_obj)
        
        formid = request.POST.get('formid2') 
        print('form id',formid)
        # property_obj=get_object_or_404(Property, id=formid)
        form3 = MultiImageForm(request.POST, request.FILES)
        print('update form =========?')
        
            # property_instance = Property.objects.create(name="Sample Property")

        for field in ['outside', 'parking', 'garage', 'garden', 'common_area', 'residence']:
            files = request.FILES.getlist(field)
            print('files',files)
            for file in files:
                PropertyImage.objects.create(
                    property=property_obj,
                    field_type=field,
                    image=file
                )
   
            

        messages.success(request, f'Property has been updated successfully!')
        return redirect('landload:listing_view', id=property_obj.custom_id)
        # else:
        #     error_messages = '<br>'.join(
        #         [f"{error}" for field_errors in form.errors.values() for error in field_errors]
        #     )
        #     messages.error(request, mark_safe(error_messages))
  
        
    return render(request,'landload/add_listing.html',{'form':form,'form2':form2,'form3':form3
                                                       ,'property_id':id,'property_obj':property_obj,'is_listing':True,
                                                       'property_obj2':property_obj2,'outside_images': outside_images,
                                                        'parking_images': parking_images,
                                                        'garage_images': garage_images,
                                                        'garden_images': garden_images,
                                                        'common_area_images': common_area_images,
                                                        'residence_images': residence_images,
                                                        'outside_images_json': outside_image_urls,
                                                        'parking_images_json': parking_image_urls,
                                                        'garage_images_json': garage_image_urls,
                                                        'garden_images_json': garden_image_urls,
                                                        'common_area_images_json': common_area_image_urls,
                                                        'residence_images_json': residence_image_urls,
                                                        'symbol':symbol,
                                                        })


@csrf_exempt  # but ideally use csrf_protect with valid CSRF!
def delete_property_image(request, image_id):
    if request.method == 'POST':
        try:
            image = PropertyImage.objects.get(id=image_id)
            image.delete()
            return JsonResponse({'success': True})
        except PropertyImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required(login_url='/')
def room(request,id):
    # property_obj = get_object_or_404(Property, pk=id)
    # existing_rooms = Rooms.objects.filter(property=property_obj).order_by('id')

    # if request.method == 'POST':
    #     room_ids = request.POST.getlist('room_id')
    #     types = request.POST.getlist('type_of_room')
    #     ensuites = request.POST.getlist('ensuite')
    #     capacities = request.POST.getlist('total_capacity')
    #     rents = request.POST.getlist('rent')

    #     for room_id, type_, ensuite, capacity, rent in zip(room_ids, types, ensuites, capacities, rents):
    #         room = Rooms.objects.get(id=room_id)
    #         room.type_of_room = type_
    #         room.ensuite = ensuite
    #         room.total_capacity = capacity
    #         room.rent = rent
    #         room.save()

    #     return redirect('property_view', pk=id)


        
    # return render(request,'landload/room.html',{'property_id':id,'property_obj':range(property_obj.rooms),'property_obj_data': property_obj,})

    property_obj = get_object_or_404(Property, pk=id)
    existing_rooms = Rooms.objects.filter(property=property_obj).order_by('id')
    data=LandlordProfile.objects.filter(landlord=request.user).first()
    symbol = get_symbol(data.currency)

    if request.method == 'POST':
        room_ids = request.POST.getlist('room_id')  
        types = request.POST.getlist('type_of_room')
        ensuites = request.POST.getlist('ensuite')
        capacities = request.POST.getlist('total_capacity')
        rents = request.POST.getlist('rent')
        amounts = request.POST.getlist('rent_ammount')
        print(rents)
        for  room_ids,type_, ensuite, capacity,amount in zip(room_ids, types, ensuites, capacities,amounts):
            if room_ids:  
                room = Rooms.objects.filter(id=room_ids).first()
                print('rooom',room)
                if room:
                    room.type_of_room = type_
                    room.ensuite = ensuite
                    room.total_capacity = capacity
                    room.rent_ammount = amount
                    room.save()
                # rent_value = request.POST.get(f'rent_{room_ids}') or request.POST.get(f'collect_rent_{room_ids}')
                # if rent_value:
                #     room.rent = float(rent_value) if rent_value.isdigit() else rent_value 
                # room.rent = float(rent)
                
        messages.success(request, f'Rooms has been updated successfully!')
        return redirect('landload:room', id=property_obj.id)

    context = {
        'property_obj': property_obj,
        'rooms': existing_rooms,
        # 'extra_rooms_needed': int(property_obj.rooms) - existing_rooms.count(),
        'room_range':range(int(property_obj.number_of_flat)),
        'is_listing':True,
        'symbol':symbol
    }
    return render(request,'landload/room.html',context)

@login_required(login_url='/')
def deactivate_property(request,pk):
    obj=Property.objects.get(id=pk)
    obj.is_active=False
    obj.save()
    return JsonResponse(True,safe=False)

@login_required(login_url='/')
def tenant(request):
    query = request.GET.get('q', '')
    tenant = Tenant.objects.filter(landload=request.user,is_active=True)
   
    if query:
        tenant = tenant.filter(
            Q(user__first_name__icontains=query) |
            Q(custom_id__icontains=query) |
            Q(property__short_name__icontains=query) 
        )
    return render(request,'landload/tenant_list.html',{'tenant':tenant,'search_field':True,'is_tenant':True})

@login_required(login_url='/')
def listing_list(request):
    data = []
    tenant_qs  = Property.objects.filter(landload=request.user,is_active=True)
    for i, obj in enumerate(tenant_qs, start=1):
        data.append({
            'responsive_id':"",
            'sr':i,
            'id':obj.custom_id,
            'name':obj.short_name,
            'profit': "---",
            'dues': "---",
            'loss': "---",
        })

    return JsonResponse({'data': data}) 

@login_required(login_url='/')
def payment_list(request):
    data = []
    print('*'*1000)
    tenant_qs  = Payment.objects.filter(landload=request.user,is_active=True)
    for i, obj in enumerate(tenant_qs, start=1):
        data.append({
            'responsive_id':"",
            'sr':i,
            'id':obj.custom_id,
            'Full_name':obj.tenant_name,
            'Property': str(obj.property.short_name),
            'Rent': "---",
            'Total Dues': "---",
            'Last Payment': "---",
            'Payment Settled till': "---",
        })

    return JsonResponse({'data': data}) 

@login_required(login_url='/')
def tenant_list(request):
    data = []
    print('*'*1000)
    tenant = Tenant.objects.filter(landload=request.user,is_active=True)
    for obj in tenant:
        data.append({
            'id':obj.id,
            'custom_id': obj.custom_id,
            'full_name':obj.user.first_name+''+obj.user.last_name if obj.user.last_login else '',
            'property': obj.property.short_name,
            'rent': obj.rent,
            'total_dues': "----",
            'last_payment': "",  
            'move_in_date': "",  
            
        })

    return JsonResponse({'data': data}) 

@login_required(login_url='/')
def tenant_add(request):
    property = Property.objects.filter(landload=request.user,is_active=True)
    form = TenantForm()
    print('run')
    if request.method == "POST":
        post_data = request.POST.copy()
        # print('post')
        # print(request.POST)
        post_data['landload']=request.user
        post_data['is_active']=True
        first_name=request.POST.get('first_name')
        middle_name=request.POST.get('middle_name')
        last_name=request.POST.get('last_name')
        phone_number=request.POST.get('phone_number')
        email=request.POST.get('email')
        form = TenantForm(post_data,request.FILES)
        if form.is_valid():
            print('pass 1')
            
            # if CustomUser.objects.filter(email=email).exists():
            #    messages.error(request, f'Email already exixts')
            #    return redirect('landload:tenant')
            user_data, created = CustomUser.objects.get_or_create(first_name=first_name,last_name=last_name,
                                      middle_name=middle_name,email=email,is_verify=True,
                                      phone_number=phone_number,defaults={
                                                                'password': 'Tenant@123',
                                                                'role': 'tenant'
                                                            })
            if created:
                # set hashed password securely
                user_data.set_password('Tenant@123')
                user_data.save()
            # form['landload']=request.user
            print('pass 2')
       
            property_obj = form.save(commit=False)
            property_obj.user = user_data  
            property_obj.save()
            token = get_random_string(16)
            TenentProfileVerify(tenant=property_obj, link=token).save()
            temp_url=redirect('tenant:tenantverify', id=token)
            token = 'http://'+str(get_current_site(request).domain)+str(temp_url.url)
            tenant_invitation_email(property_obj.user.first_name if property_obj.user.first_name else ''+' '+property_obj.user.last_name if property_obj.user.last_name else "",
            property_obj.user.email,request.user.first_name+' '+request.user.last_name if request.user.last_name else '',token,landload_id=request.user.id)
            messages.success(request, f'Tenant has been Created successfully!')
            return redirect('landload:tenant')
        else:
            # print('errr',form.errors)
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    return render(request,'landload/add_tenant.html',{'form':form,'property':property,'is_tenant':True})


@login_required(login_url='/')
def get_room(request):
    category_id = request.GET.get('category_id')
    existing_rooms = Rooms.objects.filter(property_id=category_id).values('id', 'room_code')
    # symbole = Country.objects.get(code=category_id)
    return JsonResponse({'existing_rooms': list(existing_rooms)})

@login_required(login_url='/')
def tenant_view(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    tenant_obj = get_object_or_404(Tenant, pk=id)
    form = TenantReadOnlyForm(instance=tenant_obj)
    return render(request,'landload/add_tenant.html',{'form':form,'tenant_id':id,'tenant_obj':tenant_obj,'more_fun':True,
                                                      'saved_model_id': tenant_obj.room.id if tenant_obj.room else None,
    'saved_property_id': tenant_obj.property.id if tenant_obj.property else None,'property':property,'is_tenant':True})

@login_required(login_url='/')
def tenant_dashboard(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    tenant_obj = get_object_or_404(Tenant, pk=id)
    form = TenantReadOnlyForm(instance=tenant_obj)
    return render(request,'landload/view_tenant_dashboad.html',{'form':form,'tenant_id':id,'tenant_obj':tenant_obj,'more_fun':True,
                                                      'saved_model_id': tenant_obj.room.id if tenant_obj.room else None,
    'saved_property_id': tenant_obj.property.id if tenant_obj.property else None,'property':property,'is_tenant':True})

@login_required(login_url='/')
def tenant_update(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    tenant_obj = get_object_or_404(Tenant, pk=id)
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['landload']=request.user
        post_data['is_active']=True
        post_data['user']=tenant_obj.user
        first_name=request.POST.get('first_name')
        middle_name=request.POST.get('middle_name')
        last_name=request.POST.get('last_name')
        phone_number=request.POST.get('phone_number')
        email=request.POST.get('email')
        form = TenantForm(post_data, request.FILES, instance=tenant_obj)
        if form.is_valid():

            obj=form.save()
            user = tenant_obj.user  # No need to query again
            # Update user fields if present in POST
            for field in ['first_name', 'middle_name', 'last_name', 'phone_number', 'email']:
                val = request.POST.get(field)
                if val:
                    setattr(user, field, val)
            user.save()
            messages.success(request, f'Tenant has been updated successfully!')
            return redirect('landload:tenant')
        else:
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    else:
        form = TenantForm(instance=tenant_obj)
    return render(request,'landload/add_tenant.html',{'form':form,'tenant_id':id,'tenant_obj':tenant_obj,
                                                      'saved_model_id': tenant_obj.room.id if tenant_obj.room else None,
    'saved_property_id': tenant_obj.property.id if tenant_obj.property else None,'property':property,'is_tenant':True})

@login_required(login_url='/')
def deactivate_tenant(request,pk):
    obj=Tenant.objects.get(id=pk)
    obj.is_active=False
    obj.save()
    return JsonResponse(True,safe=False)

@login_required(login_url='/')
def tenant_invite_add(request):
    property = Property.objects.filter(landload=request.user,is_active=True)
    form=TenantInviteForm()
    if request.method == "POST":
        post_data = request.POST.copy()
        post_data['is_active']=True
        form = TenantInviteForm(post_data,request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            # if CustomUser.objects.filter(email=email).exists():
            #    messages.error(request, f'Email already exixts')
            #    return redirect('landload:tenant')
            user , created = CustomUser.objects.get_or_create(email=email,defaults={
                                    'password': 'Root@123', 
                                    'role': 'tenant'
                                })
            if created:
                
                user.set_password('Root@123')
                user.is_verify=True
                user.save()
            tenant = form.save(commit=False)
            tenant.user = user
            tenant.landload = request.user
            tenant.save()
            token = get_random_string(16)
            TenentProfileVerify(tenant=tenant, link=token).save()
            temp_url=redirect('tenant:tenantverify', id=token)
            token = 'http://'+str(get_current_site(request).domain)+str(temp_url.url)
            tenant_invitation_email(user.first_name if user.first_name else ''+' '+user.last_name if user.last_name else "",
            user.email,request.user,token,tenant,landload_id=request.user.id)
            messages.success(request, f'Tenant has been Created successfully!')
            return redirect('landload:tenant')
        else:
            # print('errr',form.errors)
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))

    return render(request,'landload/add_invite_tenant.html',{'form':form,'property':property,'is_tenant':True})

@login_required(login_url='/')
def dues(request):
    query = request.GET.get('q', '')
    # print('*'*1000)
    # print(query)
    dues = Payment.objects.filter(landload=request.user,is_active=True)
    if query:
        dues = dues.filter(
            Q(tenant_name__icontains=query) |
            Q(custom_id__icontains=query) |
            Q(property__name__icontains=query) |
            Q(property__short_name__icontains=query)
        )
    return render(request,'landload/dues.html',{'dues':dues,'search_field':True,'is_payment':True})    

@login_required(login_url='/')
def dues_add(request):
    property = Property.objects.filter(landload=request.user,is_active=True)
    form = PaymentForm()
    if request.method == "POST":
        post_data = request.POST.copy()
        # print('post')
        # print(request.POST)
        post_data['landload']=request.user
        post_data['is_active']=True
        form = PaymentForm(post_data,request.FILES)
        if form.is_valid():
            # form['landload']=request.user
       
            property_obj=form.save()
            messages.success(request, f'Record has been Created successfully!')
            return redirect('landload:dues')
        else:
            # print('errr',form.errors)
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    return render(request,'landload/add_dues.html',{'form':form,'property':property,'is_payment':True})

@login_required(login_url='/')
def dues_view(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    property_obj = get_object_or_404(Payment, custom_id=id)
    form = PaymentReadOnlyForm(instance=property_obj)
    rooms=Rooms.objects.filter(property=property_obj.property)
    return render(request,'landload/add_dues.html',{'form':form,'property_id':id,'property_obj':property_obj,'more_fun':True,'property':property,
                                                    'rooms':rooms,'is_payment':True})

@login_required(login_url='/')
def dues_update(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    property_obj = get_object_or_404(Payment, pk=id)
    rooms=Rooms.objects.filter(property=property_obj.property)
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['landload']=request.user
        post_data['is_active']=True
        form = PaymentForm(post_data, request.FILES, instance=property_obj)
        if form.is_valid():
            obj=form.save()
            

            messages.success(request, f'Record has been updated successfully!')
            return redirect('landload:dues')
        else:
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    else:
        form = PaymentForm(instance=property_obj)
    return render(request,'landload/add_dues.html',{'form':form,'property_id':id,'property_obj':property_obj,'property':property,
                                                    'rooms':rooms,'is_payment':True})


@login_required(login_url='/')
def deactivate_dues(request,id):
    obj=Payment.objects.get(custom_id=id)
    obj.is_active=False
    obj.save()
    return JsonResponse(True,safe=False)

@login_required(login_url='/')
def expense(request):
    query = request.GET.get('q', '')
    # print('*'*1000)
    # print(query)
    dues = Expenses.objects.filter(landload=request.user,is_active=True)
    if query:
        dues = dues.filter(
            Q(tenant_name__icontains=query) |
            Q(custom_id__icontains=query) |
            Q(property__name__icontains=query) |
            Q(property__short_name__icontains=query)
        )
    return render(request,'landload/expense.html',{'dues':dues,'search_field':True,'is_expence':True})    

@login_required(login_url='/')
def expense_add(request):
    property = Property.objects.filter(landload=request.user,is_active=True)
    form = ExpensesForm()
    if request.method == "POST":
        post_data = request.POST.copy()
        # print('post')
        # print(request.POST)
        post_data['landload']=request.user
        post_data['is_active']=True
        form = ExpensesForm(post_data,request.FILES)
        if form.is_valid():
            # form['landload']=request.user
       
            property_obj=form.save()
            messages.success(request, f'Expense has been Created successfully!')
            return redirect('landload:expense')
        else:
            # print('errr',form.errors)
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    return render(request,'landload/add_expense.html',{'form':form,'property':property,'is_expence':True})

@login_required(login_url='/')
def expense_view(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    property_obj = get_object_or_404(Expenses, custom_id=id)
    form = ExpensesReadOnlyForm(instance=property_obj)
    rooms=Rooms.objects.filter(property=property_obj.property)
    return render(request,'landload/add_expense.html',{'form':form,'property_id':id,'property_obj':property_obj,'more_fun':True,'property':property,
                                                    'rooms':rooms,'is_expence':True})

@login_required(login_url='/')
def expense_update(request,id):
    property = Property.objects.filter(landload=request.user,is_active=True)
    property_obj = get_object_or_404(Expenses, pk=id)
    # rooms=Rooms.objects.filter(property=property_obj.property)
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['landload']=request.user
        post_data['is_active']=True
        form = ExpensesForm(post_data, request.FILES, instance=property_obj)
        if form.is_valid():
            obj=form.save()
            

            messages.success(request, f'Expenses has been updated successfully!')
            return redirect('landload:dues')
        else:
            error_messages = '<br>'.join(
                [f"{error}" for field_errors in form.errors.values() for error in field_errors]
            )
            messages.error(request, mark_safe(error_messages))
    else:
        form = ExpensesForm(instance=property_obj)
    return render(request,'landload/add_expense.html',{'form':form,'property_id':id,'property_obj':property_obj,'property':property,
                                                    'is_expence':True})


@login_required(login_url='/')
def deactivate_expense(request,id):
    obj=Expenses.objects.get(custom_id=id)
    obj.is_active=False
    obj.save()
    return JsonResponse(True,safe=False)

@login_required(login_url='/')
def expenses_list(request):
    data = []
    print('*'*1000)
    tenant_qs  = Expenses.objects.filter(landload=request.user,is_active=True)
    for i, obj in enumerate(tenant_qs, start=1):
        data.append({
            'responsive_id':"",
            'sr':i,
            'id':obj.custom_id,
            'Full_name':obj.tenant_name,
            'Property': str(obj.property.short_name),
            'Rent': "---",
            'Total Dues': "---",
            'Last Payment': "---",
            'Payment Settled till': "---",
        })

    return JsonResponse({'data': data}) 

def email_settings_view(request):
    email_settings, created = EmailSettings.objects.get_or_create(landlord=request.user)

    if request.method == 'POST':
        form = EmailSettingsForm(request.POST, instance=email_settings)
        if form.is_valid():
            form.save()
            return redirect('landload:email_setting') 
    else:
        form = EmailSettingsForm(instance=email_settings)

    return render(request, 'landload/email_settings.html', {'form': form})


