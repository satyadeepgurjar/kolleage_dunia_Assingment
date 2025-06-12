from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import ReferralProfile, Purchase, Earning

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'parent_id']

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        if parent_id:
            parent_profile = ReferralProfile.objects.get(pk=parent_id)
            user.referral_profile.parent = parent_profile
            user.referral_profile.save()
        return user

class ReferralProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ReferralProfile
        fields = ['id', 'user', 'parent', 'level', 'direct_count']

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'amount', 'created_at']

    def validate_amount(self, value):
        if value < Decimal('1000.00'):
            raise serializers.ValidationError("Purchases must be at least ₹1000 to earn referrals.")
        return value

    def create(self, validated_data):
        return Purchase.objects.create(user=self.context['request'].user, **validated_data)

class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earning
        fields = ['id', 'source_purchase', 'level', 'percentage', 'amount', 'created_at']
