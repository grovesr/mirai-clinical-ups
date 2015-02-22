from django.db import models
import pytz
import datetime
from django.utils.dateparse import parse_datetime, parse_date, datetime_re, date_re

# Create your models here.

# TODO: Add classes for carriers, products and stores

def get_customerIds(ssgetcustomers):
    """
    retrieve the customerIds from the Shipstation get customers object
    """
    jsData=ssgetcustomers.json()
    customerIds=[]
    customers=jsData['customers']
    for customer in customers:
        customerIds.append(customer['customerId'])
    return customerIds

def get_orderIds(ssgetorders):
    """
    retrieve the orderIds from the Shipstation get orders object
    """
    jsData=ssgetorders.json()
    orderIds=[]
    orders=jsData['orders']
    for order in orders:
        orderIds.append(order['orderId'])
    return orderIds

def get_shipmentIds(ssgetshipments):
    """
    retrieve the shipmentIds from the Shipstation get shipments object
    """
    jsData=ssgetshipments.json()
    shipmentIds=[]
    orders=jsData['shipments']
    for order in orders:
        shipmentIds.append(order['shipmentId'])
    return shipmentIds

def get_pack_slip_type(storeName):
    
    if storeName=='Amazon':
        return 'amazon pack slip'
    elif storeName=='ebay':
        return 'ebay packslip' 
    elif storeName == 'Manual Orders':
        return 'manual orders packslip'
    elif storeName == 'Mirai Clinical':
        return 'mirai clinical packslip'
    
    return 'none'

def parse_datestr_tz(dateTimeString,hours=0,minutes=0):
    if date_re.match(dateTimeString):
        naive=datetime.datetime.combine(parse_date(dateTimeString), datetime.time(hours,minutes))
    else:
        naive=parse_datetime(dateTimeString)
    return pytz.utc.localize(naive)
    

def parse_orders(ssgetorders, storeName, storeId, overwrite=False):
    """
    takes a Shipstation get orders object that has retrieved a list of orders
    and populates the Shipstation tables
    """
    jsData=ssgetorders.json()
    if isinstance(jsData,dict):
        data=[]
        data.append(jsData)
    else:
        data=jsData
        
    for dataItem in data:
        orders=dataItem['orders']
        pages=dataItem['pages']
        page=dataItem['page']
        print "total orders: "+str(dataItem['total'])+" page: "+str(page)+" of "+str(pages)
        for orderData in orders:
            if overwrite or order.objects.filter(pk=orderData['orderId']).count()==0:
                thisOrder=order()
                thisOrder.storeId=storeId
                thisOrder.packSlipType=get_pack_slip_type(storeName)
                thisOrder.orderType=storeName
                thisOrder.parse(orderData)
                thisOrder.save()
                if orderData['internationalOptions']:
                    internationalOptions=international_options(order=thisOrder)
                    internationalOptions.parse(orderData['internationalOptions'])
                    internationalOptions.save()
                if orderData['billTo']:
                    billtoAddress=bill_to_address(order=thisOrder)
                    billtoAddress.parse(orderData['billTo'])
                    billtoAddress.save()
                if orderData['shipTo']:
                    shiptoAddress=order_ship_to_address(order=thisOrder)
                    shiptoAddress.parse(orderData['shipTo'])
                    shiptoAddress.save()
                if orderData['insuranceOptions']:
                    insuranceOptions=order_insurance_options(order=thisOrder)
                    insuranceOptions.parse(orderData['insuranceOptions'])
                    insuranceOptions.save()
                if orderData['items']:
                    for itemData in orderData['items']:
                        thisItem=order_item(order=thisOrder)
                        thisItem.parse(itemData)
                        thisItem.save()
                        if itemData['weight']:
                            thisWeight=order_item_weight(order_item=thisItem)
                            thisWeight.parse(itemData['weight'])
                            thisWeight.save()
                if orderData['advancedOptions']:
                    thisOpt=order_advanced_options(order=thisOrder)
                    thisOpt.parse(orderData['advancedOptions'])
                    thisOpt.save()
    return pages>page

