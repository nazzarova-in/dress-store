from django.contrib import admin
from .models import Product,ProductHistory, WishList

admin.site.register(Product)
admin.site.register(ProductHistory)
admin.site.register(WishList)
