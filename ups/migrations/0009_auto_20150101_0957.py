# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0008_auto_20141230_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='queryId',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'01/01/15 14:57:31', max_length=17),
            preserve_default=True,
        ),
    ]
