from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from rest_framework import status, viewsets

from api.models import Tag, Recipe, Ingredient
from api.serializers import TagSerializer, ShortRecipeSerializer, RecipeCreateSerializer, IngredientSerializer, RecipeReadSerializer

class CastomUserViewSet(UserViewSet):
    pass

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

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
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()

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

class IngredientViewSet(ModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


