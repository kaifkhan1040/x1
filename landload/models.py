from django.db import models
from django.db import transaction
# Create your models here.
from users.models import CustomUser
from django.utils import timezone
import pytz

class Property(models.Model):
    ROOM_CHOICES = [(str(i), i) for i in range(1, 11)]


    custom_id = models.CharField(max_length=10, unique=True, blank=True)
    short_name = models.CharField(max_length=100)
    name = models.CharField(max_length=200,blank=True,null=True)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=8)

    property_type = models.CharField(max_length=100,choices=(('Detached House','Detached House'),('Private Apartment','Private Apartment')),blank=True,null=True)
    number_of_flat = models.CharField(max_length=100,choices=ROOM_CHOICES,blank=True,null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status =models.BooleanField(default=True)
    prop_thumbnail = models.ImageField(upload_to='property_thumbnails/', blank=True, null=True)
    landload = models.ForeignKey(CustomUser,on_delete=models.CASCADE,blank=True,null=True)
    rental_type= models.CharField(max_length=25,choices=(('Single Ownership','Single Ownership'),('Multi Ownership','Multi Ownership' )),blank=False)
    is_active =models.BooleanField(default=True)
    property_description = models.TextField(blank=True,null=True)
  

    def __str__(self):
        return f"{self.short_name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.custom_id:
            with transaction.atomic():
                # Lock the table during ID generation
                last_obj = Property.objects.select_for_update().order_by('-id').first()
                if last_obj and last_obj.custom_id.startswith('PP'):
                    try:
                        last_number = int(last_obj.custom_id[2:])
                    except ValueError:
                        last_number = 100
                    next_number = last_number + 1
                else:
                    next_number = 101

                # Loop to ensure uniqueness
                while True:
                    candidate_id = f'PP{next_number}'
                    if not Property.objects.filter(custom_id=candidate_id).exists():
                        self.custom_id = candidate_id
                        break
                    next_number += 1

        super().save(*args, **kwargs)
    
class FinancialBreakdown(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='financials')

    monthly_rental = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cleaning = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    electricity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gas = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    internet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    water = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    license = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    one_time_setup_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other = models.BooleanField(default=False)
    collect_rent =models.CharField(max_length=20,choices=(('Weekly','Weekly'),('Monthly','Monthly')))
    
    def total_cost(self):
        fields = [
            self.monthly_rental, self.tax, self.cleaning, self.electricity,
            self.gas, self.internet, self.water, self.license,self.one_time_setup_cost,
        ]
        return sum(f or 0 for f in fields)

    def __str__(self):
        return f"Financials for {self.property}"
    
class FinancialOtherModel(models.Model):
    financial = models.ForeignKey(FinancialBreakdown, on_delete=models.CASCADE, related_name='financialsother')
    lable = models.CharField(max_length=255,null=True,blank=True)
    amount = models.CharField(max_length=255,null=True,blank=True)

class PropertyImage(models.Model):
    def upload_to(instance, filename):
        return f'property_images/{instance.field_type}/{filename}'

    FIELD_CHOICES = [
        ('outside', 'Outside'),
        ('parking', 'Parking'),
        ('garage', 'Garage'),
        ('garden', 'Garden'),
        ('common_area', 'Common Area'),
        ('residence', 'Residence'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    field_type = models.CharField(max_length=20, choices=FIELD_CHOICES)
    image = models.ImageField(upload_to=upload_to)
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Rooms(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='room_set')    
    type_of_room = models.CharField(max_length=20,choices=[('Single','Single'),('Double','Double')])
    ensuite = models.CharField(max_length=20,choices=[('Yes','Yes'),('No','No')])
    total_capacity = models.CharField(max_length=20,choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    rent =models.CharField(max_length=20,choices=(('Per night','Per night'),('Weekly','Weekly'),('Monthly','Monthly')))
    room_code = models.CharField(max_length=10, unique=True, blank=True)
    rent_ammount = models.FloatField(default=0.0)
    room_count = models.CharField(max_length=3)

    def save(self, *args, **kwargs):
        if not self.room_code:
            with transaction.atomic():
                last_obj = Rooms.objects.select_for_update().order_by('-id').first()
                if last_obj and last_obj.room_code.startswith('Room'):
                    try:
                        last_number = int(last_obj.room_code[4:])  # Use [4:] to skip "Room"
                    except ValueError:
                        last_number = 100
                    next_number = last_number + 1
                else:
                    next_number = 101

                # Generate unique room_code
                while True:
                    candidate_id = f'Room{next_number}'
                    if not Rooms.objects.filter(room_code=candidate_id).exists():
                        self.room_code = candidate_id
                        break
                    next_number += 1

        super().save(*args, **kwargs)


class EmailSettings(models.Model):
    landlord = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_settings')
    email_host = models.CharField(max_length=255, default='smtp.gmail.com')
    email_port = models.PositiveIntegerField(default=587)
    email_host_user = models.EmailField()
    email_host_password = models.CharField(max_length=255)  
    use_tls = models.BooleanField(default=True)
    from_email =models.CharField(max_length=500)

    def __str__(self):
        return f"{self.landlord.first_name}'s Email Settings"



class Country(models.Model):
    name = models.CharField(max_length=60, unique=True)
    iso = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    dial = models.CharField(max_length=5)
    currency = models.CharField(max_length=3, null=True, blank=True)
    currency_name = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'iso', 'iso3', 'dial')

    def __str__(self):
        return self.name

class LandlordProfile(models.Model):
    landlord = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='landlord_profile')
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    currency = models.CharField(max_length=50)
    time_zone = models.CharField(max_length=50, choices=[(tz, tz) for tz in pytz.common_timezones],
        default='UTC'
        )
    user_data_hosting_location = models.CharField(max_length=50,choices=[('North America','North America'),('EU','EU'),
                                                                         ('Middle East','Middle East'),('Singapore','Singapore'),
                                                                         ('India','India')])
    billing_address=models.CharField(max_length=500,null=True,blank=True)
    subscription = models.CharField(max_length=50,choices=[('basic','basic'),('standard','standard'),('enterprise','enterprise')],null=True,blank=True)
    payment_code = models.CharField(max_length=6,null=True,blank=True)
    is_locked= models.BooleanField(default=True)

class LandloadDoucment(models.Model):
    landlord = models.ForeignKey(LandlordProfile, on_delete=models.CASCADE, related_name='idproff')
    upload_document = models.ImageField(upload_to='landload/id_proff')




class Tenant(models.Model):
    RESIDENCE_STATUS = [
        ('Citizen', 'Citizen'),
        ('EU Settled', 'EU Settled'),
        ('Indefinite Leave to Remain', 'Indefinite Leave to Remain'),
        ('Visa', 'Visa'),
    ]
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    landload = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='landload_properties',null=True,blank=True)
    property=models.ForeignKey(Property,on_delete=models.CASCADE,null=True,blank=True)
    room=models.ForeignKey(Rooms,on_delete=models.CASCADE,null=True,blank=True)
    rent=models.FloatField(default=0.0)
    deposit=models.FloatField(default=0.0)
    photo=models.ImageField(upload_to='tenant/photo',blank=True,null=True)
    id_proof=models.ImageField(upload_to='tenant/id_proof',blank=True,null=True)
    address_proof=models.ImageField(upload_to='tenant/address_proof',blank=True,null=True)
    visa_proof=models.ImageField(upload_to='tenant/visa_proof',blank=True,null=True)
    bank_statement=models.ImageField(upload_to='tenant/bank_statement',blank=True,null=True)
    custom_id = models.CharField(max_length=10, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    residence_status = models.CharField(max_length=50, choices=RESIDENCE_STATUS)
    visa_type = models.CharField(max_length=100, blank=True, null=True)
    visa_from = models.DateField(blank=True, null=True)
    visa_to = models.DateField(blank=True, null=True)
    evisa_code = models.CharField(max_length=100, blank=True, null=True)
    right_to_rent_code = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    employer_name = models.CharField(max_length=100, blank=True, null=True)
    employer_address =models.CharField(max_length=700, blank=True, null=True)
    employment_From=  models.DateField(blank=True, null=True)
    employment_to=  models.DateField(blank=True, null=True)
    salary = models.FloatField(null=True,blank=True)
    bank_name = models.CharField(max_length=500,null=True,blank=True)
    account_type = models.CharField(max_length=50,choices=[('Personal','Personal'),('Business','Business')],null=True,blank=True)
    sort_code = models.CharField(max_length=50,null=True,blank=True)
    account_number =models.CharField(max_length=50,null=True,blank=True) 
    address_proof = models.CharField(max_length=50,choices=[('Passport','Passport'),('Driving License','Driving License')])
    self_photo = models.ImageField(upload_to='tenant/self/',null=True,blank=True)
    visa_letter  = models.ImageField(upload_to='tenant/visa/',null=True,blank=True)
    bank_statement = models.ImageField(upload_to='tenant/bank/',null=True,blank=True)
    pay_slips = models.ImageField(upload_to='tenant/payslip/',null=True,blank=True)
    other = models.BooleanField(default=False)
    is_agree = models.BooleanField(default=False,null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.custom_id:
            with transaction.atomic():
                # Lock the table during ID generation
                last_obj = Tenant.objects.select_for_update().order_by('-id').first()
                if last_obj and last_obj.custom_id.startswith('TN'):
                    try:
                        last_number = int(last_obj.custom_id[2:])
                    except ValueError:
                        last_number = 100
                    next_number = last_number + 1
                else:
                    next_number = 101

                # Loop to ensure uniqueness
                while True:
                    candidate_id = f'TN{next_number}'
                    if not Tenant.objects.filter(custom_id=candidate_id).exists():
                        self.custom_id = candidate_id
                        break
                    next_number += 1

        super().save(*args, **kwargs)

class DocumentOthers(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='bankother')
    
    document_type = models.CharField(max_length=100)
    upload_document = models.ImageField(upload_to='tenant/document')


class professionHistory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='professionhhistory')
    history_employer_name = models.CharField(max_length=100, blank=True, null=True)
    history_employer_address =models.CharField(max_length=700, blank=True, null=True)
    history_employment_From=  models.DateField(blank=True, null=True)
    history_employment_to=  models.DateField(blank=True, null=True)
    history_salary = models.FloatField(null=True,blank=True)

class AddressHistory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='addresses')
    
    landlord_name = models.CharField(max_length=100)
    landlord_contact = models.CharField(max_length=20, blank=True, null=True)
    landlord_email = models.EmailField(blank=True, null=True)

    from_date = models.DateField()
    to_date = models.DateField()

    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)

