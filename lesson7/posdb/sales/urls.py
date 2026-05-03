# sales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # /sales/products/       → បញ្ជីផលិតផល
    path('products_list/', views.product_list, name='product_list'),

    # /sales/products/1/     → ទំព័រលម្អិតសម្រាប់ product id=1
    path('products/<int:pk>/', views.product_detail, name='product_detail'),

    # /sales/orders/         → ការបញ្ជាទិញទាំងអស់
    path('orders/', views.order_list, name='order_list'),

    path('orders/new/',            views.create_order,   name='create_order'),
    
    path('orders/<int:pk>/items/', views.add_item,       name='add_item'),
    
    path('orders/<int:pk>/checkout/', views.checkout,    name='checkout'),
]