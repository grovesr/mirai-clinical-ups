# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0014_auto_20150213_0715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipment_item',
            name='order_item',
        ),
    ]
