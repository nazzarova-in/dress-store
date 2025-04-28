from collections import defaultdict
from datetime import timedelta
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, ProductHistory, WishList
from .serializers import ProductSerializer, ProductHistorySerializer, WishListSerializer, AveragePriceSerializer


class ProductViewSet(viewsets.ModelViewSet):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer


class ProductHistoryViewSet(viewsets.ModelViewSet):
  queryset = ProductHistory.objects.all()
  serializer_class = ProductHistorySerializer


class WishListViewSet(viewsets.ModelViewSet):
  queryset = WishList.objects.all()
  serializer_class = WishListSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return WishList.objects.filter(user=self.request.user)

  def perform_create(self, serializer):
    return serializer.save(user=self.request.user)


class AveragePriceAPIView(APIView):
  def get(self, request):
    serializer = AveragePriceSerializer(data=request.query_params)

    serializer.is_valid(raise_exception=True)
    start_date = serializer.validated_data['start_date']
    end_date = serializer.validated_data['end_date']
    product = serializer.validated_data['product']

    discount_period = list(ProductHistory.objects.filter(product=product))
    all_dates = defaultdict(float)
    price_for_day = product.current_price
    days_count = (end_date - start_date).days + 1

    for day in range(days_count):
      current_date = start_date + timedelta(days=day)

      for discount in discount_period:
        if discount.start_date.date() <= current_date <= discount.end_date.date():
          price_for_day = discount.price
          break

      all_dates[current_date.strftime("%Y-%m-%d")] = float(price_for_day)

    prices = all_dates.values()
    average_price = round(sum(prices) / len(prices))

    return Response(f' Средняя цена: {average_price}')
