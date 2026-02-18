"""
ASGI config for yeet_bank project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yeet_bank.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Since we're not actively using WebSocket functionality,
# we'll use the standard Django ASGI application
application = django_asgi_app

# If you need to enable WebSocket support later, uncomment below:
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import notifications.routing
# import chat.routing
#
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             notifications.routing.websocket_urlpatterns +
#             chat.routing.websocket_urlpatterns
#         )
#     ),
# })
