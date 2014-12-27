from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from ups.models import mirai_check_args, mirai_get_files, mirai_initialize_ups_pkt, UPS_CO_FILE, UPS_PD, UPS_PH, UPS_PKT, UPS_SO, UPS_SOR
from ups.forms import FileNameForm
import time
import datetime
import random
import os

# Create your views here.
def index(request):
    return render(request,'ups/index.html')

def file_creation(request, pk):
    ups_pkt=get_object_or_404(UPS_PKT,pk=pk)
    
    return render(request,'ups/file_creation.html', {'ups_pkt':ups_pkt})


def file_selection(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FileNameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # create a UPS_PKT object and initialize it
            try:
                files=request.POST.get("files").split('&')
            except KeyError:
                return render(request, 'ups:file_selection', {
                    'error_message': "No files selected.",
                })
            inputType=mirai_check_args(files)
            if  inputType== -1:
                return render(request, 'ups:file_selection', {
                    'error_message': "Problem with the files.",
                })
            ups_pkt=mirai_initialize_ups_pkt(files,inputType)
            
            # redirect to a new URL:)
            return HttpResponseRedirect(reverse('ups:file_creation',args=(ups_pkt,)))
    # if a GET (or any other method) we'll create a blank form
    else:
        form=FileNameForm()
    return render(request, 'ups/file_selection.html', {'form': form})