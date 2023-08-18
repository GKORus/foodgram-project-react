from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint

User = get_user_model()

# Create your models here.
class Tag(models.Model):
    """Тэги для рецептов.
    Связано с моделью Recipe через М2М."""
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
        verbose_name='Цветовой HEX-код',
        default='#FF0000', #возможный формат
        max_length=7,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Recipe(models.Model):
    """Модель для рецептов.
    Связана с пользователем-автором GourmetUser через O2М.
    Связана с количеством игридиентов IngredientQuantity через O2М.
    Связана с пользователем Tags через M2М.
    Связана с GourmetUser через M2М для добавления в избронное и покупки."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200
    )
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиент',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient') 
    )
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты для рецепта.
    Связана с моделью IngredientQuantity через O2М."""
    name = models.CharField(
        verbose_name='Ингридиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        ordering = ['name'] #убери потом
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class RecipeIngredient(models.Model):
    """Модель для реализации отношения ManyToMany ingredient_id -- recipe_id"""

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
    """Модель избранных рецептов пользователя!!!!!"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
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


# class ShoppingCart(models.Model):
#     """Модель списка покупок пользователя"""
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='shopping_cart',
#         verbose_name='Пользователь',
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         related_name='shopping_cart',
#         verbose_name='Рецепт',
#     )

#     class Meta:
#         verbose_name = 'Покупка'
#         verbose_name_plural = 'Покупки'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=(
#                     'user',
#                     'recipe',
#                 ),
#                 name='unique_shopping_cart'
#             )
#         ]

#     def __str__(self):
#         return f'Рецепт {self.recipe} в списке покупок {self.user}'


class Subscribe(models.Model):
    """Модель подписки на авторов рецептов"""
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.user.username} подписан на {self.author.username}')