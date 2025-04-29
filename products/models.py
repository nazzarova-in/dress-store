from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
  name = models.CharField(max_length=100)
  article = models.CharField(max_length=50, unique=True)
  current_price = models.DecimalField(max_digits=10, decimal_places=2)
  description = models.TextField()

  def __str__(self):
    return f"{self.name}: ({self.article})"

  def save(self, *args, **kwargs):
    try:
      old_price = Product.objects.get(pk=self.pk)
    except Product.DoesNotExist:
      raise
    else:
      if old_price.current_price != self.current_price:
        ProductHistory.objects.create(
          product = self,
          price = old_price.current_price,
          start_date = timezone.now()
        )

    super().save(*args, **kwargs)

  def wished_user_count(self):
    return User.objects.filter(wishlists__products=self).distinct().count()


class ProductHistory(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  start_date = models.DateTimeField()
  end_date = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return f"{self.product}: {self.price} € -  c {self.start_date} до {self.end_date}"

  def is_discount(self, current_date):
    return self.start_date.date() <= current_date <= self.end_date.date()


class WishList(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
  name = models.CharField(max_length=100)
  products = models.ManyToManyField(Product, related_name="wishlists")
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.name}  ({self.user.username})"
