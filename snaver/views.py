from calendar import monthrange
from datetime import datetime
from decimal import Decimal

from django.http import JsonResponse

from django import template
from django.contrib.auth.decorators import login_required
from django.db.models import F, Prefetch
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils import dateformat
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

from snaver.forms import TransactionCreateForm
from snaver.helpers import next_month
from snaver.helpers import prev_month
from snaver.models import Subcategory, Budget
from snaver.models import Category
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

    success_url = reverse_lazy('adding')
    template_name = 'add-new.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TransactionListView(ListView):
    model = Transaction
    template_name = 'adding-transactions.html'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None

        transaction_details = self.model.objects.filter(
            subcategory__category__budget__user=self.request.user)
        return transaction_details

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CategoryView(ListView):
    template_name = "budget.html"

    def _set_current_date(self):
        if not self.kwargs.get("year", None):
            self.kwargs["year"] = str(datetime.now().year)
        if not self.kwargs.get("month", None):
            self.kwargs["month"] = f"{datetime.now().month:02d}"

    def _this_months_range(self):
        year = int(self.kwargs["year"])
        month = int(self.kwargs["month"])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._set_current_date()
        _, last_day = self._this_months_range()
        context['prev_month'] = prev_month(last_day)
        context['next_month'] = next_month(last_day)
        return context

    def get_queryset(self, *args, **kwargs):
        self._set_current_date()
        first_day, last_day = self._this_months_range()

        # https://stackoverflow.com/a/64902200/5947738
        # Dummy group by column forces Django to Sum values correctly
        past_budgeted_subquery = SubcategoryDetails.objects.filter(
            subcategory__id=OuterRef('id'),
            start_date__lte=first_day,
        ).annotate(
            dummy_group_by=Value(1)
        ).values(
            'dummy_group_by'
        ).annotate(
            past_budgeted=Sum("budgeted_amount")
        ).values("past_budgeted")

        budgeted_subquery = SubcategoryDetails.objects.filter(
            subcategory_id=OuterRef('id'),
            start_date=first_day,
        )

        # Main query
        subcategory_details = Subcategory.objects.filter(
            category__budget__user=self.request.user,
        ).order_by(
            "category__name",
            "name"
        ).annotate(
            activity=Coalesce(  # Coalesce picks first non-null value
                Sum('transaction__outflow',
                    filter=Q(
                        transaction__receipt_date__range=(first_day, last_day),
                    )
                    ),
                Decimal(0.00),
            )
        ).annotate(
            budgeted_amount=Coalesce(
                Subquery(budgeted_subquery.values("budgeted_amount")),
                Decimal(0.00)
            )
        ).annotate(
            available=Subquery(past_budgeted_subquery) - Coalesce(
                Sum('transaction__outflow',
                    filter=Q(
                        transaction__receipt_date__lte=last_day,
                    )
                    ),
                Decimal(0.00),
            )
        )

        # This is an awful hack, to add information if the element is the first
        # one in its category. If it is, it's marked as True (for the template)
        # then template checks for this value and adds extra row to the table.

        new_list = []
        cache = {}
        for sub in subcategory_details:
            if cache.get(sub.category.name, None):
                new_list.append((sub, False,))
            else:
                cache[sub.category.name] = True
                new_list.append((sub, True,))

        return new_list


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
        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('page-500.html')
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

    # UPDATE SSUBCATEGORY NAME
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
        category = Category(name=value, budget_id=budget.id)
        print(category)
        category.save()

    if type == 'new-subcategory':
        subcategory = Subcategory(name=value, category_id=id)
        subcategory.save()

    if type == 'new-budget':
        subcategory_obj = Subcategory.objects.get(id=id)
        print(subcategory_obj)
        detail = SubcategoryDetails(budgeted_amount=value, start_date=first_day, end_date=last_day,
                                    subcategory=subcategory_obj)
        detail.save()

    return JsonResponse({"success": "Object updated"})


class BudgetView(ListView):
    model = Category
    template_name = 'budget.html'

    def _set_current_date(self):
        if not self.kwargs.get("year", None):
            self.kwargs["year"] = str(datetime.now().year)
        if not self.kwargs.get("month", None):
            self.kwargs["month"] = f"{datetime.now().month:02d}"

    def _this_months_range(self):
        year = int(self.kwargs["year"])
        month = int(self.kwargs["month"])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._set_current_date()
        _, last_day = self._this_months_range()
        context['prev_month'] = prev_month(last_day)
        context['next_month'] = next_month(last_day)
        return context

    def get_queryset(self):

        self._set_current_date()
        first_day, last_day = self._this_months_range()

        return self.model.objects.filter(budget_id=self.request.user.budgets.first().id).order_by('-created_on') \
            .select_related() \
            .prefetch_related(
            Prefetch(
                "subcategories",
                queryset=Subcategory.objects.all()
                    .annotate(
                    activity=Coalesce(
                        Sum('transactions__outflow',
                            filter=Q(
                                transactions__receipt_date__lte=last_day,
                                transactions__receipt_date__gte=first_day,
                            ), distinct=True), Decimal(0.00)),
                    available=
                        Coalesce(Sum('details__budgeted_amount',
                                     filter=Q(
                                         details__end_date__lte=last_day
                                     ), distinct=True), Decimal(0.00))

                        - Coalesce(Sum('transactions__outflow',
                                       filter=Q(
                                           transactions__receipt_date__lte=last_day,
                                       ), distinct=True), Decimal(0.00))
                        )
            ),
            Prefetch(
                "subcategories__details",
                queryset=SubcategoryDetails.objects.filter(start_date__lte=last_day, end_date__gte=first_day)
            ),
        )
