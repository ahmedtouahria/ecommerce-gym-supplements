from shopping.models import *
from rest_framework import serializers

class CategorySubSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySub
        fields = '__all__'  

class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySubSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'  