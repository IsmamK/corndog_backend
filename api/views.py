from django.shortcuts import render
from .models import * 
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your views here.
class AllProducts(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SingleProduct(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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
            self.request.session.set_expiry(timezone.now() + timedelta(seconds=session_timeout))
            
            
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
    
    
