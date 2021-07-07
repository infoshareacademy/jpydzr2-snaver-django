from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import re_path

from snaver import views
# from snaver.views import ChartsListView
from snaver.views import BudgetView
from snaver.views import ReportsListView
from snaver.views import TransactionCreateView
from snaver.views import TransactionListView

urlpatterns = [
    path('', login_required(BudgetView.as_view()), name='home'),
    path('', views.index, name='logout'),
    re_path(r'^budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$',
            login_required(BudgetView.as_view()),
            name='budget_select'),
    # path('charts', ChartsListView.as_view(), name='charts'),
    path('transactions', TransactionListView.as_view(), name='transactions'),
    path('new-transaction', TransactionCreateView.as_view(), name='new-transaction'),

    # Used for ajax updates
    path('update-transaction', views.update_transaction, name="update-transaction"),
    re_path(
        r'update-category|budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/update-category',
        views.ajax_update,
        name="update-category"
    ),
    re_path(
        r'save-ordering|budget/*/save-ordering',
        views.save_ordering,
        name="update-order"
    ),
    path('reports', ReportsListView.as_view(), name='reports')
]
