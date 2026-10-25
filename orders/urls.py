
from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
]
