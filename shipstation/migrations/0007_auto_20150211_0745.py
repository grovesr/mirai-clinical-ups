# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0006_auto_20150210_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill_to_address',
            name='city',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bill_to_address',
            name='country',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bill_to_address',
            name='phone',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bill_to_address',
            name='state',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order_ship_to_address',
            name='city',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order_ship_to_address',
            name='country',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order_ship_to_address',
            name='phone',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order_ship_to_address',
            name='state',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shipment_ship_to_address',
            name='city',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shipment_ship_to_address',
            name='country',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shipment_ship_to_address',
            name='phone',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shipment_ship_to_address',
            name='state',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
