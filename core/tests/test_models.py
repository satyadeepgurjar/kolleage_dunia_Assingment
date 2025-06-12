from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import ReferralProfile

User = get_user_model()

class ReferralProfileModelTests(TestCase):
    def setUp(self):
        self.root = User.objects.create_user("root", password="pass")
        self.root_profile = self.root.referral_profile

    def test_auto_level_and_parent(self):
        child = User.objects.create_user("child", password="pass")
        child_profile = child.referral_profile
        child_profile.parent = self.root_profile
        child_profile.save()
        self.assertEqual(child_profile.level, 2)

    def test_max_direct_referrals(self):
        for i in range(8):
            u = User.objects.create_user(f"u{i}", password="pass")
            p = u.referral_profile
            p.parent = self.root_profile
            p.save()
        ninth = User.objects.create_user("u9", password="pass")
        ninth_profile = ninth.referral_profile
        ninth_profile.parent = self.root_profile
        with self.assertRaises(ValidationError):
            ninth_profile.full_clean()

    def test_self_referral_and_cycle(self):
        with self.assertRaises(ValidationError):
            self.root_profile.parent = self.root_profile
            self.root_profile.full_clean()
        b = User.objects.create_user("b", password="pass")
        c = User.objects.create_user("c", password="pass")
        bp, cp = b.referral_profile, c.referral_profile
        bp.parent = self.root_profile; bp.save()
        cp.parent = bp; cp.save()
        self.root_profile.parent = cp
        with self.assertRaises(ValidationError):
            self.root_profile.full_clean()
