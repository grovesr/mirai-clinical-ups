# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0018_auto_20150213_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment_item',
            name='order_item',
            field=models.ForeignKey(primary_key=True, default=1, serialize=False, to='shipstation.order_item'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shipment_item',
            name='shipment',
            field=models.ForeignKey(to='shipstation.shipment'),
            preserve_default=True,
        ),
    ]
