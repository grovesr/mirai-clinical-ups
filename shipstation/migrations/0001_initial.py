# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('company', models.CharField(default=b'', max_length=35, blank=True)),
                ('street1', models.CharField(default=b'', max_length=100)),
                ('street2', models.CharField(default=b'', max_length=100, blank=True)),
                ('street3', models.CharField(default=b'', max_length=100, blank=True)),
                ('city', models.CharField(default=b'', max_length=40)),
                ('state', models.CharField(default=b'', max_length=3)),
                ('postalCode', models.CharField(default=b'', max_length=11)),
                ('country', models.CharField(default=b'', max_length=4, blank=True)),
                ('phone', models.CharField(default=b'', max_length=15, blank=True)),
                ('residential', models.BooleanField(default=True)),
                ('addressVerified', models.CharField(default=b'Address validated successfully', max_length=35, choices=[(b'Address not yet validated', b'Address not yet validated'), (b'Address validated successfully', b'Address validated successfully'), (b'Address validation warning', b'Address validation warning'), (b'Address validation failed', b'Address validation failed')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='advanced_options',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('warehouseId', models.IntegerField(default=0)),
                ('nonMachinable', models.BooleanField(default=False)),
                ('saturdayDelivery', models.BooleanField(default=False)),
                ('containsAlcohol', models.BooleanField(default=False)),
                ('storeId', models.IntegerField(default=0)),
                ('customField1', models.TextField(default=b'')),
                ('customField2', models.TextField(default=b'')),
                ('customField3', models.TextField(default=b'')),
                ('source', models.CharField(default=b'', max_length=50)),
                ('billToParty', models.CharField(default=b'', max_length=50)),
                ('billToAccount', models.CharField(default=b'', max_length=50)),
                ('billToPostalCode', models.CharField(default=b'', max_length=50)),
                ('billToCountryCode', models.CharField(default=b'', max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='bill_to_address',
            fields=[
                ('address_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shipstation.address')),
            ],
            options={
            },
            bases=('shipstation.address',),
        ),
        migrations.CreateModel(
            name='customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customerId', models.IntegerField(default=0)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('company', models.CharField(default=b'', max_length=35, blank=True)),
                ('street1', models.CharField(default=b'', max_length=100)),
                ('street2', models.CharField(default=b'', max_length=100, blank=True)),
                ('city', models.CharField(default=b'', max_length=40)),
                ('state', models.CharField(default=b'', max_length=3)),
                ('postalCode', models.CharField(default=b'', max_length=11)),
                ('countryCode', models.CharField(default=b'', max_length=4, blank=True)),
                ('phone', models.CharField(default=b'', max_length=15, blank=True)),
                ('email', models.CharField(default=b'', max_length=100, blank=True)),
                ('addressVerified', models.CharField(default=b'', max_length=35)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='customs_item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(default=b'', max_length=100)),
                ('quantity', models.IntegerField(default=0)),
                ('value', models.FloatField(default=0.0)),
                ('harmonizedTariffCode', models.CharField(default=b'', max_length=20)),
                ('countryOfOrigin', models.CharField(default=b'', max_length=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='dimensions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('length', models.FloatField(default=0.0)),
                ('width', models.FloatField(default=0.0)),
                ('height', models.FloatField(default=0.0)),
                ('units', models.CharField(default=b'', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='insurance_options',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider', models.CharField(default=b'carrier', max_length=15, choices=[(b'shipsurance', b'shipsurance'), (b'carrier', b'carrier')])),
                ('insureShipment', models.BooleanField(default=False)),
                ('insuredValue', models.FloatField(default=0.0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='international_options',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contents', models.CharField(default=b'merchandise', max_length=20, choices=[(b'merchandise', b'merchandise'), (b'documents', b'documents'), (b'gift', b'gift'), (b'returned_goods', b'returned goods'), (b'sample', b'sample')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='item_option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50)),
                ('value', models.CharField(default=b'', max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='marketplace_user_name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marketplaceId', models.IntegerField(default=0)),
                ('marketplace', models.CharField(default=b'', max_length=100)),
                ('username', models.CharField(default=b'', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orderId', models.IntegerField(default=0)),
                ('orderNumber', models.IntegerField(default=0)),
                ('orderKey', models.CharField(default=b'', max_length=50)),
                ('orderDate', models.DateField()),
                ('paymentDate', models.DateField()),
                ('orderStatus', models.CharField(default=b'awaiting_shipment', max_length=20, choices=[(b'awaiting_payment', b'awaiting payment'), (b'awaiting_shipment', b'awaiting shipment'), (b'shipped', b'shipped'), (b'on_hold', b'on hold'), (b'cancelled', b'cancelled')])),
                ('customerUsername', models.CharField(default=b'', max_length=50)),
                ('customerEmail', models.CharField(default=b'', max_length=100)),
                ('orderTotal', models.FloatField(default=0.0)),
                ('amountPaid', models.FloatField(default=0.0)),
                ('taxAmount', models.FloatField(default=0.0)),
                ('shippingAmount', models.FloatField(default=0.0)),
                ('customerNotes', models.TextField(default=b'')),
                ('internalNotes', models.TextField(default=b'')),
                ('gift', models.BooleanField(default=False)),
                ('giftMessage', models.TextField(default=b'')),
                ('paymentMethod', models.CharField(default=b'', max_length=30)),
                ('requestedShippingService', models.CharField(default=b'', max_length=50)),
                ('carrierCode', models.CharField(default=b'', max_length=30)),
                ('serviceCode', models.CharField(default=b'', max_length=30)),
                ('packageCode', models.CharField(default=b'', max_length=30)),
                ('confirmation', models.CharField(default=b'', max_length=30)),
                ('shipDate', models.DateField()),
                ('holdUntilDate', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order_item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lineItemKey', models.CharField(default=None, max_length=100)),
                ('sku', models.CharField(default=b'', max_length=100)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('imageUrl', models.CharField(default=b'', max_length=200, blank=True)),
                ('quantity', models.IntegerField(default=0)),
                ('unitPrice', models.FloatField(default=0)),
                ('warehouseLocation', models.CharField(default=b'', max_length=100)),
                ('productId', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ship_to_address',
            fields=[
                ('address_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shipstation.address')),
            ],
            options={
            },
            bases=('shipstation.address',),
        ),
        migrations.CreateModel(
            name='tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tagId', models.IntegerField(default=0)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('color', models.CharField(default=b'#090909', max_length=7)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='weight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(default=0.0)),
                ('units', models.CharField(default=b'', max_length=50)),
                ('order_item', models.ForeignKey(to='shipstation.order_item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item_option',
            name='order_item',
            field=models.ForeignKey(to='shipstation.order_item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='advanced_options',
            name='order',
            field=models.ForeignKey(to='shipstation.order'),
            preserve_default=True,
        ),
    ]
