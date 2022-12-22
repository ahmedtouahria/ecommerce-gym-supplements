from django.urls import  path
from .views import *


urlpatterns = [
    path("cartitemApi/", cartitemApi.as_view(), name="cartitemApi"),
    path("product_rating/", rating_product, name="product_rating"),
    path("getcommunstrus/", get_cokmmuns_true, name="get_cokmmuns_true"),
    path("getcommuns/<int:pk>", get_cokmmuns, name="get_communs"),
    path("add_product/", add_product),
    path("send_order/", send_order,name="send_order"),
    path("process_order/", processOrder,name="send_order"),
    path("products/", ProductList.as_view()),
    path("edit_order/", edit_parcel,name="edite_order"),
    path('pdf_view/', generate_pdf, name="pdf_view"),

    ]
