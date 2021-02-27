from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
LOGIN_USER_URL = reverse('user:login')


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, password=password
    )


class UserApiTestsWithoutToken(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
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
        payload = {
            'username': 'username',
            'password': '12345',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
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
        payload = {
            'username': 'username',
            'password': '12345',
        }

        res = self.client.post(LOGIN_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)

    def test_login_user_incorrect_password(self):
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
