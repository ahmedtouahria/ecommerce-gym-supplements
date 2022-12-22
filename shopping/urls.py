from django.urls import path,re_path
from api.views import get_wilaya

from shopping.views import * 
urlpatterns = [
path('',index,name='index'),    
path('',index,name='index'),
path('products/',products,name='products'),
path('register/',register,name='register'),
path('login/',login_customer,name='login'),
path('profile/',profile,name='profile'),
path('profile/orders',profile_orders,name='profile_orders'),
path('profile/orders/<str:pk>',myorders,name='myorders'),
path('products/<str:pk>',product,name='single-product'),
path('products/<str:pk>/<str:ref_code>',productWithCode,name='single-product-code'),
path('category=<str:cat>/',categorys,name='category'),
path("logout/", logout_request, name="logout_request"),
path('cart',card,name='card'),
path('update_item/',updateItem, name="update_item"),
path('checkout/success/', success_order, name="success_order"),
path('checkout',checkout,name='checkout'),
path('about',about,name='about'),
path('getwilaya',get_wilaya,name='get_wilaya'),

]
