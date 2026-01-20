from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Minister, TimeSlot, Appointment
from django.core.mail import send_mail
import json

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
            
            # Send Notification (Mock)
            print(f"NEW APPOINTMENT: {full_name} for {slot.minister.name} on {slot.date}")
            # send_mail(
            #     'New Appointment Request',
            #     f'New appointment request from {full_name}. Check dashboard.',
            #     'system@portal.gov.np',
            #     ['admin@portal.gov.np'],
            #     fail_silently=True,
            # )
            
            return JsonResponse({
                'success': True, 
                'message': 'Appointment request submitted successfully!',
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
        # Exclude slots that have PENDING or APPROVED appointments
        # Actually logic: if is_booked is True, it's confirmed. 
        # But we also want to block slots that have pending appointments to avoid double booking requests?
        # For now, let's just stick to is_booked=False. 
        # Optional: Check if appointment exists for slot using related_name
        
        slots = TimeSlot.objects.filter(
            minister_id=minister_id,
            date=date_str,
            is_booked=False
        )
        
        # Filter out slots that have a PENDING appointment attached (if we want to be strict)
        available_slots = []
        for slot in slots:
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
