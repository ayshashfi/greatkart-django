# Generated by Django 4.2.7 on 2023-11-29 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0006_alter_reviewrating_product_alter_reviewrating_user"),
    ]

    operations = [
        migrations.DeleteModel(name="ProductGallery",),
    ]