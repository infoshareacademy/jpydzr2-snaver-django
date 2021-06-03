from datetime import datetime
from decimal import Decimal

from django import template
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.template import loader
from django.utils import dateformat
from django.utils import timezone
from django.views.generic import ListView

from snaver.helpers import next_month
from snaver.helpers import prev_month
from snaver.models import SubcategoryDetails


@login_required
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


class CategoryListView(ListView):
    template_name = "ui-tables.html"

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
                Sum('subcategory__transaction__amount'),
                Decimal(0.00)
            ),
            available=(
                    F("budgeted_amount")
                    - Sum('subcategory__transaction__amount')
            )
        )

        return subcategory_details


class CategoryView(ListView):
    template_name = "budget.html"

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
                Sum('subcategory__transaction__amount'),
                Decimal(0.00)
            ),
            available=(
                    F("budgeted_amount")
                    - Sum('subcategory__transaction__amount')
            )
        )

        return subcategory_details


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
                Sum('subcategory__transaction__amount'),
                Decimal(0.00)
            ),
            available=(
                    F("budgeted_amount")
                    - Sum('subcategory__transaction__amount')
            )
        )

        total_expenses = (
            SubcategoryDetails.objects.filter(
                subcategory__category__budget__user=self.request.user,
                start_date__lte=current_time,
                end_date__gte=current_time,
            ).aggregate(Sum('subcategory__transaction__amount'))
        )

        total_budgeted = (
            SubcategoryDetails.objects.filter(
                subcategory__category__budget__user=self.request.user,
                start_date__lte=current_time,
                end_date__gte=current_time,
            ).aggregate(Sum('budgeted_amount'))
        )

        return subcategory_details, total_expenses['subcategory__transaction__amount__sum'], total_budgeted[
            "budgeted_amount__sum"]


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

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
