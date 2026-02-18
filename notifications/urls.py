from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/mark-read/', views.mark_as_read_view, name='mark-as-read'),
    path('notifications/mark-all-read/', views.mark_all_read_view, name='mark-all-read'),
    path('notifications/unread-count/', views.unread_count_view, name='unread-count'),
    
    # Push notification endpoints
    path('push/subscribe/', views.subscribe_push_view, name='push-subscribe'),
    path('push/unsubscribe/', views.unsubscribe_push_view, name='push-unsubscribe'),
    path('push/status/', views.push_subscription_status_view, name='push-status'),
]