from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import re_path

from snaver import views
from snaver.views import BudgetView
from snaver.views import CategoryView
from snaver.views import ChartsListView
from snaver.views import TransactionCreateView
from snaver.views import TransactionListView
from snaver.views import ajax_update
from snaver.views import save_ordering
from snaver.views import update_transaction

urlpatterns = [
    path('', login_required(BudgetView.as_view()), name='home'),
    path('', views.index, name='logout'),
    re_path(r'^budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/$',
            login_required(BudgetView.as_view()),
            name='budget_select'),
    path('charts', ChartsListView.as_view(), name='charts'),
    path('adding-transaction', TransactionListView.as_view(), name='adding'),
    path('add-new', TransactionCreateView.as_view(), name='new-transaction'),
    path('update-transaction', views.update_transaction, name="update-transaction"),
    path('ajax-update', views.ajax_update, name="update-category"),
    path('save-ordering', views.save_ordering, name="update-order"),
    re_path(r'^budget/(?P<year>[0-9]{4})(?P<month>[0-9]{2})/ajax-update', views.ajax_update, name="update-category")
]
