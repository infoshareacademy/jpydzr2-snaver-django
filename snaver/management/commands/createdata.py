from django.core.management.base import BaseCommand
from faker import Faker
import faker.providers
from snaver.models import CustomUser
from snaver.tests.factories import CustomUserFactory, BudgetFactory
from django.db import transaction

CATEGORIES = ["Rachunki", "Mieszkanie", "Jedzenie"]
SUBCATEGORIES = ["Czynsz", "Kredyt studencki"]

class Command(BaseCommand):
    help = "Command information"

    @transaction.atomic
    def handle(self, *args, **options):

        CustomUser.objects.all().delete()

        users = []
        for num in range(50):
            user = CustomUserFactory()
            users.append(user)
        CustomUser.objects.add(users)
