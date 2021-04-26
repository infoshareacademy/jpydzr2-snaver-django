import datetime
from decimal import Decimal

from django.test import TestCase

from snaver.models import Budget
from snaver.models import Category
from snaver.models import MockUser
from snaver.models import Subcategory
from snaver.models import Transaction


class BudgetTestCase(TestCase):

    def setUp(self):
        user = MockUser.objects.create(name="Adam")
        Budget.objects.create(
            name="Home budget",
            user=user,
        )

    def test_budget_has_user(self):
        """Budget that is created has an user attached to it"""
        budget = Budget.objects.get(name="Home budget")
        self.assertEqual(budget.user.name, "Adam")


class CategoryTestCase(TestCase):

    def setUp(self):
        user = MockUser.objects.create(name="Krzysiek")
        budget = Budget.objects.create(
            name="Work budget",
            user=user,
        )
        Category.objects.create(name="Groceries", budget=budget)

    def test_category_has_budget(self):
        category = Category.objects.get(name="Groceries")
        self.assertEqual(category.budget.name, "Work budget")


class SubcategoryTestCase(TestCase):

    def setUp(self):
        user = MockUser.objects.create(name="Mariola")
        budget = Budget.objects.create(
            name="My budget",
            user=user,
        )
        category = Category.objects.create(name="My budget", budget=budget)
        Subcategory.objects.create(name="Cinema", category=category)

    def test_category_has_budget(self):
        subcategory = Subcategory.objects.get(name="Cinema")
        self.assertEqual(subcategory.category.name, "My budget")


class TransactionTestCase(TestCase):
    def setUp(self):
        user = MockUser.objects.create(name="Mariola")
        budget = Budget.objects.create(
            name="My budget",
            user=user,
        )
        category = Category.objects.create(name="My budget", budget=budget)
        subcategory = Subcategory.objects.create(
            name="Cinema",
            category=category
        )
        Transaction.objects.create(
            name="Spiderman",
            payee_name="Cinema city",
            amount=30.00,
            receipt_date=datetime.date(year=2021, month=4, day=26),
            subcategory=subcategory,
        )

    def test_transaction_has_correct_category_name(self):
        transaction = Transaction.objects.get(name="Spiderman")
        self.assertEqual(transaction.subcategory.category.name, "My budget")

    def test_transaction_has_correct_amount(self):
        transaction = Transaction.objects.get(name="Spiderman")
        self.assertEqual(transaction.amount, Decimal(30.00))
