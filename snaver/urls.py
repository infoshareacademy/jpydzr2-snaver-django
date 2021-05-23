from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import LoginView

from snaver import views
from snaver.views import CategoryListView
from snaver.views import ChartsListView

urlpatterns = [
    path('', views.index, name='home'),
    path('', views.index, name='logout'),
    path('budget', CategoryListView.as_view(), name='budget'),
    path('charts', ChartsListView.as_view(), name='charts'),
]
