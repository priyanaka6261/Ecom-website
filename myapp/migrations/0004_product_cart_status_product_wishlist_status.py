# Generated by Django 4.1.7 on 2023-04-16 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_wishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cart_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='wishlist_status',
            field=models.BooleanField(default=False),
        ),
    ]
