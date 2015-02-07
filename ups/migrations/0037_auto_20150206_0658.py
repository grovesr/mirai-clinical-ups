# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0036_auto_20150206_0657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='coHeader',
            field=models.ForeignKey(to='ups.CustOrderHeader', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 6, 11, 58, 56, 667698, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 6, 11, 58, 56, 665945, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
