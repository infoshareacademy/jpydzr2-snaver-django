from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class MockUser(models.Model):
    name = models.CharField(_('User name'), max_length=255)


class Budget(models.Model):
    name = models.CharField(
        _('Budget name'),
        max_length=255,
        blank=False,
        validators=[MinLengthValidator(1)],
    )
    user = models.ForeignKey(
        MockUser,
        on_delete=models.CASCADE,
        related_name='budget_user',
    )

    created_on = models.DateTimeField(default=timezone.now)


class Category(models.Model):
    name = models.CharField(_('Category name'), max_length=255)
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='category_budget',
    )
    created_on = models.DateTimeField(default=timezone.now)


class Subcategory(models.Model):
    name = models.CharField(_('Subcategory name'), max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategory_category',
    )
    created_on = models.DateTimeField(default=timezone.now)


class Transaction(models.Model):
    name = models.CharField(_('Transaction name'), max_length=255)

    payee_name = models.CharField(
        _('Payee name'),
        max_length=255,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(decimal_places=2, max_digits=11)
    receipt_date = models.DateField(_('Receipt date'))

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='transaction_subcategory',
    )

    created_on = models.DateTimeField(default=timezone.now)
