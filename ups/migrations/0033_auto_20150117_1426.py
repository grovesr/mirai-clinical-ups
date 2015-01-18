# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0032_auto_20150116_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 17, 19, 26, 44, 730091, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 17, 19, 26, 44, 728369, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='fileName',
            field=models.CharField(default=b'', max_length=51),
            preserve_default=True,
        ),
    ]
