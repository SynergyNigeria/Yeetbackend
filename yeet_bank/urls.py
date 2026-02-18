"""
URL configuration for yeet_bank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from transactions import views as transaction_views

def health_check(request):
    """Simple health check endpoint for monitoring"""
    return JsonResponse({'status': 'ok', 'message': 'YEET Bank API is running'})

urlpatterns = [
    path('', health_check, name='health-check'),  # Root health check
    path('health/', health_check, name='health'),  # Alternative health check
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),  # Updated path
    path('api/', include('notifications.urls')),
    path('api/chat/', include('chat.urls')),
    
    # Legacy transfer endpoint aliases for frontend compatibility
    path('api/transfers/history/', transaction_views.TransactionListView.as_view(), name='transfer-history'),
    path('api/transfers/validate-receiver/', transaction_views.validate_receiver_view, name='validate-receiver'),
    path('api/transfers/yeet-transfer/', transaction_views.TransactionCreateView.as_view(), name='legacy-yeet-transfer'),
    path('api/transfers/wire-transfer/', transaction_views.TransactionCreateView.as_view(), name='legacy-wire-transfer'),
    path('api/transfers/wire-transfer/', transaction_views.TransactionCreateView.as_view(), name='wire-transfer'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
