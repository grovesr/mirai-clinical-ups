# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0007_auto_20141230_1451'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ph',
            old_name='PHI_REC_TYPEE',
            new_name='PHI_REC_TYPE',
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 30, 20, 1, 33, 881324, tzinfo=utc)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'12/30/14 20:01:33', max_length=17),
            preserve_default=True,
        ),
    ]
