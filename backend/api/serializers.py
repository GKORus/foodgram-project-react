from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from api.models import Tag, Recipe, RecipeIngredient, Ingredient

User = get_user_model()


BASE_USER_FIELDS = [
    'id', 'email', 'username', 'first_name', 'last_name'
]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для предоставления данных о пользователе"""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = BASE_USER_FIELDS + ['is_subscribed']

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Выберете другой логин")
        return value

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания нового пользователя"""
    class Meta:
        model = User
        fields = BASE_USER_FIELDS + ['password']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для представления данных о тегах"""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для предоставления информации об ингредиентах"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для связи между ингредиентом и рецептом (amount)"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиента, связанного с рецептом"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для предоставления данных о рецепте для GET-запроса"""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'image',
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'author',
            'is_in_shopping_cart',
            'is_favorited'
        ]

    def get_ingredients(self, instance):
        return RecipeIngredientSerializer(
            instance.recipeingredient_set.all(),
            many=True
        ).data

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения данных о рецепте"""
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, allow_empty=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'image',
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'author'
        ]

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
        self.add_ingredients(ingredients, recipe)
        self.add_tags(tags, recipe)
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
    """Сериализатор для рецептов (сокращённая форма)"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserWithRecipesSerializer(UserSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = BASE_USER_FIELDS + [
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_recipes(self, obj):
        qs = obj.author_of.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
            )
        if recipes_limit:
            qs = qs[:int(recipes_limit)]
        return ShortRecipeSerializer(qs, many=True) .data

    def get_recipes_count(self, obj):
        return obj.author_of.count()
