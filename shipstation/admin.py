from django.contrib import admin
from shipstation.models import customer,order,shipment,insurance_options,international_options,customs_item,dimensions,order_advanced_options,shipment_advanced_options,order_item,item_option,order_item_weight,shipment_weight,marketplace_user_name,tag,bill_to_address,order_ship_to_address,shipment_ship_to_address
# Register your models here.
admin.site.register(order)
admin.site.register(shipment)
admin.site.register(customer)