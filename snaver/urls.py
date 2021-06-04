from django.urls import path

from snaver import views
from snaver.views import CategoryListView, TransactionListView
from snaver.views import ChartsListView
from snaver.views import TransactionCreateView

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(CategoryListView.as_view()), name='home'),
    path('', views.index, name='logout'),
    path('budget', CategoryListView.as_view(), name='budget'),
    path('charts', ChartsListView.as_view(), name='charts'),
    path('page-user.html', views.pages),
    path('adding-transaction', TransactionListView.as_view(), name='adding'),
    path('add-new', TransactionCreateView.as_view(), name='add_new'),
]


