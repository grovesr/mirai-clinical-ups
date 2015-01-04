# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0019_auto_20150103_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='custorderheader',
            name='query',
            field=models.CharField(default=b'', max_length=1024),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 20, 4, 43, 247506, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 20, 4, 43, 245641, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
