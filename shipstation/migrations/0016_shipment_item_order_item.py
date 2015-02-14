# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0015_remove_shipment_item_order_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment_item',
            name='order_item',
            field=models.ForeignKey(to='shipstation.order_item', null=True),
            preserve_default=True,
        ),
    ]
