# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0012_shipment_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment_item',
            name='shipment',
            field=models.ForeignKey(default=1, to='shipstation.shipment'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shipment_item',
            name='order_item',
            field=models.OneToOneField(null=True, to='shipstation.order_item'),
            preserve_default=True,
        ),
    ]
