import pytest
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Subscription


@pytest.fixture
def api_client():
    """A fixture that returns an unauthenticated API client"""
    return APIClient()

@pytest.fixture
def test_user():
    """A fixture that creates and returns a user for authentication"""
    return User.objects.create_user(email='testuser@example.com', password='password123')

@pytest.fixture
def authenticated_client(api_client, test_user):
    """A fixture that returns an authenticated client"""
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.mark.django_db
def test_subscription_model_str(test_user):
    """Tests the __str__ method of the Subscription model"""
    subscription = Subscription.objects.create(
        user=test_user,
        city='London',
        notification_period=6,
        notification_method='email'
    )
    assert str(subscription) == 'testuser@example.com - London (6 Hours)'

@pytest.mark.django_db
class TestSubscriptionAPI:
    """Groups tests for the Subscription API endpoints"""

    def test_list_subscriptions_unauthenticated(self, api_client):
        """Tests an unauthenticated user accessing list subscriptions page"""
        response = api_client.get('/api/subscriptions/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_subscriptions_authenticated(self, authenticated_client, test_user):
        """Tests an authenticated user listing their own subscriptions"""
        Subscription.objects.create(
            user=test_user,
            city='Paris',
            notification_period=3,
            notification_method='email'
        )

        other_user = User.objects.create_user(email='other@example.com', password='pw')
        Subscription.objects.create(
            user=other_user,
            city='Berlin',
            notification_period=1,
            notification_method='email'
        )

        response = authenticated_client.get('/api/subscriptions/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['city'] == 'Paris'

    def test_create_subscription(self, authenticated_client):
        """Tests an authenticated user creating a subscription"""
        payload = {
            'city': 'Tokyo',
            'notification_period': 12,
            'notification_method': 'email'
        }
        response = authenticated_client.post('/api/subscriptions/', data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['city'] == 'Tokyo'
        assert Subscription.objects.count() == 1

    def test_retrieve_subscription(self, authenticated_client, test_user):
        """Tests an authenticated user retrieving their own subscription"""
        subscription = Subscription.objects.create(
            user=test_user,
            city='Sydney',
            notification_period=1,
            notification_method='email'
        )
        response = authenticated_client.get(f'/api/subscriptions/{subscription.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['city'] == 'Sydney'

    def test_update_subscription(self, authenticated_client, test_user):
        """Tests an authenticated user updating their subscription"""
        subscription = Subscription.objects.create(
            user=test_user,
            city='Kyiv',
            notification_period=6,
            notification_method='email'
        )
        payload = {'notification_period': 12}
        response = authenticated_client.patch(
            f'/api/subscriptions/{subscription.id}/',
            data=payload
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['notification_period'] == 12

        subscription.refresh_from_db()
        assert subscription.notification_period == 12

    def test_delete_subscription(self, authenticated_client, test_user):
        """Tests an authenticated user deleting their subscription"""
        subscription = Subscription.objects.create(
            user=test_user,
            city='Rome',
            notification_period=1,
            notification_method='email'
        )
        response = authenticated_client.delete(f'/api/subscriptions/{subscription.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Subscription.objects.filter(id=subscription.id).exists()

    def test_user_cannot_access_another_users_subscription(self, authenticated_client):
        """Tests user receiving a 404 error when trying to access another user's subscription"""
        other_user = User.objects.create_user(email='other@example.com', password='pw')
        other_subscription = Subscription.objects.create(user=other_user, city="Forbidden City", notification_period=1)

        response = authenticated_client.get(f'/api/subscriptions/{other_subscription.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_non_existent_subscription(self, authenticated_client):
        """Tests requesting a subscription with an ID that does not exist"""
        non_existent_id = 99999
        response = authenticated_client.get(f'/api/subscriptions/{non_existent_id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_subscription_with_invalid_period(self, authenticated_client):
        """Tests creating a subscription with a notification_period not in the choices"""
        payload = {'city': 'Invalid City', 'notification_period': 5, 'notification_method': 'email'}
        response = authenticated_client.post('/api/subscriptions/', data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'notification_period' in response.data

    @pytest.mark.parametrize('input_method, expected_method', [
        ('email', 'email'),
        ('Email', 'email'),
        ('EMAIL', 'email'),
        ('webhook', 'webhook'),
        ('WEBHOOK', 'webhook'),
    ])
    def test_create_subscription_case_insensitive_method(
            self,
            authenticated_client,
            input_method,
            expected_method
    ):
        """Tests the notification_method field accepting case-insensitive values"""
        payload = {
            'city': 'Case Test City',
            'notification_period': 1,
            'notification_method': input_method,
        }
        if expected_method == 'webhook':
            payload['webhook_url'] = 'http://example.com/hook'

        response = authenticated_client.post('/api/subscriptions/', data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['notification_method'] == expected_method

    @pytest.mark.parametrize('input_city, expected_city', [
        ('london', 'London'),
        ('PARIS', 'Paris'),
        ('nEw yOrK', 'New York'),
        ('  berlin  ', 'Berlin'),
    ])
    def test_create_subscription_city_normalization(
            self,
            authenticated_client,
            input_city,
            expected_city
    ):
        """Tests the city field normalizing to a standard format"""
        payload = {
            'city': input_city,
            'notification_period': 1,
            'notification_method': 'email',
        }
        response = authenticated_client.post('/api/subscriptions/', data=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['city'] == expected_city