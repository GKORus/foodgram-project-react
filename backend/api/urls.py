from rest_framework.routers import DefaultRouter
from django.urls import include, path
from api.views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    SubscriptionView,
    SubscriptionCollectionView,
)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = (
    path('users/subscriptions/', SubscriptionCollectionView.as_view()),
    path('users/<int:id>/subscribe/', SubscriptionView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
)
