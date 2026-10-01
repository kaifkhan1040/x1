from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import CustomUser
from django.forms import EmailInput
from django.forms import ModelForm, TextInput, EmailInput, CharField, PasswordInput, ChoiceField, BooleanField, \
    NumberInput, DateInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

import re

class CustomUserCreationForm(UserCreationForm):
    
    def __init__(self, *args, **kwargs):
        # super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.add_input(Submit('submit', 'Submit'))
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'hidden': False,"id":'account-upload-form'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name','email','phone_number','image','dob','doj','role')
        widgets = {
            'dob':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
            'doj':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
                }
        
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,12}$'
        if not re.match(pattern, password):
            raise forms.ValidationError(
                "Password must be 8–12 characters long, include at least one uppercase letter, one lowercase letter, and one symbol."
            )
        return password


class SetLocationForm(ModelForm):
    # country = forms.ChoiceField(choices=country_choices,required=False)
    def __init__(self, *args, **kwargs):
        # super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.add_input(Submit('submit', 'Submit'))
        super().__init__(*args, **kwargs)
        self.fields['country'].widget.attrs.update({'class': 'select2 form-control customtext-change'})

    class Meta:
            model = CustomUser
            fields = ('country',)

class UserProfileForm(ModelForm):
    # country = forms.ChoiceField(choices=country_choices,required=False)
    def __init__(self, *args, **kwargs):
        # super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.add_input(Submit('submit', 'Submit'))
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control valid'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control','maxlength':10,'minlength':10})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['salary'].widget.attrs.update({'class': 'form-control'})
        self.fields['designation'].widget.attrs.update({'class': 'form-control'})
        self.fields['zipcode'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'hidden': False,"id":'account-upload-form'})
        self.fields['country'].widget.attrs.update({'class': 'select2 form-control customtext-change'})

    class Meta:
            model = CustomUser
            fields = ('first_name', 'last_name','email','phone_number','address',
            'state','zipcode','image','salary','designation','dob','doj','country')
            widgets = {
            'dob':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
            'doj':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
                }

    # widgets = {
    #         'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'accountFirstName'}),
    #         'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'accountLastName'}),
    #         'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'accountEmail'}),
    #         'phone_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'accountPhoneNumber'}),
    #         'address': forms.TextInput(attrs={'class': 'form-control', 'id': 'accountAddress'}),
    #         'state': forms.TextInput(attrs={'class': 'form-control', 'id': 'accountState'}),
    #         'zipcode': forms.TextInput(attrs={'class': 'form-control', 'id': 'accountZipcode'}),
    #         'country': forms.Select(attrs={'class': 'form-control', 'id': 'accountCountry'}),
    #     }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(max_length=200)

    class Meta:
        fields = '__all__'
        widgets = {
            'email': EmailInput(attrs={
                'class': "form-control",
            })
        }
