from django.urls import path

from snaver import views
from snaver.views import CategoryListView
from snaver.views import ChartsListView

urlpatterns = [
    path('', CategoryListView.as_view(), name='home'),
    path('', views.index, name='logout'),
    path('budget', CategoryListView.as_view(), name='budget'),
    path('charts', ChartsListView.as_view(), name='charts'),
    path('page-user.html', views.pages)
]
