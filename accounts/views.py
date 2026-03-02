from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer
from .email_utils import send_password_reset_email

class RegisterView(generics.CreateAPIView):
    """User registration view"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'id': user.id,
            'email': user.email,
            'account_number': user.account_number,
            'message': 'User registered successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login view"""
    
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })

class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout view"""
    
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_pin_view(request):
    """Change user transfer PIN"""
    
    current_pin = request.data.get('current_pin')
    new_pin = request.data.get('new_pin')
    
    if not new_pin:
        return Response(
            {'error': 'new_pin is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # Check if user has a PIN set
    if user.has_set_transfer_pin and current_pin:
        # User has existing PIN, verify current PIN
        if not user.check_transfer_pin(current_pin):
            return Response(
                {'error': 'Current PIN is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    elif user.has_set_transfer_pin and not current_pin:
        return Response(
            {'error': 'current_pin is required to change existing PIN'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new PIN
    if len(str(new_pin)) != 4 or not str(new_pin).isdigit():
        return Response(
            {'error': 'PIN must be exactly 4 digits'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user.set_transfer_pin(new_pin)
        
        # Create notification
        from notifications.models import Notification
        Notification.objects.create(
            user=user,
            title='🔒 Transfer PIN Updated',
            message='Your transfer PIN has been successfully updated. Use this PIN for all money transfers.',
            notification_type='SECURITY'
        )
        
        return Response({'message': 'Transfer PIN set successfully'})
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Change user password"""
    
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response(
            {'error': 'Both current_password and new_password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # Check current password
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Request a password-reset email.
    Body: { "email": "user@example.com" }
    Always returns 200 so we don't leak whether an email exists.
    """
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response(
            {'error': 'email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    print(f"\n[PASSWORD RESET] Request received for email: {email}")

    try:
        user = User.objects.get(email__iexact=email)
        print(f"[PASSWORD RESET] ✅ User found: {user.username} (id={user.pk})")

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

        print(f"[PASSWORD RESET] Reset link: {reset_link}")

        success = send_password_reset_email(user, reset_link)
        if success:
            print(f"[PASSWORD RESET] ✅ Email dispatched to {user.email}")
        else:
            print(f"[PASSWORD RESET] ❌ Email sending returned False for {user.email}")

        return Response({
            'found': True,
            'message': f'A password reset link has been sent to {user.email}. It expires in 1 hour.'
        })

    except User.DoesNotExist:
        print(f"[PASSWORD RESET] ⚠️  No user found with email: {email} (returning 200 anyway)")
        return Response({
            'found': False,
            'message': f'No account found with the email {email}. Please check the email or create a new account.'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm_view(request):
    """
    Confirm password reset.
    Body: { "uid": "…", "token": "…", "new_password": "…" }
    """
    uid_encoded = request.data.get('uid', '')
    token = request.data.get('token', '')
    new_password = request.data.get('new_password', '')

    if not uid_encoded or not token or not new_password:
        return Response(
            {'error': 'uid, token, and new_password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        uid = force_str(urlsafe_base64_decode(uid_encoded))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response(
            {'error': 'Invalid reset link'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not default_token_generator.check_token(user, token):
        return Response(
            {'error': 'Reset link is invalid or has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password has been reset successfully. You can now log in.'})
