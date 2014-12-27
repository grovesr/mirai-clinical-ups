# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ups_co_file',
            name='ups_pkt',
            field=models.ForeignKey(default='', to='ups.UPS_PKT'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ups_pkt',
            name='DOC_DATE',
            field=models.CharField(default=b'12/26/14 14:33:12', max_length=17),
            preserve_default=True,
        ),
    ]
