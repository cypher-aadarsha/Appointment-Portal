from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('action/<int:appointment_id>/', views.appointment_action, name='action'),
    path('login/', lambda r: redirect('/admin/login/?next=/dashboard/'), name='login'), # Redirect to admin login for now
]
