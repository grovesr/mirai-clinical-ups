from django.db import models

# Create your models here.

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
    orderId=models.IntegerField(default=0)#number     The system generated identifier for the order. This is a read-only field.
    orderNumber=models.IntegerField(default=0)#string     A user-defined order number used to identify an order.
    orderKey=models.CharField(max_length=50,default='')#string     A user-provided key that should be unique to each order.
    orderDate=models.DateField()#string     The date the order was placed.
    paymentDate=models.DateField()#string     The date the order was paid for.
    orderStatus=models.CharField(max_length=20,default=AWAITING_SHIPMENT,
                                 choices=orderStatusChoices)#string     The order's status. Possible values: "awaiting_payment", "awaiting_shipment", "shipped", "on_hold", "cancelled"
    customerUsername=models.CharField(max_length=50,default='')#string     Identifier for the customer in the originating system. This is typically a username or email address.
    customerEmail=models.CharField(max_length=100,default='')#string     The customer's email address.
    orderTotal=models.FloatField(default=0.0)#number     The order total.
    amountPaid=models.FloatField(default=0.0)#number     The total amount paid for the Order.
    taxAmount=models.FloatField(default=0.0)#number     The total tax amount for the Order.
    shippingAmount=models.FloatField(default=0.0)#number     Shipping amount paid by the customer, if any.
    customerNotes=models.TextField(default='')#string     Notes left by the customer when placing the order.
    internalNotes=models.TextField(default='')#string     Private notes that are only visible to the seller.
    gift=models.BooleanField(default=False)#boolean     Specifies whether or not this Order is a gift
    giftMessage=models.TextField(default='')#string     Gift message left by the customer when placing the order.
    paymentMethod=models.CharField(max_length=30,default='')#string     Method of payment used by the customer.
    requestedShippingService=models.CharField(max_length=50,default='')#string     Identifies the shipping service selected by the customer when placing this order.
    carrierCode=models.CharField(max_length=30,default='')#string     The code for the carrier that is to be used(or was used) when this order is shipped(was shipped).
    serviceCode=models.CharField(max_length=30,default='')#string     The code for the shipping service that is to be used(or was used) when this order is shipped(was shipped).
    packageCode=models.CharField(max_length=30,default='')#string     The code for the package type that is to be used(or was used) when this order is shipped(was shipped).
    confirmation=models.CharField(max_length=30,default='')#string     The type of delivery confirmation that is to be used(or was used) when this order is shipped(was shipped).
    shipDate=models.DateField()#string     The date the order was shipped.
    holdUntilDate=models.DateField()#string     If placed on hold, this date is the expiration date for this order's hold status. The order is moved back to awaiting_shipment on this date.

class insurance_options(models.Model):
    """
    Shipstation insuranceOptions model
    """
    SHIPSURANCE='shipsurance'
    CARRIER='carrier'
    providerOptions=(
        (SHIPSURANCE,SHIPSURANCE),
        (CARRIER,CARRIER),
    )
    provider=models.CharField(max_length=15,default=CARRIER,choices=providerOptions)#string     Preferred Insurance provider. Available options: "shipsurance" or "carrier"
    insureShipment=models.BooleanField(default=False)#boolean     Indicates whether shipment should be insured.
    insuredValue=models.FloatField(default=0.0)#number     Value to insure

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
    contents=models.CharField(max_length=20,default=MERCH,choices=contentsChoices)#string     Contents of international shipment. Available options are: "merchandise", "documents", "gift", "returned_goods", or "sample"

class customs_item(models.Model):
    """
    Shipstation customsItem
    """
    description=models.CharField(max_length=100,default='')#string     A short description of the CustomsItem
    quantity=models.IntegerField(default=0)#number     The quantity for this line item
    value=models.FloatField(default=0.0)#number     The value (in USD) of the line item
    harmonizedTariffCode=models.CharField(max_length=20,default='')#string     The Harmonized Commodity Code for this line item
    countryOfOrigin=models.CharField(max_length=2,default='')#string     The 2-character country code where the item originated

class dimensions(models.Model):
    """
    Shipstation dimensions model
    """
    length=models.FloatField(default=0.0)
    width=models.FloatField(default=0.0)
    height=models.FloatField(default=0.0)
    units=models.CharField(max_length=10,default='')

