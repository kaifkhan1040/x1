from django.urls import path
from . import views


urlpatterns = [
    path('', views.loginPage, name='login'),
    path('login/', views.adminlogin, name='adminlogin'),
    path('logout/',views.logout_view,name='logout'),
    path('email/',views.checkemail,name='checkemail'),
    path('signup/',views.signup,name='signup'),
    
    # path('password_reset', views.password_reset_request, name="password_reset")
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('forgetpassword/<str:id>',views.create_password,name='create_password'),
    # path('changepassword/',views.changepassword,name='changepassword'),
    # path('Fporegistation/',views.Fporegistation,name='Fporegistation'),
    path('userverify/<str:id>',views.userverify,name='userverify'),
    path('verify_otp/<str:id>',views.verify_otp,name='verify_otp'),
    path('resend_verification/',views.resend_verification,name='resend_verification'),

]
