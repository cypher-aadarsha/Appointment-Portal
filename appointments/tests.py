from django.test import TestCase, Client
from django.urls import reverse
from .models import Minister, TimeSlot
from datetime import date, time

class BookingTest(TestCase):
    def setUp(self):
        self.minister = Minister.objects.create(name="Test Min", portfolio="Test Port")
        self.slot = TimeSlot.objects.create(
            minister=self.minister,
            date=date(2025, 4, 14),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        self.client = Client()

    def test_booking_page_loads(self):
        response = self.client.get(reverse('appointments:book_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Min")

    def test_api_slots(self):
        url = reverse('appointments:get_slots')
        response = self.client.get(url, {'minister_id': self.minister.id, 'date': '2025-04-14'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['slots']), 1)
        self.assertEqual(data['slots'][0]['id'], self.slot.id)
