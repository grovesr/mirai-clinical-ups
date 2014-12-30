# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0005_auto_20141230_0808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 30, 13, 14, 37, 73630, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='PHI_SPL_INSTR_CODE',
            field=models.CommaSeparatedIntegerField(default=b'08', max_length=11),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'12/30/14 13:14:37', max_length=17),
            preserve_default=True,
        ),
    ]
