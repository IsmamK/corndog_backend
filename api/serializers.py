from rest_framework import serializers
from .models import *
from datetime import datetime
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class DiscountSerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False, many=True)
    class Meta:
        model = Discount
        exclude = ['users']

    
    
    def create(self, validated_data):
        # Create the discount
        if validated_data.get('amount') is None:
            validated_data['amount'] = 9999999

        validated_data.pop('users', None)

        subcategories = validated_data.pop('subcategories', None)
        discount = super().create(validated_data)
        
        if subcategories:
            discount.subcategories.set(subcategories)

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
        amount = 0
        if cart.discount_code:
            discount = Discount.objects.get(code__iexact=cart.discount_code)
            eligible_cart_items = CartItem.objects.filter(
                    cart=cart,
                    product__sub_category__in=discount.subcategories.all()
                )
            
            print(eligible_cart_items)
            if discount.subcategories.exists():
                if discount.discount_type == "amount":
                            amount = discount.amount
                            print("A",amount)
                else:
                    for cart_item in eligible_cart_items:     
                        amount += (cart_item.product.price*cart_item.quantity)*discount.amount/100
                        
                        
                    
            return amount
        
        else:
            return None


    def get_grandtotal(self, obj):
        cart = obj
        discount = self.get_discount(cart)
        subtotal = self.get_subtotal(cart)

        if discount:
            print(discount)
            return subtotal - discount
            
        else:
            return subtotal


        
class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
  

    class Meta:
        model = Order
        fields = ['id', 'name', 'shipping_address', 'phone_number', 'order_items', 'discount', 'subtotal','grandtotal', 'created_at']

    def create(self, validated_data):
        # Extract order items data if present
        order_items_data = validated_data.pop('order_items', [])

        # Create the order instance
        order = Order.objects.create(**validated_data)

        # Handle order items data if present
        if order_items_data:
            for order_item_data in order_items_data:
                # Fetch the product instance using the product ID
                product_id = order_item_data.get('product')
                try:
                    product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    # Handle the case where the product doesn't exist
                    raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")

                # Calculate the total using the product's price and the quantity
                quantity = order_item_data.get('quantity', 1)  # Default quantity is 1
                total = product.price * quantity

                # Create the OrderItem instance
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                  
                )

        return order
    
   