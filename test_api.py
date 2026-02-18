#!/usr/bin/env python
"""
Test script for Yeet Bank API
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_registration():
    """Test user registration"""
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'country': 'USA',
        'residential_address': '123 Main St',
        'password': 'testpass123',
        'password_confirm': 'testpass123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/register/', json=data, timeout=10)
        print(f'Registration: {response.status_code}')
        if response.status_code == 201:
            result = response.json()
            print(f'User ID: {result.get("id")}')
            print(f'Account Number: {result.get("account_number")}')
            return result
        else:
            print(f'Error: {response.text}')
            return None
    except Exception as e:
        print(f'Exception: {e}')
        return None

def test_login():
    """Test user login"""
    data = {
        'identifier': 'john.doe@example.com',
        'password': 'testpass123'
    }
    
    response = requests.post(f'{BASE_URL}/auth/login/', json=data)
    print(f'Login: {response.status_code}')
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None

def test_profile(access_token):
    """Test profile retrieval"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{BASE_URL}/user/profile/', headers=headers)
    print(f'Profile: {response.status_code}')
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)

if __name__ == '__main__':
    print("Testing Yeet Bank API...")
    
    # Test registration
    reg_result = test_registration()
    if reg_result:
        print("Registration successful!")
        
        # Test login
        login_result = test_login()
        if login_result:
            print("Login successful!")
            access_token = login_result.get('access')
            
            # Test profile
            test_profile(access_token)
        else:
            print("Login failed!")
    else:
        print("Registration failed!")