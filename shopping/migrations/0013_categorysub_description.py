# Generated by Django 4.0.3 on 2022-12-29 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0012_remove_imagebanner_category_remove_imagebanner_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorysub',
            name='description',
            field=models.TextField(default='', verbose_name='description'),
        ),
    ]
