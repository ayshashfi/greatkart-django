# Generated by Django 4.2.7 on 2023-12-12 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0011_rename_price_product_product_price"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product", old_name="product_price", new_name="price",
        ),
    ]
