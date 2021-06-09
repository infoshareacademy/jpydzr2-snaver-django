import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from snaver.helpers import next_month


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

    def save(self, *args, **kwargs):
        is_new = False
        if not self.pk:  # if Subcategory doesn't exist in the database
            is_new = True

        super(Subcategory, self).save(*args, **kwargs)  # create the object

        if is_new:  # after object is created, create its children
            first_day = datetime.date.today().replace(day=1)
            new_subcat_details = []
            for _ in range(1, 13):
                last_day = next_month(first_day) - datetime.timedelta(days=1)
                new_subcat_details.append(
                    SubcategoryDetails(
                        budgeted_amount=0,
                        start_date=first_day,
                        end_date=last_day,
                        subcategory_id=self.id
                    )
                )

                first_day = next_month(first_day)
            SubcategoryDetails.objects.bulk_create(new_subcat_details)

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
        related_name='subcategory_details',
    )

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            raise ValidationError(_("Start date must be before end date"))
        super(SubcategoryDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.subcategory.name} - {self.start_date}"


class Transaction(models.Model):
    name = models.CharField(_('Transaction name'), max_length=255)

    payee_name = models.CharField(
        _('Payee name'),
        max_length=255,
        blank=True,
        null=True,
    )

    outflow = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        blank=True,
        null=True,
        default=0.00
    )
    inflow = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        blank=True,
        null=True,
        default=0.00
    )

    receipt_date = models.DateField(_('Receipt date'))

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='transaction',
    )

    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"
