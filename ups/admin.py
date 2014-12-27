from django.contrib import admin

from ups.models import UPS_PKT, SS_CO, Amazon_CO, Zen_CO, UPS_PD, UPS_PH, UPS_SO, UPS_SOR, UPS_CO_FILE



#class FilesInline(admin.TabularInline):
#    model = UPS_CO_FILE
#    extra = 1
    
class UPS_CO_FILEAdmin(admin.ModelAdmin):
    fieldsets=[
               (None,      {'fields':['fileName']}),
               ('contents',{'fields':['contents'],'classes':['collapse']}),
               ]
    list_display=('fileName','contents')
    
class UPS_PKTAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['fileName']}),
        ('Date information', {'fields': ['DOC_DATE'],'classes':['collapse']}),
    ]
    list_display = ('fileName', 'DOC_DATE')
    list_filter = ['DOC_DATE']
    search_fields = ['fileName']
# Register your models here.
admin.site.register(UPS_PKT, UPS_PKTAdmin)
admin.site.register(UPS_PD)
admin.site.register(UPS_PH)
admin.site.register(UPS_SO)
admin.site.register(UPS_SOR)
admin.site.register(SS_CO)
admin.site.register(Amazon_CO)
admin.site.register(Zen_CO)
admin.site.register(UPS_CO_FILE, UPS_CO_FILEAdmin)