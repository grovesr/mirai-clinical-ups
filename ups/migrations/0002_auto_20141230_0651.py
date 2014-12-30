# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorder',
            name='purchaseDate',
            field=models.DateTimeField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 30, 11, 51, 34, 336439, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'12/30/14 11:51:34', max_length=17),
            preserve_default=True,
        ),
    ]
