from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Purchase, Earning

User = get_user_model()

class PurchaseSignalTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user("a", password="pass")
        self.b = User.objects.create_user("b", password="pass")
        self.c = User.objects.create_user("c", password="pass")
        self.b.referral_profile.parent = self.a.referral_profile; self.b.referral_profile.save()
        self.c.referral_profile.parent = self.b.referral_profile; self.c.referral_profile.save()

    def test_no_earnings_below_threshold(self):
        Purchase.objects.create(user=self.c, amount=Decimal('999.99'))
        self.assertEqual(Earning.objects.count(), 0)

    def test_direct_and_indirect_earnings(self):
        p = Purchase.objects.create(user=self.c, amount=Decimal('2000.00'))
        earnings = Earning.objects.filter(source_purchase=p)
        self.assertEqual(earnings.count(), 2)
        direct = earnings.get(recipient=self.b)
        indirect = earnings.get(recipient=self.a)
        self.assertEqual(direct.amount, Decimal('100.00'))
        self.assertEqual(indirect.amount, Decimal('20.00'))

    def test_skip_inactive_users(self):
        self.b.is_active = False
        self.b.save()
        Purchase.objects.create(user=self.c, amount=Decimal('1500.00'))
        recips = list(Earning.objects.values_list('recipient__username', flat=True))
        self.assertNotIn('b', recips)
        self.assertIn('a', recips)
