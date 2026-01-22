from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from appointments.models import Appointment
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Ideally use @login_required, simplified for demo/speed or use admin login
def dashboard_home(request):
    # For now, we assume anyone accessing this is staff or we rely on admin login (which we haven't forced yet)
    # In a real app: @login_required
    
    status_filter = request.GET.get('status', 'PENDING')
    appointments = Appointment.objects.filter(status=status_filter).order_by('slot__date', 'slot__start_time')
    
    counts = {
        'pending': Appointment.objects.filter(status='PENDING').count(),
        'approved': Appointment.objects.filter(status='APPROVED').count(),
        'rejected': Appointment.objects.filter(status='REJECTED').count(),
    }
    
    return render(request, 'dashboard/index.html', {
        'appointments': appointments,
        'counts': counts,
        'current_filter': status_filter
    })

from django.core.mail import send_mail

def appointment_action(request, appointment_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_message = request.POST.get('admin_message', '')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        appointment.admin_message = admin_message
        
        email_subject = ''
        email_body = ''
        
        if action == 'approve':
            appointment.status = 'APPROVED'
            appointment.slot.is_booked = True # Confirm slot booking
            appointment.slot.save()
            messages.success(request, f"Appointment for {appointment.full_name} Approved.")
            
            email_subject = 'Appointment Approved - Ministry Portal'
            email_body = f"""
            Dear {appointment.full_name},
            
            Your appointment with {appointment.slot.minister.name} on {appointment.slot.date} at {appointment.slot.start_time} has been APPROVED.
            
            Remarks: {admin_message}
            
            Please bring a valid ID and arrive 15 minutes early.
            
            Regards,
            Ministry Secretariat
            """
            
        elif action == 'reject':
            appointment.status = 'REJECTED'
            appointment.slot.is_booked = False # Free up slot if rejected
            appointment.slot.save()
            messages.warning(request, f"Appointment for {appointment.full_name} Rejected.")
            
            email_subject = 'Appointment Rejected - Ministry Portal'
            email_body = f"""
            Dear {appointment.full_name},
            
            Your appointment request with {appointment.slot.minister.name} on {appointment.slot.date} has been REJECTED.
            
            Reason/Remarks: {admin_message}
            
            You may try booking another slot.
            
            Regards,
            Ministry Secretariat
            """
            
        appointment.save()
        
        # Send Email
        if appointment.email:
            send_mail(
                email_subject,
                email_body,
                None,
                [appointment.email],
                fail_silently=True
            )
        
    return redirect('dashboard:home')
