from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import (
    RegistrationView,
    UserLoginView,
    UserProfileView,
    ActivationView,
    ChangePasswordView,
    GetAllUserViewset,
)

router = DefaultRouter()
router.register("get_all_users", GetAllUserViewset, basename="get_all_users")

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("activate/<str:activation_code>/", ActivationView.as_view(), name="activate"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("user-profile/", UserProfileView.as_view(), name="user-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("", include(router.urls)),
]
