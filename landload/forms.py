from django import forms
from users.models import CustomUser
from django.forms import EmailInput
from django.forms import ModelForm, TextInput, EmailInput, CharField, PasswordInput, ChoiceField, BooleanField, \
    NumberInput, DateInput
from .models import Property,Rooms,Tenant,Payment,FinancialBreakdown,Expenses,AddressHistory,EmailSettings,LandlordProfile
from django.forms.widgets import FileInput
from django.core.validators import FileExtensionValidator

class PropertyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['address_1'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['address_2'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['city'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['postcode'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['property_type'].widget.attrs.update({'class': 'form-select valid'})
        self.fields['number_of_flat'].widget.attrs.update({'class': 'form-select valid','required':True})
        self.fields['cost'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['property_description'].widget.attrs.update({'class': 'form-control valid','rows': 5})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['prop_thumbnail'].widget.attrs.update({'class': 'form-control valid'})
        
        self.fields['rental_type'].choices = [
    choice for choice in self.fields['rental_type'].choices if choice[0] != ''
]
        # self.fields['rental_type'].widget.attrs.update({'class': 'form-control valid'})
        
        
    class Meta:
            model = Property
            fields = "__all__"
            widgets = {
            'start_date':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
             'end_date':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",
                'placeholder':"date hai"}),
                'rental_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
                }
            
class PropertyReadOnlyForm(PropertyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True



class FinancialBreakdownform(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control valid'
        self.fields['other'].widget.attrs.update({'class': 'custom-control-input',"id":'customCheck1'})
        self.fields['collect_rent'].choices = [
            choice for choice in self.fields['collect_rent'].choices if choice[0] != ''
            ]
        self.fields['collect_rent'].widget.attrs.update({'class': 'form-check-input'})

    class Meta:
            model = FinancialBreakdown
            fields = "__all__"
            widgets = {
                'collect_rent': forms.RadioSelect(attrs={'class': 'form-check-input'}),
                }
            
class FinancialBreakdownReadOnlyform(FinancialBreakdownform):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True

class MultiImageInput(FileInput):
    allow_multiple_selected = True

class MultiImageForm(forms.Form):
    outside = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)
    parking = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)
    garage = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)
    garden = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)
    common_area = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)
    residence = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)

class MultiImageReadOnlyForm(MultiImageForm):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True

class RoomsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['property'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['type_of_room'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['ensuite'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['total_capacity'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['rent'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['rent_ammount'].widget.attrs.update({'class': 'form-control valid'})
        # self.fields['rent'].choices = [
        #     choice for choice in self.fields['rental_type'].choices if choice[0] != ''
        # ]
       
        
    class Meta:
            model = Rooms
            fields = "__all__"
            # widgets = {
            #      'rent': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            # }

class PaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['m_for'].widget.attrs.update({'class': 'form-select valid'})
        self.fields['method'].widget.attrs.update({'class': 'form-select valid'})

    class Meta:
            model = Payment
            fields = "__all__"

class PaymentReadOnlyForm(PaymentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True

class ExpensesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['m_for'].widget.attrs.update({'class': 'form-select valid'})
        self.fields['method'].widget.attrs.update({'class': 'form-select valid'})

    class Meta:
            model = Expenses
            fields = "__all__"

class ExpensesReadOnlyForm(PaymentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True


class TenantForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
            model = Tenant
            fields = "__all__"


class ManagerTenantForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}))
    phone_number = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'tel', 'autocomplete': 'tel'}))
    property = forms.ModelChoiceField(queryset=Property.objects.none(), widget=forms.Select(attrs={'class': 'form-select'}))
    room = forms.ModelChoiceField(queryset=Rooms.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    move_in_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    term_agreed = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12 months'}))
    rent = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}))
    deposit = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}))

    def __init__(self, *args, landlord, **kwargs):
        super().__init__(*args, **kwargs)
        self.landlord = landlord
        self.fields['property'].queryset = Property.objects.filter(landload=landlord, is_active=True).order_by('property_name')
        property_id = self.data.get('property') or self.initial.get('property')
        available_rooms = Rooms.objects.filter(property__landload=landlord, property__is_active=True).exclude(tenant__is_active=True)
        if property_id:
            available_rooms = available_rooms.filter(property_id=property_id)
        else:
            available_rooms = available_rooms.none()
        self.fields['room'].queryset = available_rooms.order_by('room_code')

    def clean(self):
        cleaned_data = super().clean()
        property_obj = cleaned_data.get('property')
        room = cleaned_data.get('room')
        if room and property_obj and room.property_id != property_obj.id:
            self.add_error('room', 'Choose a room in the selected property.')
        return cleaned_data


