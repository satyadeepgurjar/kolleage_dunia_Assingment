from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import Purchase

User = get_user_model()

class APITests(APITestCase):
    def setUp(self):
        self.a = User.objects.create_user("alice", password="pass")
        self.b = User.objects.create_user("bob", password="pass")
        self.b.referral_profile.parent = self.a.referral_profile; self.b.referral_profile.save()

    def test_signup(self):
        url = reverse('user-list')
        data = {'username': 'charlie', 'password': 'pass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='charlie').exists())

    def test_purchase_validation(self):
        self.client.login(username='bob', password='pass')
        url = reverse('purchase-list')
        resp = self.client.post(url, {'amount': 500})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.client.post(url, {'amount': 1200})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_earnings_endpoint_and_filters(self):
        self.client.login(username='bob', password='pass')
        Purchase.objects.create(user=self.b, amount=Decimal('2000.00'))
        url = reverse('earning-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(e['level'] == 1 for e in resp.data))
        resp2 = self.client.get(url + '?level=1')
        for e in resp2.data:
            self.assertEqual(e['level'], 1)
