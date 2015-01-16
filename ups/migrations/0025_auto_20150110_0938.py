# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0024_auto_20150110_0802'),
    ]

    operations = [
        migrations.AddField(
            model_name='pd',
            name='requiredFields',
            field=models.CharField(default=b'CUST_SKU,ORIG_ORD_QTY,PKT_SEQ_NBR', max_length=1024),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ph',
            name='requiredFields',
            field=models.CharField(default=b'ORD_NBR,PH1_CUST_PO_NBR,SHIPTO_NAME,SHIPTO_ADDR_1,SHIPTO_CITY,SHIPTO_STATE,SHIPTO_CNTRY,SHIPTO_ZIP,PH1_FREIGHT_TERMS,ORD_TYPE,SHIP_VIA,PKT_CTRL_NBR,PHI_SPL_INSTR_NBR,PHI_SPL_INSTR_TYPE,PHI_SPL_INSTR_CODE', max_length=1024),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 10, 14, 38, 5, 681425, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 10, 14, 38, 5, 679648, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
