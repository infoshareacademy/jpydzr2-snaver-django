from django.shortcuts import render
from django.views.generic import ListView

from snaver.models import Category


class CategoryListView(ListView):
    model = Category
    template_name = "snaver/category_list.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.model.objects.filter(budget__user=self.request.user)
        else:
            return None
