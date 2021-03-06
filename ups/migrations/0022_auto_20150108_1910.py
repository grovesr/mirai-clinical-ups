# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0021_auto_20150107_2206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custorderqueryrow',
            name='parseError',
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 9, 0, 10, 31, 376669, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 9, 0, 10, 31, 374860, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
