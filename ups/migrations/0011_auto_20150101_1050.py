# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0010_auto_20150101_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='custorderqueryrow',
            name='headers',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 1, 15, 50, 2, 264700, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'01/01/15 15:50:02', max_length=17),
            preserve_default=True,
        ),
    ]
