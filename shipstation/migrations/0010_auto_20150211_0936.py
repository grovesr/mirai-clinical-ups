# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0009_auto_20150211_0932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='orderStatus',
            field=models.CharField(default=b'awaiting_shipment', max_length=20, null=True, blank=True, choices=[(b'awaiting_payment', b'awaiting payment'), (b'awaiting_shipment', b'awaiting shipment'), (b'shipped', b'shipped'), (b'on_hold', b'on hold'), (b'cancelled', b'cancelled')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='paymentDate',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
