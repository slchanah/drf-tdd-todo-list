from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.queryset.filter(
            name=serializer.validated_data['name'], user=self.request.user
        ):
            return Response({
                'message': 'Category name is already existed'
            }, status=status.HTTP_409_CONFLICT)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class TodoItemViewSet(viewsets.ModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer
    permission_classes = (IsAuthenticated,)

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
