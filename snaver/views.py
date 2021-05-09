from django.utils import timezone
from django.views.generic import ListView

from snaver.models import Category
from snaver.models import SubcategoryDetails


class CategoryListView(ListView):
    model = Category
    template_name = "ui-tables.html"

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None

        detailed_list = []
        current_time = timezone.now
        categories = self.model.objects.filter(budget__user=self.request.user)
        for subcategory in categories:
            details = SubcategoryDetails.objects.filter(
                subcategory=subcategory,
                start_date__gte=current_time,  # TODO: str do porównania daty
                end_date__lte=current_time,
            )
            # TODO: Create object that can hold detailed info
            detailed_list.append(details)
        return detailed_list
