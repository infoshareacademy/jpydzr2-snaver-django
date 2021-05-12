from django.utils import timezone, dateformat
from django.views.generic import ListView

from snaver.models import Category
from snaver.models import SubcategoryDetails
from django.db.models import Sum
from django.http import HttpResponse
from django.template import loader


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
        ).annotate(activity=Sum('subcategory__transaction__amount'))

        return subcategory_details
