from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from api.models import Tag, Recipe, Ingredient
from api.serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer

class CastomUserViewSet(UserViewSet):
    pass

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action == 'create': 
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class IngredientViewSet(ModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
