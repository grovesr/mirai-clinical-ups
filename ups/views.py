from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from ups.models import mirai_check_args, mirai_initialize_ups_pkt, PickTicket, PH
from ups.forms import FileNameForm, PickTicketForm
from django.forms.models import inlineformset_factory

# Create your views here.
def index(request):
    return render(request,'ups/index.html')

def blank(request):
    return render(request,'base/blank.html')

def pick_ticket_detail(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_detail.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist'})
    return render(request,'ups/pick_ticket_detail.html', {'ups_pkt':ups_pkt})

def pick_ticket_edit(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_edit.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist',})
    PktInlineFormSet = inlineformset_factory(PickTicket, PH)
    #pktForm=PickTicketForm(instance=ups_pkt)
    if request.method == "POST":
        formset = PktInlineFormSet(request.POST, request.FILES, instance=ups_pkt)
        if formset.is_valid():
            formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(ups_pkt.get_absolute_url())
    else:
        formset = PktInlineFormSet(instance=ups_pkt)
    return render_to_response("ups/pick_ticket_edit.html", {
        "ups_pkt":ups_pkt, "formset": formset,
    })

def pick_ticket_report(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_report.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist'})
    return render(request,'ups/pick_ticket_report.html', {'ups_pkt':ups_pkt})

def pick_ticket_error_report(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_error_report.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist'})
    return render(request,'ups/pick_ticket_error_report.html', {'ups_pkt':ups_pkt})

def pick_ticket_pkt_report(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_pkt_report.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist'})
    return render(request,'ups/pick_ticket_pkt_report.html', {'ups_pkt':ups_pkt})

def pick_ticket_index(request):
    today=timezone.now()
    pkt_list=PickTicket.objects.filter(DOC_DATE__gte = (today - datetime.timedelta(days=7)))
    if len(pkt_list)==0:
        return render(request,'ups/pick_ticket_index.html', {'error_message':'No PickTickets to display'})
    return render(request,'ups/pick_ticket_index.html', {'pkt_list':pkt_list})

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
            return HttpResponseRedirect(reverse('ups:pick_ticket_detail',args=[ups_pkt_id,]))
    # if a GET (or any other method) we'll create a blank form
    else:
        form=FileNameForm()
    return render(request, 'ups/file_selection.html', {'form': form})