from calendar import monthrange
from datetime import datetime
from decimal import Decimal

from django import template
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils import dateformat
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.views.generic import ListView

from snaver.forms import TransactionCreateForm
from snaver.helpers import next_month
from snaver.helpers import prev_month
from snaver.models import Category
from snaver.models import Subcategory
from snaver.models import SubcategoryDetails
from snaver.models import Transaction


@login_required
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionCreateForm

    success_url = reverse_lazy('transactions')
    template_name = 'add-new.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TransactionListView(generic.ListView):
    model = Transaction
    template_name = 'adding-transactions.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None

        transaction_details = {
            'transaction_list': self.model.objects.filter(
                subcategory__category__budget__user=self.request.user),
        }
        return transaction_details

    def get_context_data(self, **kwargs):
        context = super(TransactionListView, self).get_context_data(**kwargs)
        context.update({
            'subcategory_list': Subcategory.objects.filter(
                category__budget__user=self.request.user)
        })
        return context


class ChartsListView(ListView):
    template_name = 'charts.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None

        # date has to be string for filter
        current_time = dateformat.format(timezone.now(), 'Y-m-d')

        subcategory_details = SubcategoryDetails.objects.filter(
            subcategory__category__budget__user=self.request.user,
            start_date__lte=current_time,
            end_date__gte=current_time,
        ).order_by(
            "subcategory__category__name",
            "subcategory__name"
        ).annotate(
            activity=Coalesce(  # Coalesce picks first non-null value
                Sum('subcategory__transaction__outflow'),
                Decimal(0.00)
            ),
            available=(
                    F("budgeted_amount")
                    - Sum('subcategory__transaction__outflow')
            )
        )

        total_expenses = (
            SubcategoryDetails.objects.filter(
                subcategory__category__budget__user=self.request.user,
                start_date__lte=current_time,
                end_date__gte=current_time,
            ).aggregate(Sum('subcategory__transaction__outflow'))
        )

        total_budgeted = (
            SubcategoryDetails.objects.filter(
                subcategory__category__budget__user=self.request.user,
                start_date__lte=current_time,
                end_date__gte=current_time,
            ).aggregate(Sum('budgeted_amount'))
        )

        return (
            subcategory_details,
            total_expenses['subcategory__transaction__outflow__sum'],
            total_budgeted["budgeted_amount__sum"],
        )


@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:

        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('500.html')
        return HttpResponse(html_template.render(context, request))


@csrf_exempt
def ajax_update(request, year=None, month=None):
    user = request.user
    budget = user.budgets.first()

    id = request.POST.get('id')
    type = request.POST.get('type')
    value = request.POST.get('value')

    def _set_current_date(year, month):
        if year is None:
            year = str(datetime.now().year)
        if month is None:
            month = f"{datetime.now().month:02d}"

        return year, month

    def _this_months_range(year, month):
        day = monthrange(year, month)[1]  # the last day of the month
        first_day = datetime(
            year=year,
            month=month,
            day=1,
        )
        last_day = datetime(
            year=year,
            month=month,
            day=day,
        )
        return first_day, last_day

    year, month = _set_current_date(year, month)
    first_day, last_day = _this_months_range(int(year), int(month))

    # UPDATE SUBCATEGORY NAME
    if type == 'subcategory-name':
        subcategory = Subcategory.objects.get(id=id)
        subcategory.name = value
        subcategory.save()

    # UPDATE BUDGETED AMOUNT
    if type == 'budgeted-amount':
        subcategory = SubcategoryDetails.objects.get(id=id)
        subcategory.budgeted_amount = value
        subcategory.save()

    # CREATE NEW SUBCATEGORY
    if type == 'new-category':
        category = Category(name=value, budget_id=budget.id, order=1)
        print(category)
        category.save()

    if type == 'new-subcategory':
        subcategory = Subcategory(name=value, category_id=id)
        subcategory.save()

    if type == 'new-budget':
        subcategory_obj = Subcategory.objects.get(id=id)
        print(subcategory_obj)
        detail = SubcategoryDetails(
            budgeted_amount=value,
            start_date=first_day,
            end_date=last_day,
            subcategory=subcategory_obj
        )
        detail.save()

    return JsonResponse({"success": "Object updated"})


@csrf_exempt
def update_transaction(request):
    id = request.POST.get('id', '')
    type = request.POST.get('type', '')
    value = request.POST.get('value', '')

    if type == 'transaction_date':
        print(value)
        transaction = Transaction.objects.get(id=id)
        transaction.receipt_date = value
        transaction.save()

    if type == 'payee_name':
        transaction = Transaction.objects.get(id=id)
        transaction.payee_name = value
        transaction.save()

    if type == 'transaction_subcategory':
        transaction = Transaction.objects.get(id=id)
        transaction.subcategory = Subcategory.objects.get(id=value)
        transaction.save()

    if type == 'transaction_name':
        transaction = Transaction.objects.get(id=id)
        transaction.name = value
        transaction.save()

    if type == 'outflow':
        transaction = Transaction.objects.get(id=id)
        transaction.outflow = value
        transaction.save()

    if type == 'inflow':
        transaction = Transaction.objects.get(id=id)
        transaction.inflow = value
        transaction.save()

    return JsonResponse({"success": "Object updated"})


