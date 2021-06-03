from django.core.management.base import BaseCommand
from snaver.models import CustomUser
from snaver.models import Budget
from snaver.models import Category
from snaver.models import Subcategory
from snaver.models import Transaction
from snaver.models import SubcategoryDetails
from django.db import transaction
from django.contrib.auth.hashers import make_password
from random import randint
from datetime import date

from faker import Faker
from calendar import monthrange

USERS = ["Krzysiek", "Mariola", "Andrzej"]
CATEGORIES = ["Rachunki", "Kredyty", "Wydatki na życie",
              "Odkładanie", "Rozrywki"]
SUBCATEGORIES = [
    ["Prąd", "Internet", "Telefon", "Telewizja", "Woda", "Czynsz", "Gaz"],
    ["Kredyt studencki", "Kredyt w baku", "Kredyt hipoteczny", "Samochód"],
    ["Artykuły spożywcze", "Artykuły higieniczne"],
    ["Na remont łazienki", "Na wakacje", "Skarbonka"],
    ["Restauracja", "Kino"]
]


class Command(BaseCommand):
    help = "Command information"

    @transaction.atomic
    def handle(self, *args, **options):

        today = date.today()
        first_day = today.replace(day=1)
        month_end = monthrange(today.year, today.month)[1]
        last_day = today.replace(day=month_end)

        next_first_day = first_day.replace(month=first_day.month+1)
        next_month_end = monthrange(today.year, today.month+1)[1]
        next_last_day = last_day.replace(month=first_day.month+1, day=next_month_end)

        # Initiate faker
        fake = Faker()

        # Delete all users that are not stuff
        CustomUser.objects.filter(is_staff=False).all().delete()

        CustomUser.objects.bulk_create([
            CustomUser(
                username=user,
                email=user.lower() + "@snaver.pl",
                password=make_password('test'),
                is_staff=False,
                is_active=True,
                email_confirmed=True
            ) for user in USERS
        ])

        Budget.objects.bulk_create([
            Budget(
                name="Budżet użytkownika " + user.username,
                user=user,
            ) for user in CustomUser.objects.all()
        ])

        for budget in Budget.objects.all():
            Category.objects.bulk_create([
                Category(
                    name=category,
                    budget=budget,
                ) for category in CATEGORIES
            ])

        for category in Category.objects.all():
            index = CATEGORIES.index(category.name)
            Subcategory.objects.bulk_create([
                Subcategory(
                    name=subcategory,
                    category=category,
                ) for subcategory in SUBCATEGORIES[index]
            ])

        for subcategory in Subcategory.objects.all():
            Transaction.objects.bulk_create([
                Transaction(
                    name="Transakcja",
                    payee_name=fake.company(),
                    amount=100.00,
                    receipt_date=date.today(),
                    subcategory=subcategory,
                ) for _ in range(randint(0, 10))
            ])

            SubcategoryDetails.objects.bulk_create([
                SubcategoryDetails(
                    budgeted_amount=1000.00,
                    start_date=first_day,
                    end_date=last_day,
                    subcategory=subcategory,
                )
            ])

            SubcategoryDetails.objects.bulk_create([
                SubcategoryDetails(
                    budgeted_amount=800.00,
                    start_date=next_first_day,
                    end_date=next_last_day,
                    subcategory=subcategory,
                )
            ])

