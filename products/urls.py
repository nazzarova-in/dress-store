from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductHistoryViewSet, WishListViewSet, AveragePriceAPIView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product-history', ProductHistoryViewSet, basename='product-history')
router.register(r'wishlists', WishListViewSet, basename='wishlists')

urlpatterns = [
    path('', include(router.urls)),
    path('average-price', AveragePriceAPIView.as_view(), name='average-price'),
]
