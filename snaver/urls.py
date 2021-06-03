from django.urls import path, re_path

from snaver import views
from snaver.views import CategoryListView, CategoryView
from snaver.views import ChartsListView

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(CategoryListView.as_view()), name='home'),
    path('', views.index, name='logout'),
    path('budget', CategoryListView.as_view(), name='budget'),
    re_path(r'^budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$', CategoryView.as_view(), name='budget_select'),
    path('charts', ChartsListView.as_view(), name='charts'),
    path('page-user.html', views.pages)
]
