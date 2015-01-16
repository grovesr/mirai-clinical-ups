# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0026_auto_20150110_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 13, 17, 59, 59, 790469, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pd',
            name='CUST_SKU',
            field=models.CharField(default=b'', max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pd',
            name='ORIG_ORD_QTY',
            field=models.CharField(default=b'', max_length=9),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='PH1_CUST_PO_NBR',
            field=models.CharField(default=b'', max_length=26),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='PH1_FREIGHT_TERMS',
            field=models.CharField(default=b'', max_length=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIPTO',
            field=models.CharField(default=b'', max_length=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIPTO_ADDR_1',
            field=models.CharField(default=b'', max_length=75),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIPTO_CITY',
            field=models.CharField(default=b'', max_length=40),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIPTO_CONTACT',
            field=models.CharField(default=b'', max_length=30, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIPTO_STATE',
            field=models.CharField(default=b'', max_length=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIPTO_ZIP',
            field=models.CharField(default=b'', max_length=11),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='SHIP_VIA',
            field=models.CharField(default=b'UUS2', max_length=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 13, 17, 59, 59, 788665, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