def parse_shipments(ssgetshipments, overwrite=False):
    """
    takes a Shipstation get shipments object that has retrieved a list of shipments
    and populates the Shipstation tables
    """
    jsData=ssgetshipments.json()
    if isinstance(jsData,dict):
        data=[]
        data.append(jsData)
    else:
        data=jsData
        
    for dataItem in data:
        shipments=dataItem['shipments']
        pages=dataItem['pages']
        page=dataItem['page']
        print "total shipments: "+str(dataItem['total'])+" page: "+str(page)+" of "+str(pages)
        for shipmentData in shipments:
            if overwrite or shipment.objects.filter(pk=shipmentData['shipmentId']).count()==0:
                thisShipment=shipment()
                thisShipment.parse(shipmentData)
                thisShipment.save()
                if shipmentData['shipTo']:
                    shiptoAddress=shipment_ship_to_address(shipment=thisShipment)
                    shiptoAddress.parse(shipmentData['shipTo'])
                    shiptoAddress.save()
                if shipmentData['weight']:
                    thisWeight=shipment_weight(shipment=thisShipment)
                    thisWeight.parse(shipmentData['weight'])
                    thisWeight.save()
                if shipmentData['dimensions']:
                    thisDimensions=dimensions(shipment=thisShipment)
                    thisDimensions.parse(shipmentData['dimensions'])
                    thisDimensions.save()
                if shipmentData['insuranceOptions']:
                    insuranceOptions=shipment_insurance_options(shipment=thisShipment)
                    insuranceOptions.parse(shipmentData['insuranceOptions'])
                    insuranceOptions.save()
                if shipmentData['advancedOptions']:
                    thisOpt=shipment_advanced_options(shipment=thisShipment)
                    thisOpt.parse(shipmentData['advancedOptions'])
                    thisOpt.save()
                if shipmentData['shipmentItems']:
                    for shipmentItemData in shipmentData['shipmentItems']:
                        thisShipmentItem=shipment_item(order_item=shipmentItemData['orderItemId'],
                                                       shipment=thisShipment)
                        thisShipmentItem.parse(shipmentItemData)
                        thisShipmentItem.save()
    return pages>page

def parse_customers(ssgetcustomers, overwrite=False):
    """
    takes a Shipstation get customers object that has retrieved a list of customers
    and populate the Shipstation tables
    """
    jsData=ssgetcustomers.json()
    if isinstance(jsData,dict):
        data=[]
        data.append(jsData)
    else:
        data=jsData
        
    for dataItem in data:
        customers=dataItem['customers']
        pages=dataItem['pages']
        page=dataItem['page']
        print "total customers: "+str(dataItem['total'])+" page: "+str(page)+" of "+str(pages)
        for customerData in customers:
            if overwrite or customer.objects.filter(pk=customerData['customerId']).count()==0:
                thisCustomer=customer()
                thisCustomer.parse(customerData)
                thisCustomer.save()
                if customerData['marketplaceUsernames']:
                    for marketplaceUserData in customerData['marketplaceUsernames']:
                        marketplaceUsername=marketplace_user_name(customer=thisCustomer)
                        marketplaceUsername.parse(marketplaceUserData)
                        marketplaceUsername.save()
    return pages>page

