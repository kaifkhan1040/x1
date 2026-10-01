from django.contrib import admin
from .models import Rooms,Property,Tenant,TenentProfileVerify,Payment,Country,\
    FinancialBreakdown,FinancialOtherModel,PropertyImage,AddressHistory,DocumentOthers,professionHistory,\
    EmailSettings,LandlordProfile,LandloadDoucment
# Register your models here.
admin.site.register(Rooms)
admin.site.register(Property)
admin.site.register(Tenant)
admin.site.register(TenentProfileVerify)
admin.site.register(Payment)
admin.site.register(Country)
admin.site.register(FinancialBreakdown)
admin.site.register(FinancialOtherModel)
admin.site.register(PropertyImage)
admin.site.register(AddressHistory)
admin.site.register(DocumentOthers)
admin.site.register(professionHistory)
admin.site.register(EmailSettings)
admin.site.register(LandlordProfile)
admin.site.register(LandloadDoucment)
# admin.site.register(LandloadDoucment)