from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Purchase, Earning

@receiver(post_save, sender=Purchase)
def distribute_earnings(sender, instance, created, **kwargs):
    if not created or instance.amount < Decimal('1000.00'):
        return

    profile = instance.user.referral_profile
    channel_layer = get_channel_layer()

    parent_profile = profile.parent
    if parent_profile and parent_profile.user.is_active:
        direct_pct = Decimal('5.00')
        direct_amount = (instance.amount * direct_pct / Decimal('100')).quantize(Decimal('0.01'))
        e1 = Earning.objects.create(recipient=parent_profile.user, source_purchase=instance, level=1, percentage=direct_pct, amount=direct_amount)
        async_to_sync(channel_layer.group_send)(f"earnings_{parent_profile.user.id}", {"type": "earning_notification", "earning": {"id": e1.id, "level": 1, "amount": str(direct_amount), "percentage": str(direct_pct)}})

    grandparent = parent_profile.parent if parent_profile else None
    if grandparent and grandparent.user.is_active:
        indirect_pct = Decimal('1.00')
        indirect_amount = (instance.amount * indirect_pct / Decimal('100')).quantize(Decimal('0.01'))
        e2 = Earning.objects.create(recipient=grandparent.user, source_purchase=instance, level=2, percentage=indirect_pct, amount=indirect_amount)
        async_to_sync(channel_layer.group_send)(f"earnings_{grandparent.user.id}", {"type": "earning_notification", "earning": {"id": e2.id, "level": 2, "amount": str(indirect_amount), "percentage": str(indirect_pct)}})
