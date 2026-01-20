from django.core.management.base import BaseCommand
from appointments.models import Minister, TimeSlot
from datetime import date, time, timedelta

class Command(BaseCommand):
    help = 'Populates DB with sample data'

    def handle(self, *args, **options):
        # Create Minister
        minister, created = Minister.objects.get_or_create(
            name="Hon. Ram Bahadur Thapa",
            portfolio="Minister of Technology",
            description="Leading the digital transformation of Nepal."
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Minister'))
        
        # Create Slots for next 30 days
        start_date = date.today()
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            # Skip weekends (Saturday is weekly off in Nepal usually)
            if current_date.weekday() == 5: # 5 = Saturday
                continue
                
            # Create slots 10 AM to 12 PM
            for hour in range(10, 12):
                TimeSlot.objects.get_or_create(
                    minister=minister,
                    date=current_date,
                    start_time=time(hour, 0),
                    end_time=time(hour + 1, 0)
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created slots for {minister.name}'))
