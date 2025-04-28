from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductHistoryViewSet, WishListViewSet, AveragePriceAPIView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-history', ProductHistoryViewSet)
router.register(r'wishlists', WishListViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('average-price', AveragePriceAPIView.as_view(), name='average-price'),
]
