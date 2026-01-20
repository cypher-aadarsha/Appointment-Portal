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

def appointment_action(request, appointment_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if action == 'approve':
            appointment.status = 'APPROVED'
            appointment.slot.is_booked = True # Confirm slot booking
            appointment.slot.save()
            messages.success(request, f"Appointment for {appointment.full_name} Approved.")
        elif action == 'reject':
            appointment.status = 'REJECTED'
            appointment.slot.is_booked = False # Free up slot if rejected
            appointment.slot.save()
            messages.warning(request, f"Appointment for {appointment.full_name} Rejected.")
            
        appointment.save()
        
    return redirect('dashboard:home')
