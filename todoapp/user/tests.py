from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
LOGIN_USER_URL = reverse('user:login')
USER_INFO_URL = reverse('user:me')


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, password=password
    )


class PublicUserApiTests(TestCase):
    """Test API requests that do not require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'username': 'username',
            'password': '12345',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'username': 'username',
            'password': '12345',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than or equal to 5 characters"""
        payload = {
            'username': 'username',
            'password': '1',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            username=payload['username']).exists()
        self.assertFalse(user_exists)

    def test_login_valid_user_success(self):
        """Test that a token is created for the valid user"""
        payload = {
            'username': 'username',
            'password': '12345',
        }

        create_user(username=payload['username'], password=payload['password'])

        res = self.client.post(LOGIN_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_user_not_exists(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            'username': 'username',
            'password': '12345',
        }

        res = self.client.post(LOGIN_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)

    def test_login_user_incorrect_password(self):
        """Test that token is not created if invalid credentials are given"""
        payload = {
            'username': 'username',
            'password': '12345',
        }

        create_user(username=payload['username'], password=payload['password'])

        payload['password'] = 'wrong'
        res = self.client.post(LOGIN_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)

    def test_update_user_unauthorized(self):
        """Test that authentication is required for updating user"""
        payload = {
            'username': 'username',
            'password': '12345',
        }

        create_user(username=payload['username'], password=payload['password'])

        res = self.client.patch(USER_INFO_URL, {
            'username': 'username',
            'password': '111111',
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_unauthorized(self):
        """Test that authentication is required for getting user"""
        payload = {
            'username': 'username',
            'password': '12345',
        }

        create_user(username=payload['username'], password=payload['password'])

        res = self.client.get(USER_INFO_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(username='username', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_success(self):
        """Test getting the user profile for authenticated user"""
        res = self.client.get(USER_INFO_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('username', res.data)
        self.assertNotIn('password', res.data)

    def test_update_user_success(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'username': 'new_username',
            'password': 'new_password',
        }

        res = self.client.put(USER_INFO_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_username_only_success(self):
        """Test updating the username only"""
        payload = {
            'username': 'new_username',
        }

        res = self.client.patch(USER_INFO_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_password_only_success(self):
        """Test updating the password only"""
        payload = {
            'password': 'new_password',
        }

        res = self.client.patch(USER_INFO_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_username_exists(self):
        """Test updating the username which is already existed"""
        payload = {
            'username': 'username2',
            'password': '12345',
        }
        create_user(username=payload['username'], password=payload['password'])

        res = self.client.patch(USER_INFO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
