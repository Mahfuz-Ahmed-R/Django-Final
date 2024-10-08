# Generated by Django 5.1 on 2024-08-30 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_reviewmodel_user_shippingaddress_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistmodel',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='wishlistmodel',
            name='quantity',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='wishlistmodel',
            name='size',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.size'),
        ),
    ]
