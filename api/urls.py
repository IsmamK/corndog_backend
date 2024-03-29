from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [

#  ---------------------------------------  General Paths    --------------------------------------- 
    #categories
    path('show_categories/', views.ShowCategories.as_view(), name='category-list'), #undocumented
   

    #products (undocumented - filtering & searching )
    path("products/", views.AllProducts.as_view(), name="all_products"),
    path("products/<int:pk>", views.SingleProduct.as_view(), name="single_product"),
        

    
    #cart
    path("view_cart/",views.ViewCart.as_view(),name="view_cart"),
    path("add_to_cart/",views.AddToCart.as_view(),name="add_to_cart"),
    path("delete_cart/<int:pk>",views.DeleteCart.as_view(),name="delete_cart"),
    path("delete_cart_item/<int:pk>",views.DeleteCartItem.as_view(),name="delete_cart_item"),

    #order
    path('create_order',views.CreateOrder.as_view(),name="create_order"),
    path('myorders',views.ViewOrders.as_view(),name="create_order"), 
    path('myorders/<int:pk>',views.ViewSingleOrder.as_view(),name="create_order"), 

    #discount
    path("apply_discount_code",views.ApplyDiscountCode.as_view(),name = "apply_discount_code"),
    
#  --------------------------------------- Admin Dashboard Paths    --------------------------------------- 

    #manage categories
    path('create_categories/', views.CreateCategories.as_view(), name='category-create'), #undocumented
    path('edit_categories/<int:pk>/', views.EditCategory.as_view(), name='category-detail'), #undocumented



    #manage products
    path("create_product",views.CreateProduct.as_view(),name="create_product"), #undocumented
    path("edit_product/<int:pk>",views.EditProduct.as_view(),name="edit_product"), #undocumented
 
    #manage orders
    path("list_customer_orders",views.ListCustomerOrders.as_view(),name="list_customer_orders"), #undocumented
    path("manage_customer_orders/<int:pk>",views.ManageCustomerOrders.as_view(),name="manage_customer_orders"), #undocumented **

    #manage customers
    path("get_customer_details",views.GetCustomerDetails.as_view(),name="get_customer_details"), #undocumented 

    #create_discount
    path("create_discount",views.CreateDiscount.as_view(),name="create_discount"), #undocumented
    path("list_discounts",views.ListDiscount.as_view(),name="list_discount"),  #undocumented
    path("edit_discounts/<int:pk>",views.EditDiscount.as_view(),name="edit_discount"),  #undocumented

  
]