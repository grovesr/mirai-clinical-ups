# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipstation', '0011_auto_20150211_2221'),
    ]

    operations = [
        migrations.CreateModel(
            name='shipment_item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('warehouseLocation', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('fulfillmentSku', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('order_item', models.OneToOneField(to='shipstation.order_item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
