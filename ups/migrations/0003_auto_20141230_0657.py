# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0002_auto_20141230_0651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorder',
            name='productName',
            field=models.CharField(default=b'', max_length=500),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 30, 11, 57, 30, 876451, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'12/30/14 11:57:30', max_length=17),
            preserve_default=True,
        ),
    ]
