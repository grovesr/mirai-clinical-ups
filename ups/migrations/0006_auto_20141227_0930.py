# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0005_auto_20141226_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='ups_pkt',
            name='fileContents',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ups_pkt',
            name='DOC_DATE',
            field=models.CharField(default=b'12/27/14 09:30:34', max_length=17),
            preserve_default=True,
        ),
    ]
