# Generated by Django 4.0.1 on 2022-01-18 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_item_quantity_delete_iteminventory'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipmentitem',
            name='is_shipped',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]