# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0002_order_ordertype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customerUsername',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
