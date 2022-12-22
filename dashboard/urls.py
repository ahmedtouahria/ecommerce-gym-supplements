from django.urls import path
from .views import * 
from .utils import superuser_required
urlpatterns = [
path('',superuser_required(dashboard) ,name='dashboard'),
path('commandes/',superuser_required(tables),name='tables'),
path('stock/',superuser_required(stock),name='stock'),
path('stock/<int:pk>',superuser_required(single_product),name='single_product'),
path('add_product/',superuser_required(add_product),name='add_product'),
path('options/',superuser_required(options),name='options'),
path('commandes/order/<str:pk>',superuser_required(order_detail),name='order_detail'),
]
