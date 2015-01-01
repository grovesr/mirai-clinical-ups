from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from ups.models import mirai_check_args, mirai_get_files, mirai_initialize_ups_pkt, CustOrderQueryRow, PD, PH, PickTicket, ShipmentOrderRow, ShipmentOrderReport
from ups.forms import FileNameForm
import time
import datetime
import random
import os

# Create your views here.
def index(request):
    return render(request,'ups/index.html')

def file_creation(request, pk):
    ups_pkt=get_object_or_404(PickTicket,pk=pk)
    
    return render(request,'ups/file_creation.html', {'ups_pkt':ups_pkt})


def file_selection(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FileNameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # create a PickTicket object and initialize it
            try:
                files=request.POST.get("files").split('&')
            except KeyError:
                return render(request, 'ups/file_selection.html', {
                    'error_message': "No files selected.",
                })
            inputType=mirai_check_args(files)
            if  inputType== -1:
                print "inputType="+str(inputType)+"\n"
                return render(request, 'ups/file_selection.html', {
                    'error_message': "Problem with the files.",
                })
            ups_pkt_id=mirai_initialize_ups_pkt(files,inputType)
            if ups_pkt_id == -1:
                return render(request, 'ups/file_selection.html', {
                    'error_message': "Problem with the files.",
                })
            #
            # redirect to a new URL:)
            return HttpResponseRedirect(reverse('ups:file_creation',args=[ups_pkt_id,]))
    # if a GET (or any other method) we'll create a blank form
    else:
        form=FileNameForm()
    return render(request, 'ups/file_selection.html', {'form': form})