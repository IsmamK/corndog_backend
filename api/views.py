from django.shortcuts import render
from .models import * 
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework import filters
from djoser.serializers import UserSerializer
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend 
 # Correct import statement
# --------------------------------------- Categories ---------------------------------------

local_datetime = timezone.localtime(timezone.now()).date()

class ShowCategories(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]
    filterset_fields = ["is_active"]
    search_fields = ['name']
    ordering_fields = ['priority']
  

# --------------------------------------- SubCategories ---------------------------------------

class ShowSubCategories(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]
    filterset_fields = ["is_active","parent_category"]
    search_fields = ['name']
    ordering_fields = ['priority']  

# --------------------------------------- Products ---------------------------------------

class AllProducts(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]
    search_fields = ['title']  
    ordering_fields = ['price', 'created_at','is_active']


class SingleProduct(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# --------------------------------------- CART ---------------------------------------

class ViewCart(generics.ListAPIView):
    serializer_class = CartSerializer  

    def get_queryset(self):
        session_cart_id = self.request.session.get('cart_id')

        if session_cart_id:
            try:
                existing_cart = Cart.objects.get(id=session_cart_id)
                return [existing_cart]
            except Cart.DoesNotExist:
                pass

        new_cart = Cart.objects.create(user=None)
        self.request.session['cart_id'] = new_cart.id

        session_timeout = timedelta(seconds=settings.SESSION_COOKIE_AGE)
        self.request.session.set_expiry(timezone.now() + session_timeout)
        
        return [new_cart]
        

class AddToCart(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()

class DeleteCart(generics.DestroyAPIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

class DeleteCartItem(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()

# --------------------------------------- Discount ---------------------------------------

class ApplyDiscountCode(generics.CreateAPIView, ViewCart):

    def post(self, request):
        discount_code = request.data.get("discount_code")
      
        if not discount_code:
            return Response("Discount code is required", status=status.HTTP_400_BAD_REQUEST)

        try:
            discount = Discount.objects.get(code__iexact=discount_code)
        except Discount.DoesNotExist:
            return Response("Invalid discount code", status=status.HTTP_400_BAD_REQUEST)

        if local_datetime <= discount.valid_to and local_datetime >= discount.valid_from:
            cart = Cart.objects.get(id=self.request.session.get('cart_id'))
            cart.discount_code = discount.code
            cart.save()
            return Response({"message": "Discount code applied"}, status=status.HTTP_200_OK)
        else:
            return Response("Invalid discount code", status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------- Orders ---------------------------------------

class CreateOrder(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        # Get the cart ID from the session
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.get(id=cart_id)
        
        # Check if the cart contains any items
        if not cart.cart_items.exists():
            return Response("Cannot create order with an empty cart", status=status.HTTP_400_BAD_REQUEST)
        
        # Use the CartSerializer to calculate the grand total
        cart_serializer = CartSerializer(instance=cart)
        subtotal = round(cart_serializer.get_subtotal(cart) or 0,2)
        grandtotal = round(cart_serializer.get_grandtotal(cart)or 0,2)
        discount = round(cart_serializer.get_discount(cart)or 0,2)
        # Extract data from the request
        name = request.data.get('name')
        shipping_address = request.data.get('shipping_address')
        phone_number = request.data.get('phone_number')
        
        # Create order data to pass to the OrderSerializer
        order_data = {
            'name': name,
            'shipping_address': shipping_address,
            'phone_number': phone_number,
            'grandtotal': grandtotal,
            'subtotal':subtotal,
            'discount':discount,
            'order_items': []
        }

        # Add cart items to order data
        cart_items = cart.cart_items.all()
        for cart_item in cart_items:
            order_item_data = {
                'product': cart_item.product.id,
                'quantity': cart_item.quantity,
                'subtotal': cart_item.product.price * cart_item.quantity,
            }
            order_data['order_items'].append(order_item_data)

        # Create the order using the OrderSerializer
        order_serializer = OrderSerializer(data=order_data)
        
        if order_serializer.is_valid():
            order = order_serializer.save()

            # Clear the cart after creating the order
            cart.cart_items.all().delete()

            # Optionally, you might want to clear the cart ID from the session
            request.session.pop('cart_id', None)

            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
   
    def get_queryset(self):
        return Order.objects.all()
    
class ViewSingleOrder(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
   
    def get_queryset(self):
        return Order.objects.all()
    

# ADMIN VIEWS

# --------------------------------------- MANAGING CATEGORIES ---------------------------------------

class CreateCategories(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter,]
    search_fields = ['title','active']  
    ordering_fields = ['priority']  # Add 'ordering' field for ordering

class EditCategory(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# --------------------------------------- MANAGING SUBCATEGORIES ---------------------------------------

class CreateSubCategories(generics.CreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']  

class EditSubCategory(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

# --------------------------------------- MANAGING PRODUCTS ---------------------------------------

class CreateProduct(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class EditProduct(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# --------------------------------------- MANAGING ORDERS ---------------------------------------
    
class ListCustomerOrders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class ManageCustomerOrders(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# --------------------------------------- VIEW CUSTOMER DETAILS ---------------------------------------

class GetCustomerDetails(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        try:
            customer_group = Group.objects.get(name=settings.USER_GROUPS['customer'])
            return customer_group.user_set.all()
        except Group.DoesNotExist:
            return []

# --------------------------------------- MANAGING DISCOUNTS ---------------------------------------

class CreateDiscount(generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class ListDiscount(generics.ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class EditDiscount(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
