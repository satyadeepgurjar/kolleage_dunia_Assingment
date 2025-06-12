from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class ReferralProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='referral_profile', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    level = models.PositiveSmallIntegerField(default=1)
    direct_count = models.PositiveSmallIntegerField(default=0)

    def clean(self):
        if self.parent and self._state.adding:
            if self.parent.children.count() >= 8:
                raise ValidationError("Parent already has 8 direct referrals.")
        if self.parent and self.parent.user == self.user:
            raise ValidationError("Cannot refer yourself.")
        ancestor = self.parent
        while ancestor:
            if ancestor.user == self.user:
                raise ValidationError("Referral cycle detected.")
            ancestor = ancestor.parent

    def save(self, *args, **kwargs):
        self.clean()
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} (Level {self.level})"

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase #{self.id} by {self.user.username}: ₹{self.amount}"

class Earning(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='earnings', on_delete=models.CASCADE)
    source_purchase = models.ForeignKey(Purchase, related_name='earnings', on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Earning #{self.id} for {self.recipient.username}: Level {self.level} – ₹{self.amount}"
