import pytest
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


@pytest.fixture
def api_client():
    """A fixture that returns an unauthenticated API client"""
    return APIClient()

@pytest.mark.django_db
class TestUserAPI:
    """Tests for user registration and authentication"""

    def test_user_registration_success(self, api_client):
        """Tests a new user being registered successfully via the API"""
        payload = {
            'email': 'register_test@example.com',
            'password': 'testpassword123'
        }
        response = api_client.post('/api/users/register/', data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=payload['email']).exists()

    def test_user_registration_duplicate_email(self, api_client):
        """Tests registering with an email that already exists"""
        existing_email = 'duplicate@example.com'
        User.objects.create_user(email=existing_email, password='password')

        payload = {
            'email': existing_email,
            'password': 'anotherpassword'
        }

        response = api_client.post('/api/users/register/', data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_get_jwt_token_success(self, api_client):
        """Tests a registered user obtaining a JWT token with valid credentials"""
        email = 'token_user@example.com'
        password = 'strongpassword'
        User.objects.create_user(email=email, password=password)

        payload = {
            'email': email,
            'password': password
        }

        response = api_client.post('/api/users/token/', data=payload)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_get_jwt_token_invalid_credentials(self, api_client):
        """Tests attempting to get a token with invalid credentials"""
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/users/token/', data=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, api_client):
        """Tests a valid refresh token being used to obtain a new access token"""
        email = 'refresh_user@example.com'
        password = 'password123'
        User.objects.create_user(email=email, password=password)
        token_response = api_client.post('/api/users/token/', data={'email': email, 'password': password})
        refresh_token = token_response.data['refresh']

        refresh_payload = {'refresh': refresh_token}
        response = api_client.post('/api/users/token/refresh/', data=refresh_payload)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' not in response.data