from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

from todos.models import Category, TodoItem
from todos.serializers import CategorySerializer, TodoItemSerializer


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        if self.queryset.filter(
                name=serializer.validated_data['name'],
                user=self.request.user).exists():
            raise ValidationError('Category name is already existed')
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if 'name' in serializer.validated_data:
            if self.queryset.filter(
                    name=serializer.validated_data['name'],
                    user=self.request.user).exists():
                raise ValidationError('Category name is already existed')

        super().perform_update(serializer)


class TodoItemViewSet(viewsets.ModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            return self.queryset.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotFound('Invalid item pk')

    def get_queryset(self):
        category = Category.objects.get(
            id=self.request.query_params['category_id'])
        if not category or self.request.user != category.user:
            raise ValidationError('Invalid category id')
        return self.queryset.filter(category=category)\
            .order_by('-date_created')

    def perform_create(self, serializer):
        category = Category.objects.get(
            id=serializer.validated_data['category_id'])
        if not category or self.request.user != category.user:
            raise ValidationError('Invalid category')
        serializer.save(category=category)

    def perform_update(self, serializer):
        if 'category_id' in serializer.validated_data:
            category = Category.objects.get(
                id=serializer.validated_data['category_id'])
            if not category or self.request.user != category.user:
                raise ValidationError('Invalid category')
            serializer.save(category=category)
        else:
            super().perform_update(serializer)
