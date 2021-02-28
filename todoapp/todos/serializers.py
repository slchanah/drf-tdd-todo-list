from rest_framework import serializers

from todos.models import TodoItem, Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', )
        read_only_fields = ('id',)


class TodoItemSerializer(serializers.ModelSerializer):

    category_id = serializers.IntegerField(
        write_only=True,
    )

    class Meta:
        model = TodoItem
        fields = ('id', 'name', 'done', 'date_created', 'category_id',)
        read_only_fields = ('id', 'date_created',)
