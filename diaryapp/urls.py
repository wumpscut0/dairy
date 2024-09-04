from django.contrib.auth.views import logout_then_login
from django.urls import path

from .views import (
    CustomLogoutView, CustomLoginView, UserCreateView, index,
)

app_name = "diaryapp"


urlpatterns = [
    path("", view=index, name="index"),
    path("register/", view=UserCreateView.as_view(), name="register"),
    path("login/", view=CustomLoginView.as_view(), name="login"),
    path("logout/", view=CustomLogoutView.as_view(), name="logout")
]
