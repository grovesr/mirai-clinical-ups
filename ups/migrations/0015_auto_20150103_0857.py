# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0014_auto_20150102_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='custorderheader',
            name='ups_pkt',
            field=models.ForeignKey(default=None, to='ups.PickTicket'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 13, 57, 4, 377344, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 3, 13, 57, 4, 375567, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
