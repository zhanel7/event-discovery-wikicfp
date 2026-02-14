from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Conference

User = get_user_model()

class ConferenceModelTest(TestCase):
    def test_create_conference(self):
        user = User.objects.create_user(username='creator', password='pass')
        conference = Conference.objects.create(
            title='Test Conference',
            description='Description',
            start_date='2025-01-01',
            end_date='2025-01-02',
            location='Test City',
            website='http://test.com',
            created_by=user
        )
        self.assertEqual(str(conference), 'Test Conference')

class ConferenceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user', password='pass', role='user')
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.conference_data = {
            'title': 'API Test Conf',
            'description': 'Desc',
            'start_date': '2025-03-01',
            'end_date': '2025-03-02',
            'location': 'Location',
            'website': 'http://example.com'
        }

    def test_list_conferences_public(self):
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_conference_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/events/', self.conference_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_conference_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/events/', self.conference_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conference.objects.count(), 1)