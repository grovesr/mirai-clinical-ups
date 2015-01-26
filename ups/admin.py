from django.contrib import admin
from ups.models import PickTicket, PD, PH, ShipmentOrderRow, ShipmentOrderReport, CustOrderQueryRow, CustOrderHeader

#class PDAdmin(admin.TabularInline):
#    fields=['CUST_SKU',]

# class PHInlineAdmin(admin.TabularInline):
#     model=PH
#     fieldsets = [
#          (None,{'fields':[('SHIPTO_NAME','PH1_CUST_PO_NBR',)]}),
#          ('Address',{'fields':['SHIPTO_ADDR_1','SHIPTO_ADDR_2','SHIPTO_ADDR_3',
#                                'SHIPTO_CITY','SHIPTO_STATE','SHIPTO_CNTRY',
#                                'SHIPTO_ZIP'],'classes':['collapse']}),
#          ('Required Fields',{'fields':['ORD_TYPE','SHIP_VIA','PH1_FREIGHT_TERMS',
#                           'PKT_CTRL_NBR','PHI_SPL_INSTR_NBR',
#                           'PHI_SPL_INSTR_TYPE','PHI_SPL_INSTR_CODE'],'classes':['collapse']}),
#     ]

#class PickTicketAdmin(admin.ModelAdmin):
    #fieldsets = [
    #    (None,               {'fields': ['fileName']}),
    #    ('Date information', {'fields': ['DOC_DATE'],'classes':['collapse']}),
    #]
    #list_display = ('fileName', 'DOC_DATE')
    #list_filter = ['DOC_DATE']
    #search_fields = ['fileName']
    
admin.site.register(PD)
admin.site.register(PickTicket)
admin.site.register(PH)
admin.site.register(ShipmentOrderRow)
admin.site.register(ShipmentOrderReport)
admin.site.register(CustOrderQueryRow)
admin.site.register(CustOrderHeader)