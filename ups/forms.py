from django import forms
from django.forms import  ModelForm
from ups.models import PickTicket

class FileNameForm(forms.Form):
    files=forms.CharField(widget=forms.HiddenInput, max_length=1024)

class PickTicketForm(ModelForm):
    class Meta:
        model=PickTicket
        fields=['CMPY_NAME','DOC_DATE','fileName']