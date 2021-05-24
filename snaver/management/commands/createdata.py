from django.core.management.base import BaseCommand
from snaver.models import CustomUser, Budget, Category, Subcategory, Transaction, SubcategoryDetails
from django.db import transaction
from django.contrib.auth.hashers import make_password
from random import randint
from datetime import date

from faker import Faker


USERS = ["Krzysiek", "Mariola", "Andrzej"]
CATEGORIES = ["Rachunki", "Kredyty", "Wydatki na życie", "Odkładanie", "Rozrywki"]
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

        # Initiate faker
        fake = Faker()

        # Delete all users that ate not stuff
        CustomUser.objects.filter(is_staff=False).all().delete()

        CustomUser.objects.bulk_create([
            CustomUser(
                username=user,
                email=user.lower() + "@snaver.pl",
                password=make_password('test'),
                is_staff=False,
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
            print(index)
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
                    start_date=date.today(),
                    end_date=date.today(),
                    subcategory=subcategory,
                )
            ])