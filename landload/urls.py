from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='home'),
    path('listing',views.listing,name='listing'),
    path('listing_list',views.listing_list,name='listing_list'),
    path('payment_list',views.payment_list,name='payment_list'),
    path('listing-add',views.listing_add,name='listing_add'),
    path('listing-view/<str:id>/',views.listing_view,name='listing_view'),
    path('listing-dashboard/<str:id>/',views.listing_dashboard,name='listing_dashboard'),
    path('listing-update/<int:id>/',views.listing_update,name='listing_update'),
    path('room/<int:id>/',views.room,name='room'),
    path('deactivate_property/<int:pk>/',views.deactivate_property,name='deactivate_property'),
    path('deactivate_tenant/<int:pk>/',views.deactivate_tenant,name='deactivate_tenant'),

    path('earning_report/<int:year>/',views.earning_report,name='earning_report'),
    path('property_earning_report/<int:year>/<int:pro_id>/',views.property_earning_report,name='property_earning_report'),
    path('tenant',views.tenant,name='tenant'),
    path('tenant_list',views.tenant_list,name='tenant_list'),
    path('tenant-add',views.tenant_add,name='tenant_add'),
    path('tenant-invite-add',views.tenant_invite_add,name='tenant_invite_add'),
    path('tenant-view/<int:id>/',views.tenant_view,name='tenant_view'),
    path('tenant-dashboard/<int:id>/',views.tenant_dashboard,name='tenant_dashboard'),
    path('tenant-update/<int:id>/',views.tenant_update,name='tenant_update'),
    
    path('dues',views.dues,name='dues'),
    path('dues-add',views.dues_add,name='dues_add'),
    path('dues-view/<str:id>/',views.dues_view,name='dues_view'),
    path('dues-update/<int:id>/',views.dues_update,name='dues_update'),
    path('dues-delete/<str:id>/',views.deactivate_dues,name='deactivate_dues'),

    path('expense',views.expense,name='expense'),
    path('email_setting',views.email_settings_view,name='email_setting'),
    path('expense-add',views.expense_add,name='expense_add'),
    path('expense-view/<str:id>/',views.expense_view,name='expense_view'),
    path('expense-update/<int:id>/',views.expense_update,name='expense_update'),
    path('expense-delete/<str:id>/',views.deactivate_expense,name='deactivate_expense'),
    path('expenses_list',views.expenses_list,name='expenses_list'),


    path('get_room',views.get_room,name='get_room'),
    path('setup-location/', views.setup_location, name='setup_location'),
    path('submit-step/<str:step>/', views.submit_step, name='submit_step'),
    path('delete-image/<int:image_id>/', views.delete_property_image, name='delete_property_image'),

    path('onboading',views.onboading,name='onboading'),
    path('locationdetails',views.locationdetails,name='locationdetails'),
    path('onboad-step/<str:step>/', views.onboad_step, name='onboad_step'),

   

    

]