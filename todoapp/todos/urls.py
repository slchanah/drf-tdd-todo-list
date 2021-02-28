from django.urls import path, include
from rest_framework.routers import DefaultRouter

from todos.views import CategoryViewSet, TodoItemViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('items', TodoItemViewSet)

app_name = 'todo'

urlpatterns = [
    path('', include(router.urls)),
]
