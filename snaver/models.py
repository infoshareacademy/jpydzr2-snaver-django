from django.db import models
import datetime


# Create your models here.


class Transaction(models.Model):
	name = models.CharField('Nazwa transakcji', max_length=255)
	payee_name = models.CharField('Nazwa sklepu', max_length=255)
	amount_inflow = models.DecimalField(decimal_places=2, max_digits=5)
	amount_outflow = models.DecimalField(decimal_places=2, max_digits=5)
	created_date = models.DateField('Data utworzenia', default=datetime.datetime.utcnow)
	receipt_date = models.DateField('Data transakcji')


class CategoryBudget(models.Model):
	__budgeted_amount = models.DecimalField("budgeted_amount", decimal_places=2, max_digits=5)
	datetime = models.DateField('Data')


class Category(models.Model):
	name = models.CharField('Nazwa kategorii', max_length=255)
	transactions = models.ForeignKey(
		Transaction,
		on_delete=models.CASCADE,
		related_name='transaction_category'
	)
	budgeted_amounts = models.ForeignKey(
		CategoryBudget,
		on_delete=models.CASCADE,
		related_name='category_budget'
	)


class ParentCategory(models.Model):
	name = models.CharField('Nazwa kategorii głównej', max_length=255)
	categories = models.ForeignKey(
		Category,
		on_delete=models.CASCADE,
		related_name='parent_category'
	)


class Budget(models.Model):
	name = models.CharField('Nazwa budżetu', max_length=255)
	parent_categories = models.ForeignKey(
		ParentCategory,
		on_delete=models.CASCADE,
		related_name='budget',
	)


class User(models.Model):
	name = models.CharField('Imię', max_length=255)
	# salt = ? #Column(LargeBinary)
	# key = ? #Column(LargeBinary)
	budgets = models.ForeignKey(
		Budget,
		on_delete=models.CASCADE,
		related_name='user_budget'
	)
