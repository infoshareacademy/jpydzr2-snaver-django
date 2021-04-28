from django.contrib import admin

from snaver.models import Budget
from snaver.models import Category
from snaver.models import MockUser
from snaver.models import Subcategory
from snaver.models import Transaction


@admin.register(MockUser)
class MockUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
