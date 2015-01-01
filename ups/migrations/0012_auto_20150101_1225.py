# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0011_auto_20150101_1050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custorderqueryrow',
            name='header',
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 1, 17, 25, 21, 405320, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'01/01/15 17:25:21', max_length=17),
            preserve_default=True,
        ),
    ]
