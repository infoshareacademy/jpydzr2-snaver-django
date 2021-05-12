from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.template import loader
from django.utils import dateformat
from django.utils import timezone
from django.views.generic import ListView

from snaver.models import Category
from snaver.models import SubcategoryDetails


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


class CategoryListView(ListView):
    model = Category
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
            )
        )

        return subcategory_details
