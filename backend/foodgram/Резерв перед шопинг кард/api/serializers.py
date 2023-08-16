from api.models import Tag, Recipe, RecipeIngredient, Ingredient
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from djoser.serializers import UserCreateSerializer, UserSerializer
import base64
from django.core.files.base import ContentFile

User = get_user_model()


# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')  
#             ext = format.split('/')[-1]  
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#         return super().to_internal_value(data)


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


class IngredientSerializer(serializers.ModelSerializer): #работает
    """Сериализатор для ингредиентов!!!!!!"""
    class Meta:
        model = Ingredient
        fields = '__all__' #('name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer): #работает
    """Сериализатор для связывания ингредиента с рецептом для записи!!!!!!!""" 
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
    author = UserSerializer(read_only=True)    
    ingredients = serializers.SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField(read_only=True)
#    image = Base64ImageField()
#    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', #'image',
            'ingredients', 'name',
            'text', 'cooking_time', 'author',
            'is_in_shopping_cart' #'is_favorited'
        ]

    def get_ingredients(self, instance):
        return RecipeIngredientSerializer(
            instance.recipeingredient_set.all(),
            many=True
        ).data

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()    

    # def get_is_favorited(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return user.favorites.filter(recipe=obj).exists()

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/удаления рецептов"""
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientAmountSerializer(many=True)
#    image = Base64ImageField()
    
    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients', 'name',
                  'text', 'cooking_time', 'author'] #, 'image'

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('Тег не выбран! Выберите тэг.',
                code=status.HTTP_400_BAD_REQUEST,
            )
        validated_tags = set()
        for tag in tags:
            validated_tags.add(tag)
        return validated_tags

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise ValidationError(
                'Ингредиент не выбран! Выберите ингредиент.',
                code=status.HTTP_400_BAD_REQUEST,
            )
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise ValidationError(
                    'Такой ингредиент уже был - повторение',
                    code=status.HTTP_400_BAD_REQUEST
                )
            ingredients_list.append(ingredient['id'])
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

    # def get_is_favorited(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return user.favorites.filter(recipe=obj).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в сокращённой форме"""
#    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
#            'image',
            'cooking_time'
        )


#перепиши как в пачке, а то криво
FIELDS = (
    'email',
    'id',
    'username',
    'first_name',
    'last_name',
#    'is_subscribed'
)


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя!!!!"""
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class UserSerializer(UserSerializer):
    """Сериализатор для пользователя"""
    #is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = FIELDS

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Выберете другой логин")
        return value