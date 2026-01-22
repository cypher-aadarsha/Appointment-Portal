from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Minister, TimeSlot, Appointment
from django.core.mail import send_mail
import json
from datetime import datetime
from django.utils import timezone

class PublicBookingView(TemplateView):
    template_name = 'appointments/booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ministers'] = Minister.objects.filter(is_active=True)
        return context

@method_decorator(csrf_exempt, name='dispatch') # For simplicity in this demo, though better to use CSRF token in JS
class AppointmentCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            slot_id = data.get('slot_id')
            full_name = data.get('full_name')
            # Add other fields as needed
            
            if not slot_id or not full_name:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            slot = get_object_or_404(TimeSlot, id=slot_id)
            
            if slot.is_booked:
                return JsonResponse({'error': 'Slot already booked'}, status=400)
                
            # Create Appointment
            appointment = Appointment.objects.create(
                slot=slot,
                full_name=full_name,
                email=data.get('email', ''),
                phone_number=data.get('phone_number', ''),
                purpose=data.get('purpose', ''),
                status='PENDING'
            )
            
            # Send Notification
            subject = f'Appointment Request Received - {appointment.id}'
            message = f"""
            Dear {full_name},

            Your appointment request with {slot.minister.name} for {slot.date} at {slot.start_time} has been received.
            
            Current Status: PENDING
            
            You will receive another email once the request is processed.

            Regards,
            Ministry Secretariat
            """
            
            send_mail(
                subject,
                message,
                None, # Use DEFAULT_FROM_EMAIL
                [data.get('email')],
                fail_silently=True,
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Appointment request submitted successfully! check your email.',
                'appointment_id': appointment.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def get_available_slots(request):
    minister_id = request.GET.get('minister_id')
    date_str = request.GET.get('date') # YYYY-MM-DD
    
    if not minister_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        # Date Validation
        request_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = timezone.now().date()
        
        if request_date < today:
            return JsonResponse({'error': 'Cannot book appointments for past dates'}, status=400)

        slots = TimeSlot.objects.filter(
            minister_id=minister_id,
            date=date_str,
            is_booked=False
        )
        
        # Filter out slots that have a PENDING appointment attached
        available_slots = []
        for slot in slots:
            # Also filter time if date is today
            if request_date == today:
                 if slot.start_time <= timezone.now().time():
                     continue

            if not hasattr(slot, 'appointment'):
                available_slots.append(slot)
        
        data = [{
            'id': slot.id,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M')
        } for slot in available_slots]
        return JsonResponse({'slots': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