class EmploymentHistory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='profession')
    

class TenentProfileVerify(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    link = models.CharField(max_length=500)
    verify = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.tenant)


class Payment(models.Model):
    custom_id = models.CharField(max_length=10, unique=True, blank=True)
    property = models.ForeignKey(Property,on_delete=models.CASCADE)
    room = models.ForeignKey(Rooms,on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255)
    m_for = models.CharField(choices=[('Rent WS','Rent WS'),('Deposit','Deposit'),('Penalty','Penalty'),('Custom','Custom')], max_length=50)
    amount = models.FloatField()
    method = models.CharField(max_length=50,choices=[("Cash",'cash'),('Account Transfer','Account Transfer')])
    paid_date = models.DateField(auto_now_add=True)
    proof = models.ImageField(upload_to='Payment/proof/',null=True,blank=True)
    is_active = models.BooleanField(default=True)
    landload = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    # is_active =models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.custom_id:
            with transaction.atomic():
                # Lock the table during ID generation
                last_obj = Payment.objects.select_for_update().order_by('-id').first()
                if last_obj and last_obj.custom_id.startswith('Pay'):
                    try:
                        last_number = int(last_obj.custom_id[2:])
                    except ValueError:
                        last_number = 100
                    next_number = last_number + 1
                else:
                    next_number = 101

                # Loop to ensure uniqueness
                while True:
                    candidate_id = f'Pay{next_number}'
                    if not Payment.objects.filter(custom_id=candidate_id).exists():
                        self.custom_id = candidate_id
                        break
                    next_number += 1

        super().save(*args, **kwargs)

