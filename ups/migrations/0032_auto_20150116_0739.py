# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0031_auto_20150113_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickticket',
            name='fileLineSep',
            field=models.CharField(default=b'\n', max_length=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 16, 12, 39, 52, 642492, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='PHI_SPL_INSTR_CODE',
            field=models.CommaSeparatedIntegerField(default=b'', max_length=11),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 16, 12, 39, 52, 640512, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
