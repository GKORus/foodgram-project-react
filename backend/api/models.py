from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """
    Модель для тегов рецептов.
    """
    name = models.CharField(
        verbose_name='Тэг',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвета HEX-кода',
        default='#008000',
        max_length=7,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    """
    Модель для ингредиентов рецептов.
    """
    name = models.CharField(
        verbose_name='Ингридиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    """
    Модель для рецептов.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_of',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200
    )
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='recipes')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient')
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель для реализации отношения ManyToMany ingredient_id -- recipe_id
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=0,
    )

    class Meta:
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredient_recipe')
        ]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    """
    Модель избранных рецептов пользователя
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном у {self.user}"


class ShoppingCartItem(models.Model):
    """
    Модель списка покупок пользователя
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='added_to_shopping_cart_by',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='unique_shopping_cart_item'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок {self.user}'


class Subscription(models.Model):
    """
    Модель подписки на авторов рецептов
    """
    user = models.ForeignKey(
        User,
        related_name='subscriptions',
        verbose_name='Подписки',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='followers',
        verbose_name='Подписчики',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.user.username} подписан на {self.author.username}')
