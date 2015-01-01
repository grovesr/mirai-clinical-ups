# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0009_auto_20150101_0957'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custorder',
            name='ups_pkt',
        ),
        migrations.DeleteModel(
            name='CustOrder',
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='buyerEmail',
            field=models.EmailField(default=b'', max_length=254),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='carrier',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='orderId',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='orderType',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='packSlipType',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='productName',
            field=models.CharField(default=b'', max_length=500),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 1, 15, 33, 40, 343046, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='quantity',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='sep',
            field=models.CharField(default=b'\t', max_length=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='serviceLevel',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToAddress1',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToAddress2',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToAddress3',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToCity',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToCntry',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToName',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToState',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='shipToZip',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='sku',
            field=models.CharField(default=b'', max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='type',
            field=models.CharField(default=b'', max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'01/01/15 15:33:40', max_length=17),
            preserve_default=True,
        ),
    ]
