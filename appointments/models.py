from django.db import models
from django.utils.translation import gettext_lazy as _

class Minister(models.Model):
    name = models.CharField(max_length=200)
    portfolio = models.CharField(max_length=200, help_text="e.g. Minister of Finance")
    ministry_name = models.CharField(max_length=200, default="Ministry of ...")
    photo = models.ImageField(upload_to='ministers/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.portfolio})"

class TimeSlot(models.Model):
    minister = models.ForeignKey(Minister, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('minister', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} | {self.start_time} - {self.end_time}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    
    # User Details (Public)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    purpose = models.TextField(help_text="Reason for appointment")
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for approval/rejection")

    def __str__(self):
        return f"{self.full_name} - {self.slot}"
