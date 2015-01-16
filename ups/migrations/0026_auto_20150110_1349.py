# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0025_auto_20150110_0938'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pickticket',
            name='parseErrors',
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 10, 18, 49, 11, 665357, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 10, 18, 49, 11, 663574, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