class customer(models.Model):
    """
    Shipstation customer model
    """
    customerId=models.IntegerField(default=0,primary_key=True)
    name=models.CharField(max_length=100,default='', blank=True, null=True)
    company=models.CharField(max_length=100,default='', blank=True, null=True)
    street1=models.CharField(max_length=100,default='', blank=True, null=True)
    street2=models.CharField(max_length=100,default='', blank=True, null=True)
    city=models.CharField(max_length=40,default='', blank=True, null=True)
    state=models.CharField(max_length=30,default='', blank=True, null=True)
    postalCode=models.CharField(max_length=30,default='', blank=True, null=True)
    countryCode=models.CharField(max_length=30,default='', blank=True, null=True)
    phone=models.CharField(max_length=3,default='', blank=True, null=True)
    email=models.CharField(max_length=100,default='', blank=True, null=True)
    addressVerified=models.CharField(max_length=35,default='', blank=True, null=True)
    
    def __unicode__(self):
        return "Shipstation customer "+self.name
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class order(models.Model):
    """
    Shipstation order model
    """
    AWAITING_PAYEMENT = 'awaiting_payment'
    AWAITING_SHIPMENT = 'awaiting_shipment'
    SHIPPED = 'shipped'
    ON_HOLD = 'on_hold'
    CANCELLED='cancelled'
    orderStatusChoices = (
        (AWAITING_PAYEMENT, 'awaiting payment'),
        (AWAITING_SHIPMENT, 'awaiting shipment'),
        (SHIPPED, 'shipped'),
        (ON_HOLD, 'on hold'),
        (CANCELLED,'cancelled'),
    )
    orderId=models.IntegerField(default=0,primary_key=True)#number     The system generated identifier for the order. This is a read-only field.
    orderNumber=models.CharField(max_length=100,default='', blank=True, null=True)#string     A user-defined order number used to identify an order.
    orderKey=models.CharField(max_length=50,default='', blank=True, null=True)#string     A user-provided key that should be unique to each order.
    orderDate=models.DateTimeField()#string     The date the order was placed.
    paymentDate=models.DateTimeField(null=True, blank=True)#string     The date the order was paid for.
    orderStatus=models.CharField(max_length=20,default=AWAITING_SHIPMENT,
                                 choices=orderStatusChoices, null=True, blank=True)#string     The order's status. Possible values: "awaiting_payment", "awaiting_shipment", "shipped", "on_hold", "cancelled"
    customerUsername=models.CharField(max_length=50,default='', null=True, blank=True)#string     Identifier for the customer in the originating system. This is typically a username or email address.
    customerEmail=models.CharField(max_length=100,default='', null=True, blank=True)#string     The customer's email address.
    orderTotal=models.FloatField(default=0.0, blank=True, null=True)#number     The order total.
    amountPaid=models.FloatField(default=0.0, blank=True, null=True)#number     The total amount paid for the Order.
    taxAmount=models.FloatField(default=0.0, blank=True, null=True)#number     The total tax amount for the Order.
    shippingAmount=models.FloatField(default=0.0, blank=True, null=True)#number     Shipping amount paid by the customer, if any.
    customerNotes=models.TextField(default='', blank=True, null=True)#string     Notes left by the customer when placing the order.
    internalNotes=models.TextField(default='', blank=True, null=True)#string     Private notes that are only visible to the seller.
    gift=models.BooleanField(default=False, blank=True)#boolean     Specifies whether or not this Order is a gift
    giftMessage=models.TextField(default='', blank=True, null=True)#string     Gift message left by the customer when placing the order.
    paymentMethod=models.CharField(max_length=30,default='', blank=True, null=True)#string     Method of payment used by the customer.
    requestedShippingService=models.CharField(max_length=200,default='',blank=True,null=True)#string     Identifies the shipping service selected by the customer when placing this order.
    carrierCode=models.CharField(max_length=100,default='',blank=True,null=True)#string     The code for the carrier that is to be used(or was used) when this order is shipped(was shipped).
    serviceCode=models.CharField(max_length=100,default='', blank=True, null=True)#string     The code for the shipping service that is to be used(or was used) when this order is shipped(was shipped).
    packageCode=models.CharField(max_length=100,default='', blank=True, null=True)#string     The code for the package type that is to be used(or was used) when this order is shipped(was shipped).
    confirmation=models.CharField(max_length=100,default='', blank=True, null=True)#string     The type of delivery confirmation that is to be used(or was used) when this order is shipped(was shipped).
    shipDate=models.DateTimeField(blank=True, null=True)#string     The date the order was shipped.
    holdUntilDate=models.DateTimeField(blank=True, null=True)#string     If placed on hold, this date is the expiration date for this order's hold status. The order is moved back to awaiting_shipment on this date.
    packSlipType=models.CharField(max_length=50,default='', blank=True, null=True)
    orderType=models.CharField(max_length=50,default='', blank=True, null=True)

    def __unicode__(self):
        return 'Shipstation order: '+str(self.orderNumber)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if (isinstance(value,unicode) or isinstance(value,str)) and (datetime_re.match(value) or date_re.match(value)):
                    setattr(self,key,parse_datestr_tz(value,0,0))
                else:
                    if isinstance(value,unicode):
                        setattr(self,key,value.encode('ascii','replace'))
                    else:
                        setattr(self,key,value)

