from datetime import datetime, date
from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products import overlap_date_period
from products.models import Product, ProductHistory, WishList
from products.overlap_date_period import overlap_date
from products.serializers import ProductSerializer, ProductHistorySerializer, SetPriceSerializer


class ProductApiTestCase(APITestCase):
  def setUp(self):
    self.user = User.objects.create_superuser(username='user', password='11111')
    url = reverse('token_obtain_pair')
    response = self.client.post(url, {'username': 'user', 'password':'11111'})
    self.assertEqual(response.status_code, 200)
    self.token = response.data['access']
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

  def test_get_product(self):
    product1 = Product.objects.create(name = 'Cap', article = 'as-111', current_price=45.00, description='Cool!')
    product2 = Product.objects.create(name = 'Cap2', article = 'as-222', current_price=55.00, description='Cool!')
    url = reverse('products-list')
    response = self.client.get(url)
    serializer_data = ProductSerializer([product1, product2], many=True).data
    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(serializer_data, response.data)

  def test_get_product_history(self):
    product3 = Product.objects.create(name='Cap', article='as-333', current_price=45.00, description='Cool!')
    product_history1 = ProductHistory.objects.create(
      product=product3,
      price=30,
      start_date=datetime(2025,5,1,0,0),
      end_date=datetime(2025,5,7,0,0)
    )
    url = reverse('product-history-list')
    response = self.client.get(url)
    serializer_data = ProductHistorySerializer([product_history1], many=True).data
    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(serializer_data, response.data)

  def test_create_wishlist(self):
    product5 = Product.objects.create(name='Cap', article='as-555', current_price=45.00, description='Cool!')
    product6 = Product.objects.create(name='Cap2', article='as-666', current_price=55.00, description='Cool!')
    user1 = User.objects.create(username="user1", password='11111')
    data = {
      "user": user1.id,
      "name": "wishlist1",
      "products": [product5.id, product6.id]
    }

    url = reverse('wishlists-list')
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

  def test_get_wishlist(self):
    user5 = User.objects.create(username="user5", password='55555')
    product10 = Product.objects.create(name='Cap', article='as-10', current_price=45.00, description='Cool!')
    product11 = Product.objects.create(name='Cap2', article='as-11', current_price=55.00, description='Cool!')
    wishlist3 = WishList.objects.create(name='favorite', user = user5)
    wishlist3.products.set([product10, product11])


    self.client.force_login(user5)
    url = reverse('wishlists-list')
    response = self.client.get(url)
    self.assertEqual(status.HTTP_200_OK, response.status_code)


  def test_set_price_period(self):
    product7 = Product.objects.create(name='Cap', article='as-777', current_price=45.00, description='Cool!')
    url = reverse('product-history-set-price-period')

    ProductHistory.objects.create(
      product=product7,
      price=80,
      start_date=date(2025, 6, 5),
      end_date=date(2025, 6, 10)
    )

    data = {
      'product_id' : product7.id,
      'price': 70,
      'start_date': "2025-07-05",
      'end_date': "2025-07-20",

    }
    response = self.client.post(url, data)
    self.assertEqual(status.HTTP_200_OK, response.status_code)

  def test_overlap_price_period(self):
    product8 = Product.objects.create(name='Cap', article='as-888', current_price=45.00, description='Cool!')
    url = reverse('product-history-set-price-period')

    ProductHistory.objects.create(
      product=product8,
      price=80,
      start_date=date(2025, 6, 5),
      end_date=date(2025, 6, 10)
    )

    data = {
      'product_id': product8.id,
      'price': 70,
      'start_date': "2025-06-05",
      'end_date': "2025-06-20",

    }
    response = self.client.post(url, data)
    self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


  def test_average_price(self):
    product8 = Product.objects.create(name='Cap', article='as-888', current_price=100, description='Cool!')

    ProductHistory.objects.create(
      product=product8,
      price=80,
      start_date=date(2025, 5, 5),
      end_date=date(2025, 5, 10)
    )

    url = reverse('average-price')
    params = {
      'product': product8.id,
      'start_date': '2025-05-01',
      'end_date': '2025-05-10'
    }

    response = self.client.get(url, params)
    self.assertEqual(response.status_code, 200)
    self.assertIn('avg', response.data)
    expected_avg = round((100 * 4 + 80 * 6) / 10)
    self.assertEqual(response.data['avg'], expected_avg)

class ProductSerializerTestCase(TestCase):
  def test_serializer(self):
    product1 = Product.objects.create(name='Cap', article='as-11', current_price=45, description='Cool!')
    product1.wished_user_count = lambda: 3
    data = ProductSerializer([product1], many=True).data
    expected_data = [
      {
        "id": product1.id,
        "unique_users_count": 3,
        "name": "Cap",
        "article": "as-11",
        "current_price": "45.00",
        "description": "Cool!"

      }
    ]
    self.assertEqual(expected_data, data)


class SetPriceSerializerTestCase(TestCase):
  def test_valid_date(self):
    data = {
      'product_id': 1,
      'price': 100.00,
      'start_date': date(2025, 7, 20),
      'end_date': date(2025, 7, 10),
    }

    serializer = SetPriceSerializer(data=data)
    self.assertFalse(serializer.is_valid())
    self.assertIn("Start_date can't be more end_date!", str(serializer.errors))

