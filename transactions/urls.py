from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'transactions'

# Create router for viewset
router = DefaultRouter()
router.register(r'', views.TransactionViewSet, basename='transaction')
# router.register(r'reports', views.TransactionReportViewSet, basename='transaction-report')

urlpatterns = [
    # ViewSet routes for YEET transfers (removes extra 'api' prefix)
    path('api/', include(router.urls)),
    
    # Legacy routes for backward compatibility
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/recent/', views.recent_transactions_view, name='recent-transactions'),
    path('validate-receiver/', views.validate_receiver_view, name='validate-receiver'),
    
    # Transaction reporting
    path('api/reports/create/', views.create_transaction_report, name='create-transaction-report'),
    path('api/reports/', views.get_transaction_reports, name='get-transaction-reports'),
]