from rest_framework import serializers
from .models import Product, ProductHistory, WishList


class ProductSerializer(serializers.ModelSerializer):
  unique_users_count = serializers.SerializerMethodField()

  class Meta:
    model = Product
    fields = "__all__"

  def get_unique_users_count(self, obj):
    return obj.wished_user_count()


class ProductHistorySerializer(serializers.ModelSerializer):
  class Meta:
    model = ProductHistory
    fields = "__all__"


class WishListSerializer(serializers.ModelSerializer):
  products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

  class Meta:
    model = WishList
    fields = "__all__"


class AveragePriceSerializer(serializers.Serializer):
  product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
  start_date = serializers.DateField()
  end_date = serializers.DateField()
