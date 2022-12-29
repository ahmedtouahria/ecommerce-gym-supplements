# Generated by Django 4.0.3 on 2022-12-29 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0011_remove_shippingaddress_zipcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagebanner',
            name='category',
        ),
        migrations.RemoveField(
            model_name='imagebanner',
            name='price',
        ),
        migrations.RemoveField(
            model_name='imagebanner',
            name='titel',
        ),
        migrations.AlterField(
            model_name='imagebanner',
            name='image',
            field=models.FileField(upload_to='banners', verbose_name='image or video '),
        ),
    ]