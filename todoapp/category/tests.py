from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from category.models import Category
from category.serializers import CategorySerializer


CATEGORY_URL = reverse('category:category-list')


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, password=password
    )


def create_sample_cateory(user, name):
    return Category.objects.create(user=user, name=name)


class PublicCategoryApiTest(TestCase):
    """Test API requests that do not require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_get_list(self):
        """Test that authentication is required for getting categories"""
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_create(self):
        """Test that authentication is required for creating category"""
        payload = {
            'name': 'cat_name'
        }
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTest(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(username='username', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_categories(self):
        """Test getting all categories of an authenticated user"""
        create_sample_cateory(self.user, name='cat_name1')
        create_sample_cateory(self.user, name='cat_name2')

        create_sample_cateory(create_user(
            'username2', 'password'), name='cat_name1')

        res = self.client.get(CATEGORY_URL)

        categories = Category.objects.filter(user=self.user).order_by('name')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category(self):
        """Test creating a category by an authenticated user"""
        payload = {
            'name': 'cat_name'
        }
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=res.data['id'])
        for k in payload.keys():
            self.assertEqual(payload[k], getattr(category, k))

    def test_create_category_empty_name(self):
        """Test creating a category with an empty name"""
        payload = {
            'name': '  '
        }
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_null_name(self):
        """Test creating a category without a name"""
        payload = {}
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_duplicated_name(self):
        """Test creating a category with a duplicated name"""
        create_sample_cateory(self.user, 'cat_name')

        payload = {
            'name': 'cat_name'
        }
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)