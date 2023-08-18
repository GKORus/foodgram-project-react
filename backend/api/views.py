from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db.models import Sum

from api.models import Tag, Recipe, Ingredient, Favorite, RecipeIngredient
from api.serializers import TagSerializer, ShortRecipeSerializer, RecipeCreateSerializer, IngredientSerializer, RecipeReadSerializer, UserSerializer

User = get_user_model()


class CastomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
#    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer

    def get_serializer_class(self):
        if self.action == 'create': 
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов!!!!!!!!!!!"""
    queryset = Recipe.objects.all()
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def add_recipe(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response('Этот рецпт уже есть',
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Такого рецепта уже нет',
                        status=status.HTTP_400_BAD_REQUEST)

    # def shopping_cart(self, request, pk):
    #     if request.method == 'POST':
    #         return self.add_recipe(ShoppingCart, request.user, pk)
    #     return self.delete_recipe(ShoppingCart, request.user, pk)

    # @action(
    #     detail=False,
    #     methods=['GET'],
    #     url_path='download_shopping_cart',
    # )
    # def download_shopping_cart(self, request):
    #     ingredient_list = 'Cписок покупок:'
    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__shopping_cart__user=request.user
    #     ).values(
    #         'ingredient__name', 'ingredient__measurement_unit'
    #     ).annotate(amount_sum=Sum('amount'))
    #     for num, i in enumerate(ingredients):
    #         ingredient_list += (
    #             f"\n{i['ingredient__name']} - "
    #             f"{i['amount_sum']} {i['ingredient__measurement_unit']}"
    #         )
    #         if num < ingredients.count() - 1:
    #             ingredient_list += ', '
    #     file = 'shopping_list'
    #     response = HttpResponse(
    #         ingredient_list, 'Content-Type: application/pdf'
    #     )
    #     response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    #     return response

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    # )
    # def favorite(self, request, pk):
    #     if request.method == 'POST':
    #         return self.add_recipe(Favorite, request.user, pk)
    #     return self.delete_recipe(Favorite, request.user, pk)


class IngredientViewSet(ModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
#    pagination_class = None
