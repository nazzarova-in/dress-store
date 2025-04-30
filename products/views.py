from collections import defaultdict
from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, ProductHistory, WishList
from .serializers import ProductSerializer, ProductHistorySerializer, WishListSerializer, AveragePriceSerializer, SetPriceSerializer
from .overlap_date_period import overlap_date


class ProductViewSet(viewsets.ModelViewSet):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  permission_classes = [IsAuthenticated]


class ProductHistoryViewSet(viewsets.ModelViewSet):
  queryset = ProductHistory.objects.all()
  serializer_class = ProductHistorySerializer
  permission_classes = [IsAuthenticated]

  @action(detail=False,  methods=['post'], url_path='set-price-period', permission_classes=[IsAdminUser])
  def set_price_period(self, request):
    serializer = SetPriceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    product = get_object_or_404(Product, id=data['product_id'])

    for period in ProductHistory.objects.filter(product=product):
      period_start = (period.start_date).date()
      period_end = (period.end_date).date()
      if not overlap_date(data['start_date'], data['end_date'], period_start, period_end):
        raise ValidationError("Period is overlap")

    new_period = ProductHistory.objects.create(
      product=product,
      price=data['price'],
      start_date=data['start_date'],
      end_date=data['end_date'],
    )

    return Response(SetPriceSerializer(new_period).data)


class WishListViewSet(viewsets.ModelViewSet):
  queryset = WishList.objects.all()
  serializer_class = WishListSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return WishList.objects.filter(user=self.request.user)

  def perform_create(self, serializer):
    return serializer.save(user=self.request.user)


class AveragePriceAPIView(APIView):
  permission_classes = [IsAuthenticated]
  def get(self, request):
    serializer = AveragePriceSerializer(data=request.query_params)

    serializer.is_valid(raise_exception=True)
    start_date = serializer.validated_data['start_date']
    end_date = serializer.validated_data['end_date']
    product = serializer.validated_data['product']

    discount_period = ProductHistory.objects.filter(product=product)
    all_dates = defaultdict(float)
    price_for_day = product.current_price
    days_count = (end_date - start_date).days + 1

    for day in range(days_count):
      current_date = start_date + timedelta(days=day)

      for discount in discount_period:
        if discount.is_discount(current_date):
          price_for_day = discount.price
          break

      all_dates[current_date.strftime("%Y-%m-%d")] = float(price_for_day)

    prices = all_dates.values()
    average_price = round(sum(prices) / len(prices))

    return Response({"avg": average_price})
