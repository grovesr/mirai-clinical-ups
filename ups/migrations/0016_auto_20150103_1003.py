# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0015_auto_20150103_0857'),
    ]

    operations = [
        migrations.AddField(
            model_name='ph',
            name='coQueryRow',
            field=models.ForeignKey(default=None, to='ups.CustOrderQueryRow'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 15, 3, 44, 184949, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 15, 3, 44, 183136, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
