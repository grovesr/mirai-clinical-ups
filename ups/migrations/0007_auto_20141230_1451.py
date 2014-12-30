# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0006_auto_20141230_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 30, 19, 51, 46, 892, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ph',
            name='PH1_STOP_SHIP_DATE',
            field=models.DateTimeField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'12/30/14 19:51:45', max_length=17),
            preserve_default=True,
        ),
    ]
