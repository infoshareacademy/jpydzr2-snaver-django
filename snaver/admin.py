from django.contrib import admin

from snaver.models import Category, MockUser, Budget, Subcategory, Transaction


@admin.register(MockUser)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Budget)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Subcategory)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class CategoryAdmin(admin.ModelAdmin):
    pass
