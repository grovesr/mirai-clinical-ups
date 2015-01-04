# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0012_auto_20150101_1225'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustOrderHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('headers', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='custorderqueryrow',
            name='headers',
        ),
        migrations.AddField(
            model_name='custorderqueryrow',
            name='coHeader',
            field=models.ForeignKey(default=None, to='ups.CustOrderHeader'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='custorderqueryrow',
            name='purchaseDate',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 2, 12, 56, 31, 163818, tzinfo=utc), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pickticket',
            name='DOC_DATE',
            field=models.CharField(default=b'01/02/15 12:56:31', max_length=17),
            preserve_default=True,
        ),
    ]
