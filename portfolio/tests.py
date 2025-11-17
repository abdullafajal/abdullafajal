import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import ChatLog

class AgentAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('portfolio:agent_query')

    def test_agent_query_success(self):
        """
        Test that the agent_query endpoint returns a successful JSON response.
        """
        payload = {'prompt': 'hello'}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()
        self.assertIn('text', data)
        self.assertIn('action', data)
        self.assertIn('type', data['action'])
        self.assertIn('value', data['action'])
        self.assertTrue(isinstance(data['text'], str) and len(data['text']) > 0)

    def test_chatlog_creation(self):
        """
        Test that a ChatLog entry is created after a successful query.
        """
        self.assertEqual(ChatLog.objects.count(), 0)
        
        payload = {'prompt': 'what are your skills?'}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatLog.objects.count(), 1)

        log = ChatLog.objects.first()
        self.assertEqual(log.user_message, 'what are your skills?')
        self.assertIn('Python', log.agent_response)

    def test_invalid_method(self):
        """
        Test that the endpoint returns an error for non-POST requests.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_empty_prompt(self):
        """
        Test that the endpoint returns an error for an empty prompt.
        """
        payload = {'prompt': ''}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_ics_generation(self):
        """
        Test the ICS file generation for a meeting request.
        """
        payload = {'prompt': 'let\'s schedule a meeting'}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')
        self.assertIn('attachment; filename="meeting.ics"', response['Content-Disposition'])
        
        content = response.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('SUMMARY:Meeting with Abdulla', content)