# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0018_auto_20150103_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ph',
            name='coQueryRow',
        ),
        migrations.AddField(
            model_name='ph',
            name='coHeader',
            field=models.ForeignKey(default=None, to='ups.CustOrderHeader'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='coHeader',
            field=models.ForeignKey(to='ups.CustOrderHeader'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 19, 54, 30, 739601, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 19, 54, 30, 737781, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
