# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0016_shipment_item_order_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='orderNumber',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
