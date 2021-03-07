from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from todos.models import Category, TodoItem
from todos.serializers import CategorySerializer, TodoItemSerializer


CATEGORY_LIST_URL = reverse('todo:category-list')
TODO_ITEM_LIST_URL = reverse('todo:todoitem-list')


def get_todo_item_detail_url(item_id):
    return reverse('todo:todoitem-detail', args=[item_id])


def create_user(username, password):
    return get_user_model().objects.create_user(
        username=username, password=password
    )


def create_sample_cateory(user, name):
    return Category.objects.create(user=user, name=name)


def create_sample_item(category, name):
    return TodoItem.objects.create(category=category, name=name)


class PublicCategoryApiTest(TestCase):
    """Test API requests that do not require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_get_list(self):
        """Test that authentication is required for getting categories"""
        res = self.client.get(CATEGORY_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_create(self):
        """Test that authentication is required for creating category"""
        payload = {
            'name': 'cat_name'
        }
        res = self.client.post(CATEGORY_LIST_URL, payload)

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

        res = self.client.get(CATEGORY_LIST_URL)

        categories = Category.objects.filter(user=self.user).order_by('name')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category(self):
        """Test creating a category by an authenticated user"""
        payload = {
            'name': 'cat_name'
        }
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=res.data['id'])
        for k in payload.keys():
            self.assertEqual(payload[k], getattr(category, k))

    def test_create_category_empty_name(self):
        """Test creating a category with an empty name"""
        payload = {
            'name': '  '
        }
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_null_name(self):
        """Test creating a category without a name"""
        payload = {}
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_duplicated_name(self):
        """Test creating a category with a duplicated name"""
        create_sample_cateory(self.user, 'cat_name')

        payload = {
            'name': 'cat_name'
        }
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PublicTodoItemApiTest(TestCase):
    """Test API requests that do not require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_get_list(self):
        """Test that authentication is required for getting todo items"""
        res = self.client.get(TODO_ITEM_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_create(self):
        """Test that authentication is required for creating item"""
        payload = {
            'name': 'cat_name',
            'category_id': 1
        }
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_update(self):
        """Test that authentication is required for updating item"""
        user = create_user('username2', 'password')
        item = create_sample_item(
            create_sample_cateory(user, 'cat1'), 'item')
        category = create_sample_cateory(user, 'cat2')

        payload = {
            'name': 'new_name',
            'done': True,
            'category_id': category.id,
        }
        res = self.client.put(get_todo_item_detail_url(item.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_destroy(self):
        """Test that authentication is required for destorying item"""
        user = create_user('username2', 'password')
        item = create_sample_item(
            create_sample_cateory(user, 'cat1'), 'item')

        res = self.client.delete(get_todo_item_detail_url(item.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTodoItemApiTest(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(username='username', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_todo_items(self):
        """Test getting all todo items of an authenticated user"""
        cat1 = create_sample_cateory(self.user, name='cat_name1')
        cat2 = create_sample_cateory(self.user, name='cat_name2')

        create_sample_item(cat1, 'name1')
        create_sample_item(cat1, 'name2')
        create_sample_item(cat2, 'name3')

        res = self.client.get(TODO_ITEM_LIST_URL, {'category_id': 1})

        items = TodoItem.objects.filter(
            category=cat1).order_by('-date_created')
        serializer = TodoItemSerializer(items, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_todo_item(self):
        """Test creating an item by an authenticated user"""
        create_sample_cateory(self.user, name='cat_name1')
        payload = {
            'name': 'item',
            'category_id': 1
        }
        res = self.client.post(TODO_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        item = TodoItem.objects.get(id=res.data['id'])
        for k in payload.keys():
            self.assertEqual(payload[k], getattr(item, k))

    def test_create_todo_item_empty_name(self):
        """Test creating an item with an empty name"""
        payload = {
            'name': '  ',
            'category_id': 1
        }
        res = self.client.post(TODO_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_todo_item_null_name(self):
        """Test creating an item without a name"""
        payload = {
            'category_id': 1
        }
        res = self.client.post(TODO_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_todo_item_invalid_category_id(self):
        """Test creating an item with invalid category id"""
        temp_user = create_user('username2', 'password')
        create_sample_cateory(temp_user, name='cat_name1')
        payload = {
            'name': 'item',
            'category_id': 1
        }
        res = self.client.post(TODO_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_todo_item_name(self):
        """Test updating an item name"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')
        payload = {
            'name': 'new item name',
        }
        res = self.client.patch(get_todo_item_detail_url(item.id), payload)

        item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(item.name, payload['name'])

    def test_update_todo_item_empty_name(self):
        """Test updating an item with empty name"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')
        payload = {
            'name': '  ',
        }
        res = self.client.patch(get_todo_item_detail_url(item.id), payload)

        item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(item.name, payload['name'])

    def test_update_todo_item_category_id(self):
        """Test updating the category"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')
        category = create_sample_cateory(self.user, 'cat2')

        payload = {
            'category_id': category.id,
        }
        res = self.client.patch(get_todo_item_detail_url(item.id), payload)

        item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(item.category_id, payload['category_id'])

    def test_update_todo_item_invalid_category_id(self):
        """Test updating the item with an invalid category"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')
        category = create_sample_cateory(
            create_user('username2', 'password'), 'cat2')

        payload = {
            'category_id': category.id,
        }
        res = self.client.patch(get_todo_item_detail_url(item.id), payload)

        item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(item.category_id, payload['category_id'])

    def test_update_todo_item_done(self):
        """Test updating the category"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')

        payload = {
            'done': True,
        }
        res = self.client.patch(get_todo_item_detail_url(item.id), payload)

        item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(item.done, payload['done'])

    def test_full_update_todo_item(self):
        """Test fully updating the category"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')
        category = create_sample_cateory(self.user, 'cat2')

        payload = {
            'name': 'new_name',
            'done': True,
            'category_id': category.id,
        }
        res = self.client.put(get_todo_item_detail_url(item.id), payload)

        item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(item.name, payload['name'])
        self.assertEqual(item.done, payload['done'])
        self.assertEqual(item.category_id, payload['category_id'])

    def test_update_non_exist_todo_item(self):
        """Test updating an non existing item"""

        payload = {
            'name': 'new_name',
        }
        res = self.client.put(get_todo_item_detail_url(999), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_todo_item(self):
        """Test deleting an item"""
        item = create_sample_item(
            create_sample_cateory(self.user, 'cat1'), 'item')

        res = self.client.delete(get_todo_item_detail_url(item.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TodoItem.objects.filter(id=item.id).exists())