class Expenses(models.Model):
    custom_id = models.CharField(max_length=10, unique=True, blank=True)
    property = models.ForeignKey(Property,on_delete=models.CASCADE)
    room = models.ForeignKey(Rooms,on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255)
    m_for = models.CharField(choices=[('Rent WS','Rent WS'),('Deposit','Deposit'),('Penalty','Penalty'),('Custom','Custom')], max_length=50)
    amount = models.FloatField()
    method = models.CharField(max_length=50,choices=[("Cash",'cash'),('Account Transfer','Account Transfer')])
    paid_date = models.DateField(auto_now_add=True)
    proof = models.ImageField(upload_to='Dues/proof/',null=True,blank=True)
    is_active = models.BooleanField(default=True)
    landload = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    # is_active =models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.custom_id:
            with transaction.atomic():
                # Lock the table during ID generation
                last_obj = Expenses.objects.select_for_update().order_by('-id').first()
                if last_obj and last_obj.custom_id.startswith('EXP'):
                    try:
                        last_number = int(last_obj.custom_id[2:])
                    except ValueError:
                        last_number = 100
                    next_number = last_number + 1
                else:
                    next_number = 101

                # Loop to ensure uniqueness
                while True:
                    candidate_id = f'EXP{next_number}'
                    if not Expenses.objects.filter(custom_id=candidate_id).exists():
                        self.custom_id = candidate_id
                        break
                    next_number += 1

        super().save(*args, **kwargs)