class shipment(models.Model):
    """
    Shipstation shipment model
    """
    shipmentId=models.IntegerField(default=0,primary_key=True)
    orderId=models.IntegerField(default=0, blank=True, null=True)
    orderNumber=models.CharField(max_length=100,default='', blank=True, null=True)
    createDate=models.DateTimeField( blank=True, null=True) #2014-10-03T06:51:33.6270000"
    shipDate=models.DateTimeField(blank=True, null=True)
    shipmentCost=models.FloatField(default=0.0, blank=True, null=True)
    insuranceCost=models.FloatField(default=0.0, blank=True, null=True),
    trackingNumber=models.CharField(max_length=50,default='', blank=True, null=True)
    isReturnLabel=models.BooleanField(default=False, blank=True)
    batchNumber=models.CharField(max_length=50,default='', blank=True, null=True)
    carrierCode=models.CharField(max_length=50,default='', blank=True, null=True)
    serviceCode=models.CharField(max_length=50,default='', blank=True, null=True)
    packageCode=models.CharField(max_length=50,default='', blank=True, null=True)
    confirmation=models.CharField(max_length=50,default='', blank=True, null=True)
    warehouseId=models.IntegerField(default=0, blank=True, null=True)
    voided=models.BooleanField(default=False, blank=True)
    voidDate=models.DateTimeField(blank=True, null=True)
    marketplaceNotifiedvoided=models.BooleanField(default=False, blank=True)
    notifyErrorMessage=models.TextField(default='', blank=True, null=True)
    
    def __unicode__(self):
        return 'Shipstation shipment: '+str(self.shipmentId)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if (isinstance(value,unicode) or isinstance(value,str)) and (datetime_re.match(value) or date_re.match(value)):
                    setattr(self,key,parse_datestr_tz(value,0,0))
                else:
                    if isinstance(value,unicode):
                        setattr(self,key,value.encode('ascii','replace'))
                    else:
                        setattr(self,key,value)

class insurance_options(models.Model):
    """
    Shipstation insuranceOptions model
    """
    class Meta:
        abstract=True
        
    SHIPSURANCE='shipsurance'
    CARRIER='carrier'
    providerOptions=(
        (SHIPSURANCE,SHIPSURANCE),
        (CARRIER,CARRIER),
    )
    provider=models.CharField(max_length=15,default=CARRIER,choices=providerOptions, blank=True, null=True)#string     Preferred Insurance provider. Available options: "shipsurance" or "carrier"
    insureShipment=models.BooleanField(default=False, blank=True)#boolean     Indicates whether shipment should be insured.
    insuredValue=models.FloatField(default=0.0, blank=True, null=True)#number     Value to insure

    def __unicode__(self):
        return 'Shipstation insurance_options: '
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class order_insurance_options(insurance_options):
    """
    Shipstation order insuranceOptions model
    """
    order=models.OneToOneField(order, primary_key=True)

    def __unicode__(self):
        return 'Shipstation insurance_options for order: '+str(self.order.orderId)

class shipment_insurance_options(insurance_options):
    """
    Shipstation shipment insuranceOptions model
    """
    shipment=models.OneToOneField(shipment, primary_key=True)

    def __unicode__(self):
        return 'Shipstation insurance_options for shipment: '+str(self.shipment.shipmentId)

