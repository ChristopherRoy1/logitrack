# Generated by Django 4.0.1 on 2022-01-19 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_alter_shipment_date_shipped'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
