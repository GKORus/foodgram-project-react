import os
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from api.filters import RecipeFilter, IngredientFilter
from api.models import (
    Tag,
    Recipe,
    Ingredient,
    Favorite,
    RecipeIngredient,
    ShoppingCartItem,
    Subscription,
)
from api.serializers import (
    TagSerializer,
    ShortRecipeSerializer,
    RecipeCreateSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    UserWithRecipesSerializer,
)
from api.permissions import IsAuthorOrReadOnlyPermission

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                IsAuthenticated,
                IsAuthorOrReadOnlyPermission
            ]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        os.unlink(instance.image.path)
        instance.delete()

    def add_recipe(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            raise ValidationError('Recipe already exists')
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError('Recipe doesn\'t exist')

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]

    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_recipe(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]

    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCartItem, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_recipe(ShoppingCartItem, request.user, pk)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        output = 'Cписок покупок:\n'
        ingredients = RecipeIngredient.objects.filter(
            recipe__added_to_shopping_cart_by__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            amount_sum=Sum('amount')
        )
        for i in ingredients:
            output += (
                f"- {i['ingredient__name']} "
                f"({i['ingredient__measurement_unit']})"
                f" - {i['amount_sum']}\n"
            )
        return HttpResponse(output, content_type='text/plain', headers={
            'Content-Disposition': 'attachment; filename="shopping_cart.txt"'
        })


class SubscriptionCollectionView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserWithRecipesSerializer

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        author = get_object_or_404(User, pk=id)
        if author == request.user:
            raise ValidationError('Нельзя подписаться на себя')
        if Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            raise ValidationError('Подписка уже существует')
        Subscription.objects.create(user=request.user, author=author)
        serializer = UserWithRecipesSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError('Подписки не существует')


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
