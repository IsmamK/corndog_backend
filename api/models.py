from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model
import sys
# Create your models here.

User = get_user_model()
class Category(models.Model):
    name = models.CharField(max_length = 255)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField()
    def __str__(self):
        return f"{self.id} : {self.name}"

class SubCategory(models.Model):
    name = models.CharField(max_length = 255)
    parent_category = models.ForeignKey(Category,on_delete = models.CASCADE , related_name = "subcategories")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField()
    def __str__(self):
        return f"{self.id} : {self.name}"
    
class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    description = models.TextField()
    image = models.ImageField()
    sub_category = models.ForeignKey(SubCategory,on_delete = models.CASCADE,related_name = "products")
    created_at = models.DateTimeField(auto_now_add=True)  # Added created_at field with auto_now_add
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.title} (Price = {self.price})"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,related_name = "cart")
    created_at = models.DateTimeField(auto_now_add=True)
    discount_code = models.CharField(max_length=50, blank=True, null=True)  # Optional discount code field

    def __str__(self):
        if self.user != None:
           return f"Cart for {self.user.username }"
        else:
            return f"Anonymous Cart Id: {self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name = "cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name = "cart_item")
    quantity = models.PositiveIntegerField(default=1)
   
    def __str__(self):
        return self.product.title



class Order(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.CharField(max_length=512)
    phone_number = models.CharField(max_length=20)  
    discount = models.DecimalField(decimal_places=2,max_digits=20)
    subtotal =models.DecimalField(decimal_places=2,max_digits=20)
    grandtotal = models.DecimalField(decimal_places=2,max_digits=20)
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')


    def __str__(self):
        return f"Order Id: {self.id} , Customer: {self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name = "order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name = "order_item")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

#coded discount
class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(choices=[('percentage', 'Percentage'), ('amount', 'Fixed Amount')], max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    max_usage = models.PositiveIntegerField(default=9999999)
    users = models.ManyToManyField(User, through='DiscountUsage')  # Many-to-Many relationship with User model
    subcategories = models.ManyToManyField(SubCategory, blank=True)  # Many-to-Many relationship with SubCategory model
    def __str__(self):
        return self.code


class DiscountUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE,related_name = "usage")
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.discount.code} - Usage Count: {self.usage_count}"
