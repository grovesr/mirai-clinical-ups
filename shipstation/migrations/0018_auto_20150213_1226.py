# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0017_auto_20150213_0733'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment_item',
            name='imageUrl',
            field=models.CharField(default=b'', max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment_item',
            name='lineItemKey',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment_item',
            name='name',
            field=models.CharField(default=b'', max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment_item',
            name='productId',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment_item',
            name='quantity',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment_item',
            name='sku',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment_item',
            name='unitPrice',
            field=models.FloatField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
