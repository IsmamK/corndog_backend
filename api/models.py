from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2,max_digits=6)
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return f"{self.id} {self.title} (Price = {self.price})"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
        return f"{self.quantity} x {self.product.title} in {self.cart}"
