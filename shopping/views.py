from django.db.models import Q
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests
from shopping.models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Max,Sum
from datetime import date, timedelta
from django.utils import timezone
from constance import config
from django.utils.translation import gettext_lazy as _
from shopping.utils import recommendation, visited,get_cart_total


# Create your views here.
''' Nous avons deux cas ici
1/ Lorsque le client est enregistré ==>  if request.user.is_authenticated:...
2/ Lorsqu'il n'est pas inscrit ===> else:...

'''


# This function hundel all data about guest user help COOKIES and js


def cookieCart(request):

    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('cart', cart)
    items = []
    order = {"get_cart_total": 0, "get_cart_items": 0}
    cartItem = order['get_cart_items']
    for i in cart:
        try:
            cartItem += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price*cart[i]['quantity'])
            order['get_cart_total'] += total
            try:
                item = {
                    'id': product.id,
                    'product': {'id': product.id, 'name': product.name,'name_ar': product.name_ar, 'price': product.price,
                                'image': product.image}, 'quantity': cart[i]['quantity'], 'color': cart[i]["color"], 'size': cart[i]["size"],
                    'get_total': total,
                }
            except:
                item = {
                    'id': product.id,
                    'product': {'id': product.id, 'name': product.name,'name_ar': product.name_ar, 'price': product.price,
                                'image': product.image}, 'quantity': cart[i]['quantity'],
                    'get_total': total,
                }
            items.append(item)

        except Product.DoesNotExist:
            print("Product.DoesNotExist")
    return {'cartItem': cartItem, 'order': order, 'items': items}


def guestOrder(request, data):
    name = str(data['form']['name'])
    phone = str(data['form']['phone'])
    email = str(data['form']['email'])
    cookieData = cookieCart(request)
    items = cookieData['items']
    if Customer.objects.filter(phone=phone).exists() or Customer.objects.filter(email=email).exists():
        customer=Customer.objects.filter(phone=phone).first()
        customer.name = name
        customer.save()
    else:
        customer=Customer(name=name,phone=phone,email=email)
        customer.save()
    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        print("item", item)
        product = Product.objects.filter(id=item['id']).first()
        try:
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity'],
                color=item['color'],
                size=item['size']
            )
        except:
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity'],
            )
    try:
        return customer, order
    except:
        return None, None


def index(request):
    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
        else:
            order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        items    = cookieData['items']
        order    = cookieData['order']
        cartItem = cookieData['cartItem']
    d = date.today()-timedelta(days=7)
    order_items = Product.objects.all().order_by("-count_sould")[:7]
    top_rated = Product.objects.annotate(rating_count=Sum("rating__stars")).order_by("-rating_count")
    print(top_rated)
    toast = ToastMessage.objects.all().last()
    affaires = Affaire.objects.all()
    sections = Section.objects.all()
    context = {
        "sections":sections,
        "new_arrival": Product.objects.all().reverse()[:5],#last products
        "trending": order_items[:5],# best selling
        "top_rated": top_rated[:5],
        "toast": toast,
        "affaires": affaires,
        "category_sub": CategorySub.objects.all(),
        "category": Category.objects.all(),
        "imgs_banner": ImageBanner.objects.all()[:3],
        "products": Product.objects.all().order_by('?')[:12],
        "items": items,
        "order": order,
        "cartItem": cartItem,
        "titel": "Accueil",'config': config
    }
    return render(request, 'arabic/pages/home.html', context)
# products views

# la page des produits


def products(request):
    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
        else:
            order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
        print(items)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItem = cookieData['cartItem']
    order_items = Product.objects.all().order_by("-count_sould")[:7]
    if request.method == "GET":
        category_data = request.GET.get('category','')
        price_data = request.GET.get('price',1000000)
        products = Product.objects.filter(Q(quantity__gt=0) & Q(price__lt=price_data)& Q(price__gt=0) & Q(category__name__icontains=category_data))
    else:
        products = Product.objects.filter(quantity__gt=0)
    paginator = Paginator(products,40)
    page_number = request.GET.get("page", 1)
    page_products_display = paginator.get_page(page_number)
    context = {
        "trending": order_items[:5],
        "products": page_products_display,
        "category": Category.objects.all(),
        "categorys": CategorySub.objects.all(),
        "order": order,
        "cartItem": cartItem,
        "paginator": paginator,
        "page": page_products_display,
        "page_number": int(page_number),
        "titel": "produits",'config': config
    }
    return render(request, 'arabic/pages/products.html', context)

