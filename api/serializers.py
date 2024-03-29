from rest_framework import serializers
from .models import *
from datetime import datetime
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        exclude = ['users']

    
    
    def create(self, validated_data):
        # Create the discount
        if validated_data.get('amount') is None:
            validated_data['amount'] = 9999999

        validated_data.pop('users', None)
        discount = super().create(validated_data)
        

        return discount
    
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True, required=True)
    cart_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'cart_id', 'quantity']
    
    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        cart_id = validated_data.pop('cart_id')

        product = Product.objects.get(pk=product_id)
        cart = Cart.objects.get(pk=cart_id)

        quantity = validated_data.pop('quantity', 1)  # Default quantity is 1

        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart, defaults={'quantity': quantity})

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    
class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    grandtotal = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'created_at',"subtotal","discount_code","discount","grandtotal"]

    def get_cart_items(self, obj):
        cart_items = CartItem.objects.filter(cart=obj)
        cart_item_details = []
        for cart_item in cart_items:
            product_details = {
                'id': cart_item.product.id,
                'title': cart_item.product.title,
                'price': cart_item.product.price,
                
            }
            detailed_cart_item = {
                'cart_item_id': cart_item.id,
                'product': product_details,
                'quantity': cart_item.quantity,
                'total' : cart_item.product.price*cart_item.quantity
            }
            cart_item_details.append(detailed_cart_item)

        return cart_item_details

    def get_subtotal(self, obj):
        cart_items = CartItem.objects.filter(cart=obj)
        subtotal = 0 
        for cart_item in cart_items:
            subtotal += cart_item.product.price*cart_item.quantity
        return subtotal
    def get_discount(self,obj):
        cart = obj 
        if cart.discount_code:
            discount = Discount.objects.get(code__iexact=cart.discount_code)
            discount_serializer = DiscountSerializer(discount)  # Serialize the discount object
            return discount_serializer.data  # Return serialized discount object
        else:
            return None


    def get_grandtotal(self, obj):
        cart = obj
        discount = self.get_discount(cart)
        subtotal = self.get_subtotal(cart)

        if discount:
            if discount.get('discount_type') == "amount":
                return subtotal - Decimal(discount.get('amount'))
            else:
                amount = Decimal(subtotal) * Decimal(discount.get('amount')) / 100
                return subtotal - amount
        else:
            return subtotal

        


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity']
    
class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    grandtotal = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user','created_at',"shipping_address","phone_number", 'order_items',"grandtotal"]

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        order_item_details = []
        for order_item in order_items:
            product_details = {
                'id': order_item.product.id,
                'title': order_item.product.title,
                'price': order_item.product.price,
                
            }
            detailed_order_item = {
                'order_item_id': order_item.id,
                'product': product_details,
                'quantity': order_item.quantity,
                'subtotal' : order_item.product.price*order_item.quantity
            }
            order_item_details.append(detailed_order_item)

        return order_item_details

    def get_grandtotal(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        grandtotal = 0 
        for order_item in order_items:
            grandtotal += order_item.product.price*order_item.quantity
        return grandtotal


