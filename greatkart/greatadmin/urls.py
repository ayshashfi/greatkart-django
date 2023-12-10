from django.urls import path
from . import views

urlpatterns = [
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('usermanagement/',views.usermanagement,name='usermanagement'),
    path('blockuser/<int:user_id>/',views.blockuser,name='blockuser'),
    path('edit_admin_profile/',views.edit_admin_profile,name='edit_admin_profile'),
    path('admin_logout1/',views.admin_logout1,name='admin_logout1'),
   
]