# category page 
def categorys(request,cat):
    category=CategorySub.objects.filter(name=cat).first()
    products=Product.objects.filter(category=category)
    other_products=Product.objects.filter(category__category=category.category,)

    context={"products":products,
        "category": Category.objects.all(),'config': config,
        "other_products":other_products
    }
    return render(request,"arabic/pages/category.html",context)

def product(request, pk):
    # print("customer_ref",request.session['ref_customer'])

    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
        else:
            order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItem = cookieData['cartItem']
    ref_visitor = request.session.get('ref_visitor')
    try:
        product_id = Product.objects.get(slug=pk)
        visited(request,ref_visitor,product_id)
    except Product.DoesNotExist:
        product_id = None
        return redirect('products')
    order_items = Product.objects.all().order_by("-count_sould")[:7]
    context = {
        "products": Product.objects.filter(category=product_id.category),
        "ratings": Rating.objects.filter(product=product_id),
        "variants": Variant.objects.filter(product=product_id),
        "trending": order_items[:5],
        "category": Category.objects.all(),
        "stars": product_id.avg_rating,
        "product": product_id,
        "order": order,
        "cartItem": cartItem,
        "product_imgs": ProductImage.objects.filter(product=product_id),
        "titel": str(product_id.name).replace(" ", "-").lower(),'config': config

    }
    return render(request, 'arabic/pages/single-product.html', context)
# register Customer views


def productWithCode(request, pk, *args, **kwargs):
    code = str(kwargs.get('ref_code'))
    try:
        customer = Customer.objects.get(code=code)
        request.session['ref_customer'] = customer.id
    except:
        request.session['ref_customer'] = None
        print("customer_ref", request.session['ref_customer'])

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
        print(items)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItem = cookieData['cartItem']
    ref_visitor = request.session.get('ref_visitor')
    try:
        product_id = Product.objects.get(slug=pk)
        visited(request,ref_visitor,product_id)
    except Product.DoesNotExist:
        product_id = None
        return redirect('products')
    order_items = Product.objects.all().order_by("-count_sould")[:7]

    context = {
        "products": Product.objects.filter(category=product_id.category),
        "trending": order_items[:5],
        "ratings": Rating.objects.filter(product=product_id),
        "stars": product_id.avg_rating,
        "product": product_id,
        "category": Category.objects.all(),
        "order": order,
        "cartItem": cartItem,
        "product_imgs": ProductImage.objects.filter(product=product_id),
        "titel": str(product_id.name).replace(" ", "-").lower(),'config': config
    }
    return render(request, 'arabic/pages/single-product.html', context)


''' AUTHENTICATION LOGIC
LogIn / SignUp / Logout
'''
# la page d'inscription


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        email = request.POST['email']
        phone = request.POST['phone']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
       # print(name,phone,password1,password2)
        if len(phone) == 10 and len(password1) >= 8 and password1 == password2:
            list_users = Customer.objects.filter(email=email)
            if list_users.count() < 1:
                user = Customer.objects.create(email=email, phone=phone, password=password1)
                login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, "register user successfully")
                return redirect('index')
        else:
            messages.error(request, _("Unsuccessful registration. Invalid information."))
    context={
        'config': config,

        }
    return render(request, 'account/signup.html',context)
# login Customer views

# la page d'authentication (Login)


