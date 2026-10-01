from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='home'),
    path('tenantverify/<str:id>',views.tenantverify,name='tenantverify'),

    path('tenant/onboard/step1/', views.tenant_step1, name='tenant_step1'),
    path('submit-step/<str:step>/', views.submit_step, name='submit_step'),
    # path('tenant/onboard/step2/', views.tenant_step2, name='tenant_step2'),
    # path('tenant/onboard/step3/', views.tenant_step3, name='tenant_step3'),
    # path('tenant/onboard/step4/', views.tenant_step4, name='tenant_step4'),
    # path('tenant/onboard/step5/', views.tenant_step5, name='tenant_step5'),

]