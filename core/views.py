from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import ReferralProfile, Purchase, Earning
from .serializers import UserSerializer, ReferralProfileSerializer, PurchaseSerializer, EarningSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def referrals(self, request):
        profile = request.user.referral_profile
        children = profile.children.all()
        serializer = ReferralProfileSerializer(children, many=True)
        return Response(serializer.data)

class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)

class EarningFilter(filters.FilterSet):
    level = filters.NumberFilter(field_name='level')
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Earning
        fields = ['level', 'start_date', 'end_date']

class EarningViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EarningSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = EarningFilter

    def get_queryset(self):
        return Earning.objects.filter(recipient=self.request.user)
