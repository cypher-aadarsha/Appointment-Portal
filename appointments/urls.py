from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.PublicBookingView.as_view(), name='book_appointment'),
    path('api/slots/', views.get_available_slots, name='get_slots'),
    path('api/book/', views.AppointmentCreateView.as_view(), name='create_appointment'),
]
