from django.contrib import admin

from todos import models


admin.register(models.Category)
admin.register(models.TodoItem)
