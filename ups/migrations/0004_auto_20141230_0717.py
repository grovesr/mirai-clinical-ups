# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0003_auto_20141230_0657'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickticket',
            name='division',
            field=models.CharField(default=b'', max_length=10),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pickticket',
            name='warehouse',
            field=models.CharField(default=b'', max_length=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 30, 12, 17, 7, 281214, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'12/30/14 12:17:07', max_length=17),
            preserve_default=True,
        ),
    ]
