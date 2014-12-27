from django import forms

class FileNameForm(forms.Form):
    files=forms.CharField(widget=forms.HiddenInput, max_length=1024)
