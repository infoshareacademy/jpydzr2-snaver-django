from django.urls import path
from .views import login_view, registration_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"), # EXAMPLE LOGIN PATH #
    path('registration/', registration_view, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"), # EXAMPLE LOGIN PATH #
]
