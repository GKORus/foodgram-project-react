from api.models import Tag, Recipe, RecipeIngredient, Ingredient
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов"""
    class Meta:
        model = Tag
        fields = '__all__'


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

class IngredientSerializer(serializers.ModelSerializer): #работает
    #"""Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__' #('name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer): #работает
    #"""Сериализатор для связывания ингредиента с рецептом для записи""" 
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

class RecipeIngredientSerializer(serializers.ModelSerializer): #работает
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзатор для GET-запроса"""
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags',
            'ingredients', 'name',
            'text', 'cooking_time'
        ]

    def get_ingredients(self, instance):
        return RecipeIngredientSerializer(
            instance.recipeingredient_set.all(),
            many=True
        ).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientAmountSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients', 'name',
                  'text', 'cooking_time']

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('Отсутствие тега')
        validated_tags = set()
        for tag in tags:
            validated_tags.add(tag)
        return validated_tags

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise ValidationError(
                'Требуется выбрать хотя бы один ингредиент!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        know_ingredients = []
        for ingredient in ingredients:
            if ingredient['id'] in know_ingredients:
                raise ValidationError(
                    'Ингредиенты повторяются',
                    code=status.HTTP_400_BAD_REQUEST
                )
            know_ingredients.append(ingredient['id'])
        return data


    def add_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients]
        )

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.add_ingredients(recipe=instance,
                             ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, recipe):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(recipe,
                                    context=context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в сокращённой форме"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )