from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic.base import TemplateView

from .views import account_activation_sent
from .views import activate
from .views import login_view
from .views import registration_view
from .views import ProfileView, EmailChangeView, EmailChangeDoneView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('registration/', registration_view, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('account_activation_sent/',
         account_activation_sent,
         name="account_activation_sent"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('email_change/<pk>/', EmailChangeView.as_view(), name="email_change"),
    path('email_change_done/', EmailChangeDoneView.as_view(), name="email_change_done"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/$',
        activate,
        name='activate'
        ),
]
