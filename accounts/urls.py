from django.urls import path
from .views import login_view, registration_view
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', login_view, name="login"),
    path('registration/', registration_view, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('account_activation_sent/', registration_view.account_activation_sent, name="account_activation_sent"),
]