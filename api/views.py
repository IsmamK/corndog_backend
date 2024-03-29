from django.shortcuts import render
from .models import * 
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework import filters
from django.contrib.auth.models import Group
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
# Create your views here.

#  --------------------------------------- Categories    --------------------------------------- 

local_datetime = timezone.localtime(timezone.now()).date()

class ShowCategories(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']  


#  ---------------------------------------  Products    --------------------------------------- 

class AllProducts(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']  
    ordering_fields = ['price', 'created_at','is_active']


class SingleProduct(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

#  --------------------------------------- CART    --------------------------------------- 

class ViewCart(generics.ListAPIView):
    serializer_class = CartSerializer  
    authentication_classes = [TokenAuthentication]
    

    def get_queryset(self):
        # Ensure the user is authenticated
        if self.request.user.is_authenticated:
            # Get the authenticated user's cart
            user_cart, created = Cart.objects.get_or_create(user=self.request.user)
            return [user_cart]
        else:
            # For non-authenticated users, check if the session has an associated cart
            session_cart_id = self.request.session.get('cart_id')

            if session_cart_id:
                # Try to get the existing cart associated with the session
                try:
                    existing_cart = Cart.objects.get(id=session_cart_id)
                    return [existing_cart]
                except Cart.DoesNotExist:
                    pass

            # If no existing cart is found, create a new cart for the non-authenticated user
            new_cart = Cart.objects.create(user=None)

            # Store the cart ID in the session
            self.request.session['cart_id'] = new_cart.id

            # Set the session expiration time
            session_timeout = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)  # Default is 2 weeks
            self.request.session.set_expiry(local_datetime + timedelta(seconds=session_timeout))
            
            
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

#  --------------------------------------- Discount    --------------------------------------- 

class ApplyDiscountCode(generics.CreateAPIView,ViewCart):

    def post(self, request):
        discount_code = request.data.get("discount_code")
      
        if not discount_code:
            return Response("Discount code is required", status=status.HTTP_400_BAD_REQUEST)

        user = request.user
       

        try:
            discount = Discount.objects.get(code__iexact=discount_code)
            print(discount)
        except Discount.DoesNotExist:
            print("namecheck failed")
            return Response("Invalid discount code", status=status.HTTP_400_BAD_REQUEST)

        usage, created = DiscountUsage.objects.get_or_create(user=user, discount=discount)
        print(usage)
        if usage is None:
            print("usage exist check failed")
            return Response("Invalid discount code", status=status.HTTP_400_BAD_REQUEST)
        print(local_datetime <= discount.valid_to)
        print(local_datetime >= discount.valid_from)
        print(discount.valid_from,"current time:",local_datetime)
        if local_datetime <= discount.valid_to and local_datetime >= discount.valid_from:
            print( "usage count",usage.usage_count , "max_usage", discount.max_usage)
            if usage.usage_count < discount.max_usage:
                print("usage check passed")
                cart = user.cart
                cart.discount_code = discount.code
                cart.save()
                return Response({"message": "Discount code applied", "discount": serialized_discount}, status=status.HTTP_200_OK)
            else:
                return Response("Discount code usage limit exceeded", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid discount code", status=status.HTTP_400_BAD_REQUEST)

#  --------------------------------------- ORDERS    --------------------------------------- 

class CreateOrder(generics.CreateAPIView):
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]

    def post(self,request):
        user = request.user
        cart = user.cart
        cart_items = cart.cart_items.all()

        if len(cart_items) == 0:
            return Response("Cannot create order with empty cart")

        shipping_address = request.data.get('shipping_address')
        phone_number = request.data.get('phone_number')
        discount_code = request.data.get('discount_code')
         
        order_data = {
            'user': user.id,
            'shipping_address': shipping_address,
            'phone_number': phone_number,
            
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order = order_serializer.save()

            for cart_item in cart_items:
                OrderItem.objects.create(order=order,product = cart_item.product,quantity = cart_item.quantity)

            cart.cart_items.all().delete()

            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

class ViewOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
   
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
class ViewSingleOrder(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
   
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    

#ADMIN VIEWS

#  --------------------------------------- MANAGING CATEGORIES    --------------------------------------- 

class CreateCategories(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']  

class EditCategory(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



#  --------------------------------------- MANAGING PRODUCTS    --------------------------------------- 

class CreateProduct(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class EditProduct(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

#  --------------------------------------- MANAGING ORDERS    ---------------------------------------
    
class ListCustomerOrders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class ManageCustomerOrders(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

#  --------------------------------------- VIEW CUSTOMER DETAILS    ---------------------------------------

class GetCustomerDetails(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        try:
            customer_group = Group.objects.get(name=settings.USER_GROUPS['customer'])
            return customer_group.user_set.all()
        except Group.DoesNotExist:
            return []

#  --------------------------------------- MANAGING DISCOUNTS    ---------------------------------------

class CreateDiscount(generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class ListDiscount(generics.ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class EditDiscount(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer