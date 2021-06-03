from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.template import loader
from django.utils import dateformat
from django.utils import timezone
from django.views.generic import ListView
from django import template

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

    def get_queryset(self, *args, **kwargs):
        selected_date = dateformat.format(
            datetime(
                year=int(self.kwargs["year"]),
                month=int(self.kwargs["month"]),
                day=1
            ),
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
