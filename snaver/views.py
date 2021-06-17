from datetime import datetime
from decimal import Decimal

from django import template
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils import dateformat
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.views.generic import ListView

from snaver.forms import TransactionCreateForm
from snaver.helpers import next_month
from snaver.helpers import prev_month
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

    success_url = reverse_lazy('adding')
    template_name = 'add-new.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TransactionListView(ListView):
    model = Transaction
    template_name = 'adding-transactions.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None

        transaction_details = {
            'transaction_list': self.model.objects.filter(
                subcategory__category__budget__user=self.request.user),
            'subcategory_list': self.model.objects.filter(
                subcategory__category__budget__user=self.request.user).distinct("subcategory__name")
        }
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
                Sum('subcategory__transaction__outflow',
                    filter=Q(
                        subcategory__transaction__receipt_date__lte=F("end_date"),
                        subcategory__transaction__receipt_date__gte=F("start_date")
                    )
                    ),
                Decimal(0.00),
            )
        ).annotate(
            available=(F("budgeted_amount") - F("activity"))
        )

        # This is an awful hack, to add information if the element is the first
        # one in its category. If it is, it's marked as True (for the template)
        # then template checks for this value and adds extra row to the table.

        new_list = []
        cache = {}
        for sub in subcategory_details:
            if cache.get(sub.subcategory.category.name, None):
                new_list.append((sub, False,))
            else:
                cache[sub.subcategory.category.name] = True
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
def update_category(request):
    print("doszedlem tutaj")
    id = request.POST.get('id', '')
    type = request.POST.get('type', '')
    value = request.POST.get('value', '')
    print(value)

    if type == 'subcategory-name':
        print("ok, tutaj tez jestem")
        subcategory = Subcategory.objects.get(id=id)
        subcategory.name = value
        subcategory.save()

    if type == 'budgeted-amount':
        print("ok, tutaj tez jestem")
        subcategory = SubcategoryDetails.objects.get(id=id)
        subcategory.budgeted_amount = value
        subcategory.save()

    return JsonResponse({"success": "Object updated"})

@csrf_exempt
def update_transaction(request):
    print("1)doszedlem tutaj")
    id = request.POST.get('id', '')
    type = request.POST.get('type', '')
    value = request.POST.get('value', '')

    print("-----------id:")
    print(id)
    print("-----------type:")
    print(type)
    print("-----------value:")
    print(value)
    print("")
    print("")


    if type == 'transaction_date':
        transaction = Transaction.objects.get(id=id)
        transaction.receipt_date = value
        transaction.save()

    if type == 'payee_name':
        transaction = Transaction.objects.get(id=id)
        print("-------transaction:")
        print(transaction)
        transaction.payee_name = value
        print("--------name:")
        print(value)
        transaction.save()

    if type == 'transaction_subcategory':
        print("2)ok, kategoria")
        transaction = Transaction.objects.get(id=id)
        print(transaction)
        print(transaction.id)
        print("-------transaction")

        transaction.subcategory.id = Subcategory.objects.get(id=value)
        transaction.subcategory.name = Subcategory.objects.get(id=value)

        print("--------nazwa kategorii po zmianie:")
        print(transaction.subcategory.name)
        print("----------id kategorii po zmianach:")
        print(transaction.subcategory.id)

        transaction.save()

        print("-----------transakcja")
        print(transaction)

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

