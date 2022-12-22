from collections import OrderedDict
import json
from django.shortcuts import redirect
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from shopping.models import Customer, Order, Product, Rating
from shopping.utils import recommendation
from shopping.views import cookieCart, guestOrder
from .serializers import *
from constance import config
from django.http import HttpResponse
from xhtml2pdf import pisa


# Get cartItem number 
def cartitem(request):
    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
            order.confirmed=False
            order.save()
        else:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItem = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItem = cookieData['cartItem']
    return cartItem

# end point to show cartItem
class cartitemApi(APIView):
    def get(self, request, format=None):
        return Response({"cartItem": cartitem(request)})


# end point to search product Ascyn



# end point for rating product
@api_view(['POST'])
def rating_product(request):
    if request.method == 'POST':
        user_id = request.data.get("user_id",None)
        product_id = request.data.get("product_id",None)
        stars = request.data.get("stars",4)
        content = request.data.get("content")
        try:
            user = Customer.objects.get(id=user_id)
            product = Product.objects.get(id=product_id)
            print(user, product)
            rate,create = Rating.objects.get_or_create(user=user, product=product)
            rate.stars = stars
            rate.content = content
            rate.save()
        except:
            print("Exception for rating system ")

        return Response({"message": "Hello, world!"})


@api_view(['GET'])
def get_wilaya(request):
    headers = {"X-API-ID": config.ID_API_YALIDIN,"X-API-TOKEN": config.TOKEN_API_YALIDIN }
    response = requests.get(config.BASE_URL_YALIDIN+"wilayas/", headers=headers)
    wilayas = response.json()
    result = wilayas.get('data',None)
    return Response(result)


@api_view(['GET'])
def get_cokmmuns_true(request):
    headers = {"X-API-ID": config.ID_API_YALIDIN,"X-API-TOKEN": config.TOKEN_API_YALIDIN }
    response = requests.get(config.BASE_URL_YALIDIN+"communes/?has_stop_desk=true", headers=headers)
    response_delevery = requests.get(config.BASE_URL_YALIDIN+"deliveryfees/", headers=headers)
    communs = response.json()
    deliveryfees = response_delevery.json()
    result = communs.get('data',None)
    result_2 = deliveryfees.get('data',None)

    return Response({"communs": result, "deliveryfees": result_2})
@api_view(['GET'])
def get_cokmmuns(request,pk):
    headers = {"X-API-ID": config.ID_API_YALIDIN,"X-API-TOKEN": config.TOKEN_API_YALIDIN }
    response = requests.get(f"{config.BASE_URL_YALIDIN}communes/?page={pk}", headers=headers)
    communs = response.json()
    result = communs.get('data',None)
    return Response({"communs": result})


@api_view(['POST'])
def add_product(request):
    product_ref = request.session.get("product_ref", None)
    if request.method == 'POST':
        sizes = request.data.get('sizes', None)
        colors = request.data.get('colors', None)
        if product_ref is not None:
            try:
                product = Product.objects.get(id=product_ref)
            except:
                product=None
            if product is not None and sizes is not None:
                for size in sizes:
                    #s = Variation(product=product, category="size", item=size)
                    #s.save()
                    size,create=Size.objects.get_or_create(size=size)
                    for color in colors:
                    #s = Variation(product=product,category="color", item=color)
                    #s.save()
                        color,create=Color.objects.get_or_create(color=color)
                        Variant.objects.create(product=product,size=size,color=color)
            else:
                return Response({"product or sizes is none !"})
            request.session["product_ref"]=None
            return redirect("index")
        else:
            return Response({"product_ref is none !"})
    return Response({"success": "true"})

