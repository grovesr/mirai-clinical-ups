# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0030_auto_20150113_1303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pd',
            name='error',
        ),
        migrations.RemoveField(
            model_name='pd',
            name='requiredFields',
        ),
        migrations.RemoveField(
            model_name='ph',
            name='error',
        ),
        migrations.RemoveField(
            model_name='ph',
            name='requiredFields',
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 14, 2, 5, 54, 149529, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 14, 2, 5, 54, 147749, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
