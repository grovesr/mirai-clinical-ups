from django.contrib import admin

from ups.models import PickTicket, PD, PH, ShipmentOrderRow, ShipmentOrderReport, CustOrderQueryRow



#class FilesInline(admin.TabularInline):
#    model = CustOrderQueryRow
#    extra = 1

    
class PickTicketAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['fileName']}),
        ('Date information', {'fields': ['DOC_DATE'],'classes':['collapse']}),
    ]
    list_display = ('fileName', 'DOC_DATE')
    list_filter = ['DOC_DATE']
    search_fields = ['fileName']
# Register your models here.
admin.site.register(PickTicket, PickTicketAdmin)
admin.site.register(PD)
admin.site.register(PH)
admin.site.register(ShipmentOrderRow)
admin.site.register(ShipmentOrderReport)
admin.site.register(CustOrderQueryRow)