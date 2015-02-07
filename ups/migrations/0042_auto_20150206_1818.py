# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0041_auto_20150206_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='carrier',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 6, 23, 18, 50, 406196, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 6, 23, 18, 50, 404509, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