# send order to yalidin express 
@api_view(['POST'])
def send_order(request):
    if request.method == 'POST':
        order_id = request.data.get("order_id", None)
        freeshipping = request.data.get("freeshipping", False)
        has_exchange = request.data.get("has_exchange", False)
        try:
            order_obj = Order.objects.get(id=order_id)
        except:
            order_obj = None
        print(request.data)
        if order_obj is not None and Order.objects.filter(id=order_id).exists() and OrderItem.objects.filter(order=order_obj).exists():
            product_list = []
            
            shipping_obj = ShippingAddress.objects.filter(order=order_obj).first()
            orders_items = OrderItem.objects.filter(order=order_id)
            for i in orders_items:
                # hundel product quantity in stock 
                product = Product.objects.get(id=i.product.id)
                product.quantity=product.quantity-i.quantity
                # add count sould in product (for statistics )
                product.count_sould=product.count_sould+i.quantity
                product.save()
                #-----PRODUCT LIST IN PARCEL--------#
                product_list.append({"produit": i.product.name, "quantité": i.quantity})
            print("product list ",len(product_list))
            data = OrderedDict(
                [(0,
                  OrderedDict(
                    [("order_id", str(order_obj.id)), 
                    ("firstname", shipping_obj.name),
                    ("familyname", shipping_obj.name),
                    ("contact_phone",  shipping_obj.phone),
                    ("address", shipping_obj.address if shipping_obj.address is not None else shipping_obj.city + shipping_obj.state),
                    ("to_commune_name", shipping_obj.city),
                    ("to_wilaya_name", shipping_obj.state),
                    ("product_list", str(product_list)),
                    ("price", int(order_obj.get_cart_total)),
                    ("freeshipping", freeshipping), ("is_stopdesk", shipping_obj.is_stopdesk), ("has_exchange", has_exchange), ("product_to_collect", str(product_list) if len(str(product_list))>5 else "product_to_collect does not exist" )])),])
            url = config.BASE_URL_YALIDIN+"parcels/"
            headers = {"X-API-ID": config.ID_API_YALIDIN,"X-API-TOKEN": config.TOKEN_API_YALIDIN, "Content-Type": "application/json"}
            if not order_obj.edited:
                response = requests.post(url=url, headers=headers, data=json.dumps((data)))
                my_response=response.json()
                print(my_response)
                try:
                    transition_yal=my_response[str(order_id)]["tracking"]
                except:
                    return Response({"transition_yal": "Does Not Exist"})
                try:
                    transaction_id=Order.objects.filter(id=order_id).update(transaction_id=transition_yal,confirmed=True)
                    print(transaction_id)
                    print("yalidin",my_response)
                except:
                    return Response({"transaction_id": "Does Not update"})
            else:
                data=OrderedDict(
                    [("order_id", str(order_obj.id)), 
                    ("firstname", shipping_obj.name),
                    ("familyname", shipping_obj.name),
                    ("contact_phone",  shipping_obj.phone),
                    ("address", shipping_obj.address if shipping_obj.address is not None else shipping_obj.city + shipping_obj.state),
                    ("to_commune_name", shipping_obj.city),
                    ("to_wilaya_name", shipping_obj.state),
                    ("product_list", str(product_list)),
                    ("price", int(order_obj.get_cart_total)),
                    ("freeshipping", freeshipping), ("is_stopdesk", shipping_obj.is_stopdesk), ("has_exchange", has_exchange), ("product_to_collect", str(product_list))])

                response = requests.patch(url=url+order_obj.transaction_id, headers=headers, data=json.dumps((data)))
                my_response=response.json()
                print("yalidin",my_response)
                order_obj.confirmed=True
                order_obj.save()
        else:
            return Response({"order is None or does not match"})
    return Response({"success": "true"})

@api_view(['POST'])
def edit_parcel(request):
    if request.method=="POST":
        order=request.data.get("order_tracking",None)
        request.session["order_changed_id"]=order
        print(request.session["order_changed_id"])
    return Response({"success":"true"})
from rest_framework import generics,serializers,filters
class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name','description','slug','image']
class ProductList(generics.ListCreateAPIView):
    serializer_class =ProductsSerializer
    search_fields = ['name','name_ar','description']
    filter_backends = (filters.SearchFilter,)
    queryset = Product.objects.all()

from django.template.loader import render_to_string
import datetime
@api_view(['GET'])
def generate_pdf(request):
    orders_id=request.query_params.get('orders_id').split(',')
    orders_arr= []
    for order in orders_id:
        get_order = Order.objects.filter(id=order).first()
        orders_arr.append(get_order)
    if len(orders_arr)>0:
        template_path = 'arabic/pages/pdf_template.html'
        response = HttpResponse(content_type='application/pdf')
        filename=f'{datetime.date.today()}commande.pdf'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        html = render_to_string(template_path, {'orders_arr': orders_arr})
        pisaStatus = pisa.CreatePDF(html, dest=response)
        return response 
    else:
        return Response({"Orders does not found"})

@api_view(['POST'])
def processOrder(request):
    if request.method == "POST":
        data = request.data
        print(data)
        stop_disk = data['stop_disk']
        # get order if user is authenticated
        if request.user.is_authenticated:
            customer = request.user
            order_changed = request.session.get("order_changed_id", None)
            if order_changed is not None:
                order = Order.objects.get(customer=customer,transaction_id=order_changed)
                order.confirmed=False
                order.save()
            else:
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # get order if user is not authenticated
        else:
            customer, order = guestOrder(request, data)
        '''recommendation function'''
        recommendation(request,Customer,order)
        if customer is not None:
            total = float(data['form']['total'])
            if total > 0:
                order.complete = True
                order.save()
                shipping=ShippingAddress.objects.filter(order=order)
                '''============ if edited parcel ================ '''
                if ShippingAddress.objects.filter(order=order).count() > 0:
                    '''===== make order -> edited for "patch" request not "post" to "YALIDIN" ========'''
                    order.edited=True
                    order.save()
                    '''=====we need update shipping address========'''
                    shipping_address=shipping.update(
                    customer=customer,
                    order=order,
                    name=data['form']['name'],
                    phone=data['form']['phone'],
                    address=None if stop_disk else data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    is_stopdesk=stop_disk
                )
                    request.session["shipping_address"]=shipping_address
                    ''' ======== change session value to parcel =========='''
                    request.session["order_changed_id"]=None
                #========= if create new parcel ================
                else:
                    shipping_address=ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    name=data['form']['name'],
                    phone=data['form']['phone'],
                    address=None if stop_disk else data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    is_stopdesk=stop_disk
                )   
                    #for success order page 
                request.session["shipping_address"]=shipping_address.id
        else:
            return Response({'Customer is None'})
    else:
       return Response({'Methode not allowed'}) 
    return Response({'order submitted..'})

