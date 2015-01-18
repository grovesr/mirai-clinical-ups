from django import forms
from django.forms.utils import ErrorList
from ups.models import PH, PD

class FileNameForm(forms.Form):
    files=forms.CharField(widget=forms.HiddenInput, max_length=1024)

class PhForm(forms.ModelForm):
    class Meta:
        model = PH
        fields=['ORD_TYPE','SHIPTO_NAME','SHIPTO_ADDR_1','SHIPTO_ADDR_2',
              'SHIPTO_ADDR_3','SHIPTO_CITY','SHIPTO_STATE','SHIPTO_ZIP','SHIP_VIA',
              'PH1_CUST_PO_NBR','PH1_FREIGHT_TERMS','PHI_SPL_INSTR_NBR','PHI_SPL_INSTR_TYPE',
              'PHI_SPL_INSTR_CODE','PHI_SPL_INSTR_DESC','PKT_PROFILE_ID','PKT_CTRL_NBR',]
    error_css_class = 'pkt-error-text'
    required_css_class='pkt-param-text'
    
class PdForm(forms.ModelForm):
    class Meta:
        model = PD
        fields=['SIZE_DESC','CUST_SKU','ORIG_ORD_QTY','PKT_SEQ_NBR',]
    error_css_class = 'pkt-error-text'
    required_css_class='pkt-param-text'
    
class TitleErrorList(ErrorList):
    def __unicode__(self):              # __unicode__ on Python 2
        return self.as_title()

    def as_title(self):
        if not self: 
            return ''
        return '%s, ' % ''.join(['%s, ' % e for e in self])[:-2]