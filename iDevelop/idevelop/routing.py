from django.urls import path
from idevelop import consumers

websocket_urlpatterns = [
    path('idevelop/collab', consumers.MyConsumer.as_asgi()),
]