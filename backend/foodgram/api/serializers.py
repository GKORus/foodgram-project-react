from api.models import Tag, Recipe, RecipeIngredient, Ingredient
from rest_framework import serializers

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов"""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, instance):
        return RecipeIngredientSerializer(
            instance.recipeingredient_set.all(),
            many=True
        ).data


# class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient',
#         queryset=Ingredient.objects.all()
#     )
 
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount')

class RecipeCreateSerializer(serializers.ModelSerializer):
    #ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'tags') #'ingredients')

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',