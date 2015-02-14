from django import forms
from functools import partial

class DateSpanQueryForm(forms.Form):
    DateInput = partial(forms.DateInput, {'class': 'datepicker'})
    startDate=forms.DateField(widget=DateInput())
    stopDate=forms.DateField(widget=DateInput())
    