from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import account_activation_sent
from .views import activate
from .views import login_view
from .views import registration_view

urlpatterns = [
    path('login/', login_view, name="login"),
    path('registration/', registration_view, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('account_activation_sent/', account_activation_sent, name="account_activation_sent"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/$',
        activate, name='activate'),
]