from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='home'),
    # path('landload',views.landload,name='landload'),
    # path('add_landload',views.add_landload,name='add_landload'),
    # path('update_landload/<int:id>',views.add_landload,name='update_landload'),
    # path('delete_landload/<int:id>',views.delete_landload,name='delete_landload'),
    # path('setuplandload/<str:id>',views.setuplandload,name='setuplandload'),
    path('list', views.landload_list, name='landload_list'),
    path('approve_landload/<int:pk>', views.approve_landload, name='approve_landload'),
    path('reject_landload/<int:pk>', views.reject_landload, name='reject_landload'),
    path('payment_token/<int:pk>', views.payment_token, name='payment_token'),

]