class international_options(models.Model):
    """
    Shipstation internationalOptions model
    """
    MERCH='merchandise'
    DOCS='documents'
    GIFT='gift'
    RET='returned_goods'
    SAMPLE='sample'
    contentsChoices=(
            (MERCH,'merchandise'),
            (DOCS,'documents'),
            (GIFT,'gift'),
            (RET,'returned goods'),
            (SAMPLE,'sample')
            )
    order=models.OneToOneField(order, primary_key=True)
    contents=models.CharField(max_length=20,default=MERCH,choices=contentsChoices, blank=True, null=True)#string     Contents of international shipment. Available options are: "merchandise", "documents", "gift", "returned_goods", or "sample"
    

    def __unicode__(self):
        return 'Shipstation international_options: '
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class customs_item(models.Model):
    """
    Shipstation customsItem
    """
    international_options=models.ForeignKey(international_options, default=None)
    description=models.CharField(max_length=100,default='', blank=True, null=True)#string     A short description of the CustomsItem
    quantity=models.IntegerField(default=0, blank=True, null=True)#number     The quantity for this line item
    value=models.FloatField(default=0.0, blank=True, null=True)#number     The value (in USD) of the line item
    harmonizedTariffCode=models.CharField(max_length=20,default='', blank=True, null=True)#string     The Harmonized Commodity Code for this line item
    countryOfOrigin=models.CharField(max_length=2,default='', blank=True, null=True)#string     The 2-character country code where the item originated

    def __unicode__(self):
        return 'Shipstation customs_item for order: '+str(self.international_options.order.order_id)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class dimensions(models.Model):
    """
    Shipstation dimensions model
    """
    shipment=models.OneToOneField(shipment, primary_key=True)
    length=models.FloatField(default=0.0, blank=True, null=True)
    width=models.FloatField(default=0.0, blank=True, null=True)
    height=models.FloatField(default=0.0, blank=True, null=True)
    units=models.CharField(max_length=10,default='', blank=True, null=True)
    
    def __unicode__(self):
        return "Shipstation dimensions: w="+str(self.width)," l="+str(self.length)+" h="+str(self.height)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class advanced_options(models.Model):
    """
    Shipstation AdvancdOptions model
    """
    class Meta:
        abstract=True
        
    warehouseId=models.IntegerField(default=0, blank=True)#number     Specifies the warehouse where to the order is to ship from.
    nonMachinable=models.BooleanField(default=False, blank=True)#boolean     Specifies whether the order is non-machinable.
    saturdayDelivery=models.BooleanField(default=False, blank=True)#boolean     Specifies whether the order is to be delivered on a Saturday.
    containsAlcohol=models.BooleanField(default=False, blank=True)#boolean     Specifies whether the order contains alcohol.
    storeId=models.IntegerField(default=0, blank=True, null=True)#number     ID of store that is associated with the order.
    customField1=models.TextField(default='', blank=True, null=True)#string     Field that allows for custom data to be associated with an order.
    customField2=models.TextField(default='', blank=True, null=True)#string     Field that allows for custom data to be associated with an order.
    customField3=models.TextField(default='', blank=True, null=True)#string     Field that allows for custom data to be associated with an order.
    source=models.CharField(max_length=50,default='', blank=True, null=True)#string     Identifies the original source/marketplace of the order.
    billToParty=models.CharField(max_length=50,default='', blank=True, null=True)#string     Identifies which party to bill. Possible values: "my_account", "recipient", "third_party".
    billToAccount=models.CharField(max_length=50,default='', blank=True, null=True)#string     Account number of billToParty.
    billToPostalCode=models.CharField(max_length=50,default='', blank=True, null=True)#string     Postal Code of billToParty.
    billToCountryCode=models.CharField(max_length=50,default='', blank=True, null=True)#string     Country Code of billToParty.
    
    def __unicode__(self):
        return "Shipstation advance_options "
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class order_advanced_options(advanced_options):
    """
    Shipstation order AdvancdOptions model
    """
    order=models.OneToOneField(order, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation advance_options for orderId:"+str(self.order.orderId)

class shipment_advanced_options(advanced_options):
    """
    Shipstation order AdvancdOptions model
    """
    
    shipment=models.OneToOneField(shipment, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation advance_options for shipment:"+str(self.shipment.shipmentId)

class order_item(models.Model):
    """
    Shipstation orderItem model
    """
    order=models.ForeignKey(order, default=None)
    orderItemId=models.IntegerField(default=0,primary_key=True)
    lineItemKey=models.CharField(max_length=100, default=None,blank=True, null=True)
    sku=models.CharField(max_length=100,default='', blank=True, null=True)
    name=models.CharField(max_length=500,default='', null=True, blank=True)
    imageUrl=models.CharField(max_length=200,default='',blank=True, null=True)
    quantity=models.IntegerField(default=0, blank=True, null=True)
    unitPrice=models.FloatField(default=0, blank=True, null=True)
    warehouseLocation=models.CharField(max_length=100,default='', blank=True, null=True)
    productId=models.IntegerField(default=0, null=True, blank=True)
    
    def __unicode__(self):
        return "Shipstation order_item: "+str(self.orderItemId)+" for orderId:"+str(self.order.orderId)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)
    
class shipment_item(models.Model):
    """
    Shipstation shipmentItems model
    """
    shipment=models.ForeignKey(shipment)
    order_item=models.IntegerField(default=1, primary_key=True)
    lineItemKey=models.CharField(max_length=100, default=None,blank=True, null=True)
    sku=models.CharField(max_length=100,default='', blank=True, null=True)
    name=models.CharField(max_length=500,default='', null=True, blank=True)
    imageUrl=models.CharField(max_length=200,default='',blank=True, null=True)
    quantity=models.IntegerField(default=0, blank=True, null=True)
    unitPrice=models.FloatField(default=0, blank=True, null=True)
    warehouseLocation=models.CharField(max_length=100,default='', blank=True, null=True)
    productId=models.IntegerField(default=0, null=True, blank=True) 
    warehouseLocation=models.CharField(max_length=100,default='', blank=True, null=True)
    fulfillmentSku=models.CharField(max_length=100,default='', blank=True, null=True)
    
    def __unicode__(self):
        return "Shipstation shipment_item for order_item:"+str(self.order_item)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)
    
