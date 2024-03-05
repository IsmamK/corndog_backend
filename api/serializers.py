from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True, required=True)
    cart_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'cart_id', 'quantity']
    
    def create(self,validated_data):
        product_id = self.validated_data.pop("product_id")
        cart_id = validated_data.pop('cart_id')

        product = Product.objects.get(pk=product_id)
        cart = Cart.objects.get(pk=cart_id)

        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart, defaults=validated_data)

        if not created:
            cart_item.quantity += validated_data.get('quantity', 1)
            cart_item.save()

        return cart_item
    
class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'created_at']

    def get_cart_items(self, obj):
        cart_items = CartItem.objects.filter(cart=obj)
        cart_item_details = []
        for cart_item in cart_items:
            product_details = {
                'id': cart_item.product.id,
                'title': cart_item.product.title,
                'price': cart_item.product.price,
                # Add other fields as needed
            }
            detailed_cart_item = {
                'cart_item_id': cart_item.id,
                'product': product_details,
                'quantity': cart_item.quantity,
            }
            cart_item_details.append(detailed_cart_item)

        return cart_item_details

 


    
