# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0004_auto_20150210_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill_to_address',
            name='state',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order_ship_to_address',
            name='state',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shipment_ship_to_address',
            name='state',
            field=models.CharField(default=b'', max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
