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

from snaver.models import SubcategoryDetails, Budget


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

        x = 10

        return subcategory_details, total_expenses['subcategory__transaction__amount__sum'], total_budgeted["budgeted_amount__sum"], x