from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    account_level = serializers.ReadOnlyField(source='get_account_level')
    can_transfer_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'country', 'residential_address', 'account_number',
            'ifsc_code', 'ifsc_verified', 'balance', 'is_verified', 'has_deposit', 'is_basic', 'is_premium',
            'is_business', 'is_prime', 'has_set_transfer_pin', 'can_transfer_enabled',
            'transfer_block_message', 'account_level',
            'can_transfer_status', 'date_joined', 'is_staff'
        ]
        read_only_fields = [
            'id', 'account_number', 'ifsc_code', 'ifsc_verified', 'balance', 'is_verified', 'has_deposit',
            'is_basic', 'is_premium', 'is_business', 'is_prime',
            'has_set_transfer_pin', 'can_transfer_enabled', 'transfer_block_message',
            'account_level', 'can_transfer_status',
            'date_joined'
        ]
    
    def get_can_transfer_status(self, obj):
        """Get transfer eligibility status and message"""
        can_transfer, message = obj.can_transfer()
        return {
            'eligible': can_transfer,
            'message': message
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'country', 'residential_address', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if email already exists
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'A user with this email already exists.'
            })
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Set username to email to ensure uniqueness
        email = validated_data.get('email')
        validated_data['username'] = email
        
        try:
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except IntegrityError as e:
            if 'username' in str(e):
                raise serializers.ValidationError({
                    'email': 'A user with this email already exists.'
                })
            else:
                raise serializers.ValidationError({
                    'non_field_errors': 'Unable to create user. Please try again.'
                })

class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        
        if identifier and password:
            # Try to authenticate with different fields
            user = None
            
            # Try email
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
            
            # Try phone
            if not user:
                try:
                    user_obj = User.objects.get(phone=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            # Try account number
            if not user:
                try:
                    user_obj = User.objects.get(account_number=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            # Try username
            if not user:
                user = authenticate(username=identifier, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include identifier and password')
