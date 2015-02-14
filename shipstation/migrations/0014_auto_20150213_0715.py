# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0013_auto_20150213_0651'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipment_item',
            name='id',
        ),
        migrations.AlterField(
            model_name='shipment_item',
            name='shipment',
            field=models.ForeignKey(primary_key=True, serialize=False, to='shipstation.shipment'),
            preserve_default=True,
        ),
    ]