def login_customer(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if  len(password) > 3:
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                if user.admin:
                    return redirect('/dashboard/')
                messages.info(request, f"_(Vous êtes maintenant connecté comme) {user.name}.")
                return redirect('index')
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            messages.error(request, _("Invalid username or password."))
    context={
        'config': config,

        }
    return render(request, 'account/login.html',context)


@login_required(login_url='login')
def logout_request(request):
    logout(request)
    messages.info(request, _("You have successfully logged out."))
    return redirect("index")


'''
-------------------
Profits page Logic
-------------------
'''


@login_required(login_url='login')
def profile(request):
    user = request.user
    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
        else:
            order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
    if request.method == "POST":
        print(request.POST)
        name=request.POST.get("name")
        phone=request.POST.get("phone")
        print(name,phone)
        customer=Customer.objects.filter(email=user.email).update(name=name,phone=phone)
        # print(items)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItem = cookieData['cartItem']
    try:
        money = Conversion.objects.get(receveur=user)
    except Conversion.DoesNotExist:
        money = 0
    order_items = Product.objects.all().order_by("-count_sould")[:7]

    context = {
        "money": money,
        "trending": order_items[:5],
        "titel": "profile",
        "items": items,
        "category": Category.objects.all(),

        "order": order,
        "cartItem": cartItem,'config': config

    }
    return render(request, "arabic/pages/myprofile.html", context)


@login_required(login_url='login')
def profile_orders(request):
    user = request.user
    orders = Order.objects.filter(
        customer=user, complete=True).order_by('-date_ordered')
    paginator = Paginator(orders, 8)
    page_number = request.GET.get("page", 1)
    page_products_display = paginator.get_page(page_number)
    order_items = Product.objects.all().order_by("-count_sould")[:7]

    context = {
        "orders": page_products_display,
        "trending": order_items[:5],
        "titel": "Mes commandes",
        "category": Category.objects.all(),

        "page": page_products_display,
        "page_number": int(page_number),
        "paginator": paginator,'config': config

    }
    return render(request, 'arabic/pages/profile_orders.html', context)

@login_required(login_url='login')

def myorders(request, pk):
    user = request.user
    order = Order.objects.filter(transaction_id=pk).first()
    headers = {"X-API-ID": config.ID_API_YALIDIN,
               "X-API-TOKEN": config.TOKEN_API_YALIDIN}
    response = requests.get(
        f"{config.BASE_URL_YALIDIN}parcels/{order.transaction_id}", headers=headers)
    parcel = response.json()
    print(parcel)
    total_data = parcel.get("total_data", 0)
    if total_data > 0:
        transaction_id = parcel.get('data', None)
        last_status = transaction_id[0]
        try:
            if order.customer != user:
                return redirect("profile_orders")
        except:
            return redirect("profile_orders")
        order_items = OrderItem.objects.filter(order=order)
    else:
        order_items = OrderItem.objects.filter(order=order)
        last_status = ""
    product_items = Product.objects.all().order_by("-count_sould")[:7]

    context = {
        "order": order,
        "trending":product_items,
        "order_items": order_items,
        "titel": "Mes commandes",
        "last_status": last_status,
        "category": Category.objects.all(),'config': config

    }
    return render(request, 'arabic/pages/profile_myorder.html', context)


# card product views
# la page de gestionaire de panier d'un client

def card(request):
    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
        else:
            order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
        # print(items)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItem = cookieData['cartItem']
        print("order", order)
    order_items = Product.objects.all().order_by("-count_sould")[:7]

    context = {
        "items": items,
        "trending": order_items[:5],
        "order": order,
        "cartItem": cartItem,
        "titel": "panier",
        "category": Category.objects.all(),
        'config': config


    }
    return render(request, 'arabic/pages/card.html', context)
# checkout order views

# la page de Processus de vente


#@login_required(login_url='login')
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order_changed = request.session.get("order_changed_id", None)
        if order_changed is not None:
            order = Order.objects.get(customer=customer,transaction_id=order_changed)
        else:
            order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
        # print(items)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItem = cookieData['cartItem']
    order_items = Product.objects.all().order_by("-count_sould")[:7]


    context = {
        "items": items,
        "trending": order_items[:5],
        "order": order,
        "cartItem": cartItem,
        "category": Category.objects.all(),
        "titel": "vérifier",
        'config': config,
    }
    return render(request, 'arabic/pages/checkout.html', context)

# endpoint to update cart_item number for user authenticated


def updateItem(request):
    # get user
    customer = request.user
    order_changed = request.session.get("order_changed_id", None)
    if order_changed is not None:
        order = Order.objects.get(customer=customer,transaction_id=order_changed)
    else:
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    # load json request from user
    data = json.loads(request.body)

    if "productColor" in data or "productSize" in data:
        productColor = data.get("productColor", None)
        productSize = data.get("productSize", None)
        productId = data['productId']
        action = data['action']
        product = Product.objects.filter(id=productId).first()
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product, color=productColor, size=productSize)
        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem=orderItem.delete()
            return JsonResponse({"message":'remove',"total":0,"global_total":get_cart_total(order)}, safe=False)

    else:
        # get required data from json  "productId" & "action user (add,remove)"
        productId = data['productId']
        action = data['action']
        product = Product.objects.filter(id=productId).first()
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product)
        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()
        if orderItem.quantity <= 0:
            orderItem=orderItem.delete()
            return JsonResponse({"message":'remove',"total":0,"global_total":get_cart_total(order)}, safe=False)

    return JsonResponse({"message":'Item was added',"total":orderItem.product.price * orderItem.quantity,"id":orderItem.id,"global_total":get_cart_total(order)}, safe=False)



def success_order(request):
    shipping_id=request.session.get("shipping_address",None)
    if shipping_id is not None:
        try:
            shipping_address=ShippingAddress.objects.get(id=shipping_id)
        except :
            shipping_address=None
    else:
        return redirect('products')

    context={"config":config,"titel":"success","shipping_address":shipping_address}
    return render(request,"arabic/pages/success_order.html",context)


def about(request):
    context={
        "config":config
    }
    return render(request,'arabic/pages/about.html',context)