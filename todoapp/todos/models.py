from django.db import models

from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('name', 'user',)

    def __str__(self):
        return self.name


class TodoItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
