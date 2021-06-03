import factory.django
from faker import Faker
from snaver.models import CustomUser
from snaver.models import Budget
from snaver.models import Category
from snaver.models import Subcategory
from snaver.models import Transaction
from snaver.models import SubcategoryDetails

faker = Faker()


class CustomUserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CustomUser

    first_name = faker.first_name()
    last_name = faker.last_name()
    username = factory.Sequence(lambda n: "User %03d" % n)
    password = faker.password(
        length=20,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    is_staff = False
    is_superuser = False
    is_active = True
    email_confirmed = True
    name = faker.name()


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    name = faker.word() + " budget"
    user = factory.Iterator(CustomUser.objects.all())
    created_on = faker.date_time()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = faker.word() + " category"
    budget = factory.Iterator(Budget.objects.all())
    created_on = faker.date_time()


class SubcategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subcategory

    name = faker.word() + " subcategory"
    category = factory.Iterator(Category.objects.all())
    created_on = faker.date_time()


class SubcategoryDetailsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubcategoryDetails

    budgeted_amount = 100.00
    start_date = faker.date
    end_date = faker.date

    subcategory = factory.Iterator(Subcategory.objects.all())


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    name = faker.word() + " subcategory"
    payee_name = faker.word()
    amount = 100.00
    receipt_date = faker.date_time()
    subcategory = factory.Iterator(Subcategory.objects.all())
    created_on = faker.date_time()