class item_option(models.Model):
    """
    Shipstation item_option model
    """
    order_item=models.ForeignKey(order_item, default=None)
    name=models.CharField(max_length=50,default='', blank=True, null=True)
    value=models.CharField(max_length=50,default='', blank=True, null=True)
    def __unicode__(self):
        return "Shipstation item_option: "+self.name+" for order_item:"+self.order_item.orderItemId
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)

class weight(models.Model):
    """
    Shipstation weight model
    """
    class Meta:
        abstract=True
        
    value=models.FloatField(default=0.0, blank=True, null=True)
    units=models.CharField(max_length=50,default='', blank=True, null=True)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)
                
class order_item_weight(weight):
    """
    Shipstation order_item_weight model
    """
    order_item=models.OneToOneField(order_item, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation weight: "+str(self.value)+" for order_item:"+str(self.order_item.lineItemKey)
    
class shipment_weight(weight):
    """
    Shipstation shipment_weight model
    """
    shipment=models.OneToOneField(shipment, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation weight: "+str(self.value)+" for shipment:"+str(self.shipment.shipmentId)
    
class marketplace_user_name(models.Model):
    """
    Shipstation marketplace user name model
    """
    customer=models.OneToOneField(customer, primary_key=True)
    marketplaceId=models.IntegerField(default=0, blank=True, null=True)
    marketplace=models.CharField(max_length=100,default='', blank=True, null=True)
    username=models.CharField(max_length=100,default='', blank=True, null=True)
    
    def __unicode__(self):
        return "Shipstation marketplace_user_name for "+self.customer.name
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)
    
class tag(models.Model):
    """
    Shipstation tag model
    """
    customer=models.ForeignKey(customer, default=None)
    tagId=models.IntegerField(default=0, blank=True, null=True)
    name=models.CharField(max_length=100,default='', blank=True, null=True)
    color=models.CharField(max_length=7,default='#090909', blank=True, null=True)
    
    def __unicode__(self):
        return "Shipstation tag "+self.name
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)
    
class address(models.Model):
    """
    Shipstation address model
    """
    class Meta:
        abstract=True
        
    VALIDATED = 'Address not yet validated'
    NOT_VALIDATED = 'Address validated successfully'
    VALIDATION_WARNING = 'Address validation warning'
    VALIDATION_FAILED = 'Address validation failed'
    addressValidationChoices = (
        (VALIDATED, VALIDATED),
        (NOT_VALIDATED, NOT_VALIDATED),
        (VALIDATION_WARNING, VALIDATION_WARNING),
        (VALIDATION_FAILED, VALIDATION_FAILED),
    )
    name=models.CharField(max_length=100,default='')
    company=models.CharField(max_length=100,default='', blank=True, null=True)
    street1=models.CharField(max_length=100,default='', blank=True, null=True)
    street2=models.CharField(max_length=100,default='', blank=True, null=True)
    street3=models.CharField(max_length=100,default='', blank=True, null=True)
    city=models.CharField(max_length=50,default='', blank=True, null=True)
    state=models.CharField(max_length=50,default='', blank=True, null=True)
    postalCode=models.CharField(max_length=11,default='', blank=True, null=True)
    country=models.CharField(max_length=50,default='', blank=True, null=True)
    phone=models.CharField(max_length=100,default='', blank=True, null=True)
    residential=models.CharField(max_length=35,blank=True, null=True)
    addressVerified=models.CharField(max_length=35, default=NOT_VALIDATED,
                                      choices=addressValidationChoices, blank=True, null=True)
    
    def parse(self,orderData):
        if not orderData:
            return
        for key,value in orderData.iteritems():
            if  not isinstance(value,dict) and not isinstance(value,list) and value:
                if isinstance(value,unicode):
                    setattr(self,key,value.encode('ascii','replace'))
                else:
                    setattr(self,key,value)
    
class bill_to_address(address):
    """
    Shipstation bill to address
    """
    order=models.OneToOneField(order, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation bill_to_address for order "+str(self.order.orderId)
    
class order_ship_to_address(address):
    """
    Shipstation ship to address for order
    """
    order=models.OneToOneField(order, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation ship_to_address for order "+str(self.order.orderId)
    
class shipment_ship_to_address(address):
    """
    Shipstation ship to address for shipment
    """
    shipment=models.OneToOneField(shipment, primary_key=True)
    
    def __unicode__(self):
        return "Shipstation ship_to_address for shipment "+str(self.shipment.shipmentId)