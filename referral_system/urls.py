from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.views import UserViewSet, PurchaseViewSet, EarningViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'earnings', EarningViewSet, basename='earning')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
