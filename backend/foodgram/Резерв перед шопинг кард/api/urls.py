from rest_framework.routers import DefaultRouter
from django.urls import include, path
from api.views import CastomUserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet

router = DefaultRouter()
router.register('users', CastomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = (
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
)