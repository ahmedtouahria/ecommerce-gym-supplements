from django.forms import ModelForm

from shopping.models import Product

class ProductForm(ModelForm):
    class Meta:
        model=Product
        fields ='__all__'
        exclude = ('barcode_num','count_sould','num_views','date_add','profit')