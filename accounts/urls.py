from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Password reset (unauthenticated)
    path('auth/forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('auth/reset-password/', views.reset_password_confirm_view, name='reset-password'),
    path('user/profile/', views.ProfileView.as_view(), name='profile'),
    path('user/change-pin/', views.change_pin_view, name='change-pin'),
    path('user/change-password/', views.change_password_view, name='change-password'),
]