class advanced_options(models.Model):
    """
    Shipstation AdvancdOptions model
    """
    order=models.ForeignKey(order)
    warehouseId=models.IntegerField(default=0)#number     Specifies the warehouse where to the order is to ship from.
    nonMachinable=models.BooleanField(default=False)#boolean     Specifies whether the order is non-machinable.
    saturdayDelivery=models.BooleanField(default=False)#boolean     Specifies whether the order is to be delivered on a Saturday.
    containsAlcohol=models.BooleanField(default=False)#boolean     Specifies whether the order contains alcohol.
    storeId=models.IntegerField(default=0)#number     ID of store that is associated with the order.
    customField1=models.TextField(default='')#string     Field that allows for custom data to be associated with an order.
    customField2=models.TextField(default='')#string     Field that allows for custom data to be associated with an order.
    customField3=models.TextField(default='')#string     Field that allows for custom data to be associated with an order.
    source=models.CharField(max_length=50,default='')#string     Identifies the original source/marketplace of the order.
    billToParty=models.CharField(max_length=50,default='')#string     Identifies which party to bill. Possible values: "my_account", "recipient", "third_party".
    billToAccount=models.CharField(max_length=50,default='')#string     Account number of billToParty.
    billToPostalCode=models.CharField(max_length=50,default='')#string     Postal Code of billToParty.
    billToCountryCode=models.CharField(max_length=50,default='')#string     Country Code of billToParty.

class order_item(models.Model):
    """
    Shipstation orderItem model
    """
    models.ForeignKey(order)
    lineItemKey=models.CharField(max_length=100, default=None)
    sku=models.CharField(max_length=100,default='')
    name=models.CharField(max_length=100,default='')
    imageUrl=models.CharField(max_length=200,default='',blank=True)
    quantity=models.IntegerField(default=0)
    unitPrice=models.FloatField(default=0)
    warehouseLocation=models.CharField(max_length=100,default='')
    productId=models.IntegerField(default=0)
    
class item_option(models.Model):
    """
    Shipstation item_option model
    """
    order_item=models.ForeignKey(order_item)
    name=models.CharField(max_length=50,default='')
    value=models.CharField(max_length=50,default='')

class weight(models.Model):
    """
    Shipstation weight model
    """
    order_item=models.ForeignKey(order_item)
    value=models.FloatField(default=0.0)
    units=models.CharField(max_length=50,default='')
    
class customer(models.Model):
    """
    Shipstation customer model
    """
    customerId=models.IntegerField(default=0)
    name=models.CharField(max_length=100,default='')
    company=models.CharField(max_length=35,default='', blank=True)
    street1=models.CharField(max_length=100,default='')
    street2=models.CharField(max_length=100,default='', blank=True)
    city=models.CharField(max_length=40,default='')
    state=models.CharField(max_length=3,default='')
    postalCode=models.CharField(max_length=11,default='')
    countryCode=models.CharField(max_length=4,default='', blank=True)
    phone=models.CharField(max_length=15,default='',blank=True)
    email=models.CharField(max_length=100,default='',blank=True)
    addressVerified=models.CharField(max_length=35,default='')

class marketplace_user_name(models.Model):
    """
    Shipstation marketplace user name model
    """
    
    marketplaceId=models.IntegerField(default=0)
    marketplace=models.CharField(max_length=100,default='')
    username=models.CharField(max_length=100,default='')
    
class tag(models.Model):
    """
    Shipstation tag model
    """
    tagId=models.IntegerField(default=0)
    name=models.CharField(max_length=100,default='')
    color=models.CharField(max_length=7,default='#090909')
    
class address(models.Model):
    """
    Shipstation address model
    """
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
    company=models.CharField(max_length=35,default='', blank=True)
    street1=models.CharField(max_length=100,default='')
    street2=models.CharField(max_length=100,default='', blank=True)
    street3=models.CharField(max_length=100,default='', blank=True)
    city=models.CharField(max_length=40,default='')
    state=models.CharField(max_length=3,default='')
    postalCode=models.CharField(max_length=11,default='')
    country=models.CharField(max_length=4,default='', blank=True)
    phone=models.CharField(max_length=15,default='',blank=True)
    residential=models.BooleanField(default=True, blank=True)
    addressVerified=models.CharField(max_length=35, default=NOT_VALIDATED,
                                      choices=addressValidationChoices)
    
class bill_to_address(address):
    """
    Shipstation billTo address
    """
    models.ForeignKey(order)
    
class ship_to_address(address):
    """
    Shipstation billTo address
    """
    models.ForeignKey(order)
    