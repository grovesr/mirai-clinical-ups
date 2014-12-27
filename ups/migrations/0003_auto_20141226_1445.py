# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0002_auto_20141226_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ups_pkt',
            name='DOC_DATE',
            field=models.CharField(default=b'12/26/14 14:45:02', max_length=17),
            preserve_default=True,
        ),
    ]
