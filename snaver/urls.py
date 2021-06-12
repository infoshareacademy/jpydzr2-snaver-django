from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import re_path

from snaver import views
from snaver.views import CategoryView
from snaver.views import ChartsListView
from snaver.views import TransactionCreateView
from snaver.views import TransactionListView
from snaver.views import ReportsListView

urlpatterns = [
    path('', login_required(CategoryView.as_view()), name='home'),
    path('', views.index, name='logout'),
    path('budget', login_required(CategoryView.as_view()), name='budget'),
    re_path(r'^budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$',
            login_required(CategoryView.as_view()),
            name='budget_select'),
    path('charts', ChartsListView.as_view(), name='charts'),
    re_path(r'^charts/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$',
            login_required(ChartsListView.as_view()),
            name='charts_select'),
    path('page-user.html', views.pages),
    path('adding-transaction', TransactionListView.as_view(), name='adding'),
    path('add-new', TransactionCreateView.as_view(), name='add_new'),
    path('reports', ReportsListView.as_view(), name='reports'),
    re_path(r'^reports/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$',
            login_required(ReportsListView.as_view()),
            name='reports_select'),
]
