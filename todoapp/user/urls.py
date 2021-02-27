from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from user.views import CreateUserView, ManagerUserView


app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='login'),
    path('token_refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', ManagerUserView.as_view(), name='me'),
]