class BudgetView(ListView):
    model = Category
    template_name = 'budget.html'

    def set_current_date(self):
        if not self.kwargs.get("year", None):
            self.kwargs["year"] = str(datetime.now().year)
        if not self.kwargs.get("month", None):
            self.kwargs["month"] = f"{datetime.now().month:02d}"

    def months_range(self, year, month):
        day = monthrange(year, month)[1]  # the last day of the month
        first_day = datetime(
            year=year,
            month=month,
            day=1,
        )
        last_day = datetime(
            year=year,
            month=month,
            day=day,
        )
        return first_day, last_day

    def sum_budgeted(self):
        queryset = Subcategory.objects.filter(
            category__budget_id=self.request.user.budgets.first().id
        ).aggregate(
            to_be_budgeted=Coalesce(
                Sum('transactions__inflow'), Decimal(0.00)
            ) - Coalesce(
                Sum('details__budgeted_amount'), Decimal(0.00)
            )
        )
        # quantize to change 0 to 0.00
        return queryset["to_be_budgeted"].quantize(Decimal('.00'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.set_current_date()
        first_day, last_day = self.months_range(
            year=int(self.kwargs["year"]),
            month=int(self.kwargs["month"])
        )

        context['prev_month'] = prev_month(last_day)
        context['next_month'] = next_month(last_day)

        context['to_be_budgeted'] = self.sum_budgeted()

        return context

    def get_queryset(self):
        self.set_current_date()
        first_day, last_day = self.months_range(
            year=int(self.kwargs["year"]),
            month=int(self.kwargs["month"])
        )

        queryset = self.model.objects.filter(
            budget_id=self.request.user.budgets.first().id
        ).order_by('order', '-created_on') \
            .select_related() \
            .prefetch_related(
            Prefetch(
                "subcategories",
                queryset=Subcategory.objects.all().order_by('order', '-created_on')
                    .annotate(
                    activity=Coalesce(
                        Sum('transactions__outflow',
                            filter=Q(
                                transactions__receipt_date__lte=last_day,
                                transactions__receipt_date__gte=first_day,
                            ), distinct=True), Decimal(0.00)
                    ),
                    available=Coalesce(
                        Sum('details__budgeted_amount',
                            filter=Q(details__end_date__lte=last_day),
                            distinct=True),
                        Decimal(0.00)
                    ) - Coalesce(
                        Sum('transactions__outflow',
                            filter=Q(transactions__receipt_date__lte=last_day),
                            distinct=True),
                        Decimal(0.00)
                    ),
                    budgeted=Coalesce(
                        Sum('details__budgeted_amount',
                            filter=Q(
                                details__end_date__lte=last_day,
                                details__end_date__gte=first_day,
                            ),
                            distinct=True),
                        Decimal(0.00)
                    ),
                )
            ),
            Prefetch(
                "subcategories__details",
                queryset=SubcategoryDetails.objects.filter(
                    start_date__lte=last_day,
                    end_date__gte=first_day
                )
            ),
        )

        return queryset


@csrf_exempt
def save_ordering(request):
    categories = request.POST.get('categories')
    categories_ids = categories.split(',')

    subcategories = request.POST.get('subcategories')
    subcategories_ids = subcategories.split(',')

    with transaction.atomic():
        current_order = 1
        for lookup_id in categories_ids:
            category = Category.objects.get(id=lookup_id)
            category.order = current_order
            category.save()
            current_order += 1

    with transaction.atomic():
        current_order = 1
        for lookup_id in subcategories_ids:
            subcategory = Subcategory.objects.get(id=lookup_id)
            subcategory.order = current_order
            subcategory.save()
            current_order += 1
    return JsonResponse({"success": "Order updated"})


class ReportsListView(ListView):
    template_name = 'reports.html'

    def _set_current_date(self):
        if not self.kwargs.get("year", None):
            self.kwargs["year"] = str(datetime.now().year)
        if not self.kwargs.get("month", None):
            self.kwargs["month"] = f"{datetime.now().month:02d}"

    def _this_month(self):
        selected_date = datetime(
            year=int(self.kwargs["year"]),
            month=int(self.kwargs["month"]),
            day=1
        )
        return selected_date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._set_current_date()
        selected_date = self._this_month()
        context['prev_month'] = prev_month(selected_date)
        context['next_month'] = next_month(selected_date)
        return context

    def get_queryset(self, *args, **kwargs):
        self._set_current_date()
        selected_date = dateformat.format(
            self._this_month(),
            'Y-m-d')

        subcategory_details = SubcategoryDetails.objects.filter(
            subcategory__category__budget__user=self.request.user,
            start_date__lte=selected_date,
            end_date__gte=selected_date,
        ).order_by(
            "subcategory__category__name",
            "subcategory__name"
        ).annotate(
            activity=Coalesce(  # Coalesce picks first non-null value
                Sum('subcategory__transactions__outflow',
                    filter=Q(
                        subcategory__transactions__receipt_date__lte=F("end_date"),
                        subcategory__transactions__receipt_date__gte=F("start_date")
                    )
                    ),
                Decimal(0.00),
            )
        ).annotate(
            available=(
                    F("budgeted_amount") - F("activity")
            )
        )

        return subcategory_details