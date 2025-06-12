from django.urls import re_path
from .consumers import EarningConsumer

websocket_urlpatterns = [
    re_path(r'ws/earnings/(?P<user_id>\d+)/$', EarningConsumer.as_asgi()),
]
