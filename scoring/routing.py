from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/scoring/(?P<match_id>\d+)/$', consumers.ScoringConsumer.as_asgi()),
]