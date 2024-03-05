from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path("products/", views.AllProducts.as_view(), name="all_products"),
    path("products/<int:pk>", views.SingleProduct.as_view(), name="single_product"),
    path("view_cart/",views.ViewCart.as_view(),name="view_cart"),
    path("add_to_cart/",views.AddToCart.as_view(),name="add_to_cart"),
    path("delete_cart/<int:pk>",views.DeleteCart.as_view(),name="delete_cart"),
    path("delete_cart_item/<int:pk>",views.DeleteCartItem.as_view(),name="delete_cart_item"),


  
]