class ManagerTenantDocumentsForm(forms.ModelForm):
    right_to_rent_code = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    id_proof = forms.FileField(required=False, validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg', 'webp'])], widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}))
    bank_statement = forms.FileField(required=False, validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg', 'webp'])], widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}))

    class Meta:
        model = Tenant
        fields = ['id_proof', 'right_to_rent_code', 'photo', 'bank_statement']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class TenantReadOnlyForm(TenantForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True

class TenantInviteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter tenant email'})
    )
    class Meta:
            model = Tenant
            fields = ['property','room','rent','deposit','email']


class TenantInviteReadOnlyForm(TenantForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    middle_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter tenant email'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = Tenant
        fields = ['property', 'room', 'rent', 'deposit', 'first_name', 'middle_name', 'email','phone_number',
                  'photo','id_proof','address_proof','visa_proof','bank_statement']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['middle_name'].initial = self.instance.user.middle_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone_number'].initial = self.instance.user.phone_number

        for name, field in self.fields.items():
            value = self.initial.get(name) or getattr(self.instance, name, None)

            if value:  
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True




class LocationForm(forms.Form):
    location = forms.CharField(label='Your Location', max_length=255)


class TenantStep1Form(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['residence_status', 'visa_type', 'visa_from', 'visa_to', 'evisa_code', 'right_to_rent_code']
        widgets = {
            'visa_from': forms.DateInput(attrs={'type': 'date'}),
            'visa_to': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['residence_status'].widget.attrs.update({'class': 'form-select valid'})


class TenantProfessionForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['employer_name', 'employer_address', 'employment_From', 'employment_to', 'salary']
        widgets = {
            'employment_From': forms.DateInput(attrs={'type': 'date'}),
            'employment_to': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class TenantDocumentsForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['address_proof', 'self_photo', 'visa_letter', 'bank_statement', 'pay_slips','other']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['address_proof'].widget.attrs.update({'class': 'form-select'})
        self.fields['other'].widget.attrs.update({'class': 'form-check-input',"id":'customCheck001'})

class TenantBankForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = True
        self.fields['account_type'].choices = [
                choice for choice in self.fields['account_type'].choices if choice[0] != ''
            ]
        self.fields['account_type'].widget.attrs.update({'class': 'form-check-input'})
    class Meta:
        model = Tenant
        fields = ['bank_name', 'account_type', 'sort_code', 'account_number']
        widgets = {
            'account_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }

class LandlordProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].widget.attrs.update({'class': 'select2 form-control customtext-change'})
        self.fields['time_zone'].widget.attrs.update({'class': 'select2 form-control customtext-change'})
        self.fields['user_data_hosting_location'].widget.attrs.update({'class': 'select2 form-control customtext-change'})
        self.fields['currency'].widget.attrs.update({'class': 'form-control','readonly':True})

    class Meta:
        model = LandlordProfile
        fields=['country','time_zone','user_data_hosting_location','currency']

class IdProffForm(forms.Form):
    id_proff = forms.FileField(widget=MultiImageInput(attrs={'multiple': True,'class':'form-control','hidden':True}), required=False)

class EmailSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['use_tls'].widget.attrs.update({'class': 'form-check-input'})

    class Meta:
        model = EmailSettings
        fields = ['email_host', 'email_port', 'email_host_user', 'email_host_password', 'use_tls','from_email']
        widgets = {
            'email_host_password': forms.PasswordInput(),
        }

class AddressHistoryForm(forms.ModelForm):
    class Meta:
        model = AddressHistory
        exclude = ['user']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['landlord_name'].widget.attrs.update({'class': 'form-control valid'})
