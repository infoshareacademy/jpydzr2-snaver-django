from django.urls import path

from snaver import views
from snaver.views import CategoryListView

urlpatterns = [
    path('', views.index, name='home'),
    path('', views.index, name='logout'),
    path('budget', CategoryListView.as_view(), name='budget')
]
