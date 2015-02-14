# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0019_auto_20150213_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment_item',
            name='order_item',
            field=models.IntegerField(default=1, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
