import uuid
import random
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
'''
We need generate a random code for any user to subscribe
'''


def recommendation(request,Model,order):
    ''' ========== recommendation system ============= '''
    try:
        user_id = request.session['ref_customer']
        user_recommended = Model.objects.get(id=user_id)
    except:
        user_recommended = None
    if user_recommended is not None and request.user != user_recommended and order is not None:
        order.recommended_by = user_recommended
        order.save()
        user_recommended.point += 1
        user_recommended.number_of_referalls += 1
        user_recommended.is_receveur = True
        user_recommended.save()
    ''' ====== end recommendation system ========== '''

def generate_random_code():
    code = str(uuid.uuid4()).replace('-', '')[:12]
    return code


def generate_transform_id():
    code = str(uuid.uuid4()).replace('-', '')[:8]
    return code

def generate_barcode():
    code = str(uuid.uuid4()).upper().replace('-', '')[:7]
    return code

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)

def visited(request,ref_visitor,instance):
    if ref_visitor !=instance.id:
        instance.num_views+=1
        instance.save()
        request.session["ref_visitor"]=instance.id
    else:
        print("ref_visitor")

def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser or u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return function
def get_cart_total(order):
    orderitems = order.orderitem_set.all()
    total = sum([item.get_total for item in orderitems])
    return total