from django.shortcuts import redirect, render
import json
from shopping.models import CategorySub, Customer, Order, OrderItem, Product, ProductImage, ShippingAddress, Variant
from django.db.models import Avg, Count, Min, Sum
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    if request.user.admin:
        new_order = Order.objects.filter(
            date_ordered__month=date.today().month, confirmed=True)
        today_mony = 0
        today_profit = 0
        for i in new_order:
            orderitems = i.orderitem_set.all()
            for j in orderitems:
                today_mony = today_mony+j.product.price*j.quantity
                today_profit = today_profit+j.product.profit*j.quantity
        new_clients = Customer.objects.filter(
            created_at__day=date.today().day).count()
        num_users = Customer.objects.all().count()
        num_partners = Customer.objects.filter(is_receveur=True).count()
        num_orders = Order.objects.all().count()
        num_products = Product.objects.all().count()
        num_promotors = Customer.objects.filter(is_receveur=True)
        best_sellers = Product.objects.all().order_by("-count_sould")[:7]

        # dashboard chart graphic
        chart_data_order = (
            Order.objects.annotate(date=TruncMonth("date_ordered"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("date")
        )
        chart_data_order_confirmed = (
            Order.objects.filter(confirmed=True).annotate(
                date=TruncMonth("date_ordered"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("date")
        )
        chart_data_order = json.dumps(
            list(chart_data_order), cls=DjangoJSONEncoder)
        chart_data_order_confirmed = json.dumps(
            list(chart_data_order_confirmed), cls=DjangoJSONEncoder)
        context = {
            "chart_data_order_confirmed": chart_data_order_confirmed,
            "chart_data": chart_data_order,
            "today_mony": today_mony,
            "today_profit": today_profit,
            "new_order": new_order.count(),
            "new_clients": new_clients,
            "num_users": num_users,
            "categorys": CategorySub.objects.all(),
            "best_sellers": best_sellers,
            "num_partners": num_partners,
            "num_orders": num_orders,
            "num_products": num_products,
            "num_promotors": num_promotors,
            "titel": "Accueil",
            "active": "home",

        }
        return render(request, 'dashboard/pages/dashboard.html', context)
    else:
        return redirect('index')

@login_required(login_url='login')
def tables(request):
    if request.user.admin:
        orders = Order.objects.filter(complete=True).order_by("-date_ordered")
        orders_no_complete = Order.objects.filter(complete=False).count()
        paginator = Paginator(orders, 12)
        page_number = request.GET.get("page", 1)
        page_products_display = paginator.get_page(page_number)
        context = {
            "orders": page_products_display,
            "titel": "orders",
            "paginator": paginator,
            "page": page_products_display,
            "page_number": int(page_number),
            "active": "tables",
            "orders_no_complete": orders_no_complete,
            "orders_edited": Order.objects.filter(edited=True).count()

        }

        return render(request, "dashboard/pages/tables.html", context)
    else:
        return redirect('index')

@login_required(login_url='login')

def stock(request):
    if request.user.admin:

        if request.method == "GET":
            query = request.GET.get("search", "")
            products = Product.objects.filter(
                Q(name__icontains=query) | Q(category__name__icontains=query) | Q(barcode_num__icontains=query[:12]))
        else:
            products = Product.objects.all().order_by("-name")
        count_products = products.count()
        paginator = Paginator(products, 12)
        page_number = request.GET.get("page", 1)
        page_products_display = paginator.get_page(page_number)
        best_sellers = Product.objects.all().order_by("-count_sould")[:7]
        quantity_in_stock = Product.objects.aggregate(
            quantity_in_stock=Sum("quantity"))
        count_products_category = Product.objects.all().annotate(
            count_products=Sum("count_sould"))
        count_vend_products = OrderItem.objects.filter(
            order__confirmed=True).count()
        print(count_products_category.values("count_products"))
        context = {
            "products": page_products_display,
            "titel": "stock",
            "paginator": paginator,
            "page": page_products_display,
            "page_number": int(page_number),
            "count_products": count_products,
            "best_sellers": best_sellers,
            "quantity_in_stock": quantity_in_stock,
            "categorys": CategorySub.objects.all(),
            "count_vend_produts": count_vend_products,
            "active": "stock",}
        return render(request, "dashboard/pages/stock.html", context)
    else:
        return redirect('index')

@login_required(login_url='login')
def order_detail(request, pk):
    if request.user.admin:
        try:
            order_id = Order.objects.get(transaction_id=pk)
        except:
            order_id = None
        if order_id is not None:
            order_items = OrderItem.objects.filter(order=order_id)
        else:
            return redirect("tables")
        context = {"order_items": order_items,
                "active": "tables",
                "order_id": order_id, "titel": "order details", }
        return render(request, 'dashboard/pages/order_detail.html', context)
    else:
        return redirect('index')
@login_required(login_url='login')

def options(request):
    if request.user.admin:

        context = {"titel": "options"}
        return render(request, 'dashboard/pages/options.html', context)
    else:
        return redirect('index')
        
@login_required(login_url='login')

def add_product(request):
    if request.user.admin:

        if request.method == 'POST':
            if "name" in request.POST:
                print(request.POST)
                name = request.POST.get('name', None)
                name_ar = request.POST.get('name_ar', None)
                price1 = float(request.POST.get('price1', None))
                price2 = float(request.POST.get('price2', None))
                category = request.POST.get('category', None)
                quantity = int(request.POST.get('quantity', None))
                description = request.POST.get('description', None)
                description_ar = request.POST.get('description_ar', None)
                etagere = request.POST.get('etagere', None)
                reference = request.POST.get('reference', None)
                images = request.FILES.getlist("images")
                image = request.FILES.get("image", None)
                print(images)
                try:
                    product_duplicated = Product.objects.get(name=name)
                except Product.DoesNotExist:
                    product_duplicated = None
                if product_duplicated is not None:
                    pass
                else:
                    try:
                        category_id = CategorySub.objects.get(name=category)
                    except:
                        category_id = None
                    try:
                        product = Product(name=name,
                                        name_ar=name_ar,
                                        category=category_id,
                                        price_achat=price1,
                                        price=price2,
                                        quantity=quantity,
                                        description=description,
                                        description_ar=description_ar,
                                        image=image,
                                        etage=etagere,
                                        reference=reference,
                                        )
                        product.save()
                        print("product_ref", product.id)
                # using session for adding product variations later
                        request.session['product_ref'] = product.id
                        for i in images:
                            p = ProductImage(product=product, image=i)
                            p.save()
                            print("success")
                    except:
                        print("error")

        context = {"category": CategorySub.objects.all, "titel": "add product"}
        return render(request, 'dashboard/pages/add_product.html', context)
    else:
        return redirect('index')
        
@login_required(login_url='login')

def single_product(request, pk):
    if request.user.admin:

        product = Product.objects.filter(id=pk).first()
        variants = Variant.objects.filter(product=product)
        print(variants)
        context = {
            "product": product,
            "active": "stock",
            "variants": variants,
            "titel": product.slug
        }
        return render(request, 'dashboard/pages/single_product.html', context)
    else:
        return redirect('index')