from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from api.models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Subscription,
    ShoppingCartItem,
    Favorite,
)


class RecipeIngredient(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredient, )


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource


admin.site.register(Ingredient, IngredientAdmin)


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCartItem)
class ShoppingCartItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass
