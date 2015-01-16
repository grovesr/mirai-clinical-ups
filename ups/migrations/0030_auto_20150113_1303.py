# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0029_auto_20150113_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 13, 18, 3, 53, 366541, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='ORD_TYPE',
            field=models.CharField(default=b'', max_length=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='PHI_SPL_INSTR_DESC',
            field=models.CharField(default=b'', max_length=135, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 13, 18, 3, 53, 364747, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
