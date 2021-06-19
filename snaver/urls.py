from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import re_path

from snaver import views
from snaver.views import CategoryView
from snaver.views import ChartsListView
from snaver.views import TransactionCreateView
from snaver.views import TransactionListView
from snaver.views import BudgetListView

from snaver.views import load_budget
from snaver.views import update_category

urlpatterns = [
    path('', login_required(CategoryView.as_view()), name='home'),
    path('', views.index, name='logout'),
    path('budget', login_required(CategoryView.as_view()), name='budget'),
    path('budget2', views.load_budget, name='budget2'),
    re_path(r'^budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$',
            login_required(CategoryView.as_view()),
            name='budget_select'),
    path('charts', ChartsListView.as_view(), name='charts'),
    path('page-user.html', views.pages),
    path('adding-transaction', TransactionListView.as_view(), name='adding'),
    path('add-new', TransactionCreateView.as_view(), name='add_new'),
    path('update-category', views.update_category, name="update-category"),
    path('budget3/', BudgetListView.as_view(), name='budget3'),
]
