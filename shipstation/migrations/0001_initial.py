# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='customer',
            fields=[
                ('customerId', models.IntegerField(default=0, serialize=False, primary_key=True)),
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
                ('description', models.CharField(default=b'', max_length=100, blank=True)),
                ('quantity', models.IntegerField(default=0)),
                ('value', models.FloatField(default=0.0, blank=True)),
                ('harmonizedTariffCode', models.CharField(default=b'', max_length=20, blank=True)),
                ('countryOfOrigin', models.CharField(default=b'', max_length=2, blank=True)),
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
                ('customer', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.customer')),
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
                ('orderId', models.IntegerField(default=0, serialize=False, primary_key=True)),
                ('orderNumber', models.CharField(default=b'', max_length=100)),
                ('orderKey', models.CharField(default=b'', max_length=50)),
                ('orderDate', models.DateTimeField()),
                ('paymentDate', models.DateTimeField()),
                ('orderStatus', models.CharField(default=b'awaiting_shipment', max_length=20, choices=[(b'awaiting_payment', b'awaiting payment'), (b'awaiting_shipment', b'awaiting shipment'), (b'shipped', b'shipped'), (b'on_hold', b'on hold'), (b'cancelled', b'cancelled')])),
                ('customerUsername', models.CharField(default=b'', max_length=50, blank=True)),
                ('customerEmail', models.CharField(default=b'', max_length=100, blank=True)),
                ('orderTotal', models.FloatField(default=0.0, null=True, blank=True)),
                ('amountPaid', models.FloatField(default=0.0, null=True, blank=True)),
                ('taxAmount', models.FloatField(default=0.0, null=True, blank=True)),
                ('shippingAmount', models.FloatField(default=0.0, null=True, blank=True)),
                ('customerNotes', models.TextField(default=b'', null=True, blank=True)),
                ('internalNotes', models.TextField(default=b'', null=True, blank=True)),
                ('gift', models.BooleanField(default=False)),
                ('giftMessage', models.TextField(default=b'', null=True, blank=True)),
                ('paymentMethod', models.CharField(default=b'', max_length=30, null=True, blank=True)),
                ('requestedShippingService', models.CharField(default=b'', max_length=200, null=True, blank=True)),
                ('carrierCode', models.CharField(default=b'', max_length=30, null=True, blank=True)),
                ('serviceCode', models.CharField(default=b'', max_length=30, null=True, blank=True)),
                ('packageCode', models.CharField(default=b'', max_length=30, null=True, blank=True)),
                ('confirmation', models.CharField(default=b'', max_length=30, null=True, blank=True)),
                ('shipDate', models.DateTimeField(null=True, blank=True)),
                ('holdUntilDate', models.DateTimeField(null=True, blank=True)),
                ('packSlipType', models.CharField(default=b'', max_length=50, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='international_options',
            fields=[
                ('order', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.order')),
                ('contents', models.CharField(default=b'merchandise', max_length=20, null=True, choices=[(b'merchandise', b'merchandise'), (b'documents', b'documents'), (b'gift', b'gift'), (b'returned_goods', b'returned goods'), (b'sample', b'sample')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='bill_to_address',
            fields=[
                ('name', models.CharField(default=b'', max_length=100)),
                ('company', models.CharField(default=b'', max_length=35, null=True, blank=True)),
                ('street1', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('street2', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('street3', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('city', models.CharField(default=b'', max_length=40, null=True, blank=True)),
                ('state', models.CharField(default=b'', max_length=3, null=True, blank=True)),
                ('postalCode', models.CharField(default=b'', max_length=11, null=True, blank=True)),
                ('country', models.CharField(default=b'', max_length=4, null=True, blank=True)),
                ('phone', models.CharField(default=b'', max_length=15, null=True, blank=True)),
                ('residential', models.CharField(max_length=35, null=True, blank=True)),
                ('addressVerified', models.CharField(default=b'Address validated successfully', max_length=35, null=True, blank=True, choices=[(b'Address not yet validated', b'Address not yet validated'), (b'Address validated successfully', b'Address validated successfully'), (b'Address validation warning', b'Address validation warning'), (b'Address validation failed', b'Address validation failed')])),
                ('order', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.order')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order_advanced_options',
            fields=[
                ('warehouseId', models.IntegerField(default=0, blank=True)),
                ('nonMachinable', models.BooleanField(default=False)),
                ('saturdayDelivery', models.BooleanField(default=False)),
                ('containsAlcohol', models.BooleanField(default=False)),
                ('storeId', models.IntegerField(default=0)),
                ('customField1', models.TextField(default=b'', null=True, blank=True)),
                ('customField2', models.TextField(default=b'', null=True, blank=True)),
                ('customField3', models.TextField(default=b'', null=True, blank=True)),
                ('source', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToParty', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToAccount', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToPostalCode', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToCountryCode', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('order', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.order')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order_insurance_options',
            fields=[
                ('provider', models.CharField(default=b'carrier', max_length=15, null=True, choices=[(b'shipsurance', b'shipsurance'), (b'carrier', b'carrier')])),
                ('insureShipment', models.BooleanField(default=False)),
                ('insuredValue', models.FloatField(default=0.0, blank=True)),
                ('order', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.order')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order_item',
            fields=[
                ('orderItemId', models.IntegerField(default=0, serialize=False, primary_key=True)),
                ('lineItemKey', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('sku', models.CharField(default=b'', max_length=100)),
                ('name', models.CharField(default=b'', max_length=500)),
                ('imageUrl', models.CharField(default=b'', max_length=200, null=True, blank=True)),
                ('quantity', models.IntegerField(default=0)),
                ('unitPrice', models.FloatField(default=0, null=True, blank=True)),
                ('warehouseLocation', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('productId', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order_item_weight',
            fields=[
                ('value', models.FloatField(default=0.0)),
                ('units', models.CharField(default=b'', max_length=50)),
                ('order_item', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.order_item')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='order_ship_to_address',
            fields=[
                ('name', models.CharField(default=b'', max_length=100)),
                ('company', models.CharField(default=b'', max_length=35, null=True, blank=True)),
                ('street1', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('street2', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('street3', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('city', models.CharField(default=b'', max_length=40, null=True, blank=True)),
                ('state', models.CharField(default=b'', max_length=3, null=True, blank=True)),
                ('postalCode', models.CharField(default=b'', max_length=11, null=True, blank=True)),
                ('country', models.CharField(default=b'', max_length=4, null=True, blank=True)),
                ('phone', models.CharField(default=b'', max_length=15, null=True, blank=True)),
                ('residential', models.CharField(max_length=35, null=True, blank=True)),
                ('addressVerified', models.CharField(default=b'Address validated successfully', max_length=35, null=True, blank=True, choices=[(b'Address not yet validated', b'Address not yet validated'), (b'Address validated successfully', b'Address validated successfully'), (b'Address validation warning', b'Address validation warning'), (b'Address validation failed', b'Address validation failed')])),
                ('order', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.order')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='shipment',
            fields=[
                ('shipmentId', models.IntegerField(default=0, serialize=False, primary_key=True)),
                ('orderId', models.IntegerField(default=0)),
                ('orderNumber', models.CharField(default=b'', max_length=30)),
                ('createDate', models.DateTimeField()),
                ('shipmentCost', models.FloatField(default=0.0, blank=True)),
                ('trackingNumber', models.CharField(default=b'', max_length=50)),
                ('isReturnLabel', models.BooleanField(default=False)),
                ('batchNumber', models.CharField(default=b'', max_length=50, blank=True)),
                ('carrierCode', models.CharField(default=b'', max_length=50)),
                ('serviceCode', models.CharField(default=b'', max_length=50)),
                ('packageCode', models.CharField(default=b'', max_length=50, blank=True)),
                ('confirmation', models.CharField(default=b'', max_length=50, blank=True)),
                ('warehouseId', models.IntegerField(default=0)),
                ('voided', models.BooleanField(default=False)),
                ('voidDate', models.DateTimeField(blank=True)),
                ('shipDate', models.DateTimeField(blank=True)),
                ('marketplaceNotifiedvoided', models.BooleanField(default=False)),
                ('notifyErrorMessage', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='dimensions',
            fields=[
                ('shipment', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.shipment')),
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
            name='shipment_advanced_options',
            fields=[
                ('warehouseId', models.IntegerField(default=0, blank=True)),
                ('nonMachinable', models.BooleanField(default=False)),
                ('saturdayDelivery', models.BooleanField(default=False)),
                ('containsAlcohol', models.BooleanField(default=False)),
                ('storeId', models.IntegerField(default=0)),
                ('customField1', models.TextField(default=b'', null=True, blank=True)),
                ('customField2', models.TextField(default=b'', null=True, blank=True)),
                ('customField3', models.TextField(default=b'', null=True, blank=True)),
                ('source', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToParty', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToAccount', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToPostalCode', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('billToCountryCode', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('shipment', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.shipment')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='shipment_insurance_options',
            fields=[
                ('provider', models.CharField(default=b'carrier', max_length=15, null=True, choices=[(b'shipsurance', b'shipsurance'), (b'carrier', b'carrier')])),
                ('insureShipment', models.BooleanField(default=False)),
                ('insuredValue', models.FloatField(default=0.0, blank=True)),
                ('shipment', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.shipment')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='shipment_ship_to_address',
            fields=[
                ('name', models.CharField(default=b'', max_length=100)),
                ('company', models.CharField(default=b'', max_length=35, null=True, blank=True)),
                ('street1', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('street2', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('street3', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('city', models.CharField(default=b'', max_length=40, null=True, blank=True)),
                ('state', models.CharField(default=b'', max_length=3, null=True, blank=True)),
                ('postalCode', models.CharField(default=b'', max_length=11, null=True, blank=True)),
                ('country', models.CharField(default=b'', max_length=4, null=True, blank=True)),
                ('phone', models.CharField(default=b'', max_length=15, null=True, blank=True)),
                ('residential', models.CharField(max_length=35, null=True, blank=True)),
                ('addressVerified', models.CharField(default=b'Address validated successfully', max_length=35, null=True, blank=True, choices=[(b'Address not yet validated', b'Address not yet validated'), (b'Address validated successfully', b'Address validated successfully'), (b'Address validation warning', b'Address validation warning'), (b'Address validation failed', b'Address validation failed')])),
                ('shipment', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.shipment')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='shipment_weight',
            fields=[
                ('value', models.FloatField(default=0.0)),
                ('units', models.CharField(default=b'', max_length=50)),
                ('shipment', models.OneToOneField(primary_key=True, serialize=False, to='shipstation.shipment')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tagId', models.IntegerField(default=0)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('color', models.CharField(default=b'#090909', max_length=7)),
                ('customer', models.ForeignKey(default=None, to='shipstation.customer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order_item',
            name='order',
            field=models.ForeignKey(default=None, to='shipstation.order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item_option',
            name='order_item',
            field=models.ForeignKey(default=None, to='shipstation.order_item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customs_item',
            name='international_options',
            field=models.ForeignKey(default=None, to='shipstation.international_options'),
            preserve_default=True,
        ),
    ]
