from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CustomUser(AbstractUser):
    name = models.CharField(_('User name'), max_length=255)
    email_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}"


class Budget(models.Model):
    name = models.CharField(
        _('Budget name'),
        max_length=255,
        blank=False,
        validators=[MinLengthValidator(1)],
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='budget',
    )

    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    name = models.CharField(_('Category name'), max_length=255)
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='category',
    )
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"


class Subcategory(models.Model):
    name = models.CharField(_('Subcategory name'), max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategory',
    )
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"


class SubcategoryDetails(models.Model):
    budgeted_amount = models.DecimalField(
        _("Budgeted amount"),
        decimal_places=2,
        max_digits=12)
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='subcategory',
    )

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            raise ValidationError(_("Start date must be before end date"))
        super(SubcategoryDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"


class Transaction(models.Model):
    name = models.CharField(_('Transaction name'), max_length=255)

    payee_name = models.CharField(
        _('Payee name'),
        max_length=255,
        blank=True,
        null=True,
    )

    outflow = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True, default=0.00)
    inflow = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True, default=0.00)

    receipt_date = models.DateField(_('Receipt date'))

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='transaction',
    )

    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"

