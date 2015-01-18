from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from ups.models import mirai_check_args, mirai_initialize_ups_pkt, PickTicket, PH, PD
from ups.forms import FileNameForm, PhForm, PdForm, TitleErrorList
from django.forms.models import inlineformset_factory, modelform_factory

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

def pick_ticket_edit_ph(request, pk):
    try:
        ups_ph=PH.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_edit_ph.html', {'error_message':'PickTicket PH '+str(pk)+' doesn''t exist',})
    phFields=['SHIPTO_NAME','PH1_CUST_PO_NBR',]
    PdInlineFormset=inlineformset_factory(PH, PD, extra=0, form=PdForm)
    PhForm=modelform_factory(PH,fields=phFields)
    #pktForm=PickTicketForm(instance=ups_pkt)
    if request.method == "POST":
        phForm=PhForm(request.POST,instance=ups_ph, error_class=TitleErrorList)
        pdForms=PdInlineFormset(request.POST,instance=ups_ph, error_class=TitleErrorList)
        if pdForms.is_valid() and phForm.is_valid():
            #formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(ups_ph.get_absolute_url())
    else:
        phForm=PhForm(ups_ph.__dict__,instance=ups_ph, error_class=TitleErrorList)
        pdForms=PdInlineFormset(instance=ups_ph, error_class=TitleErrorList)
    return render(request,"ups/pick_ticket_edit_ph.html", {
        "ups_ph":ups_ph, "phForm":phForm, "pdForms": pdForms,
    })

def pick_ticket_edit(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_edit.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist',})
    pktFields=['DOC_DATE','fileName']
    PhInlineFormset=inlineformset_factory(PickTicket,PH,extra=0, form=PhForm)
    PickTicketForm=modelform_factory(PickTicket,fields=pktFields)
    #pktForm=PickTicketForm(instance=ups_pkt)
    if request.method == "POST":
        pktForm=PickTicketForm(request.POST,instance=ups_pkt, error_class=TitleErrorList)
        phForms=PhInlineFormset(request.POST,instance=ups_pkt, error_class=TitleErrorList)
        if phForms.is_valid() and pktForm.is_valid():
            #formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(ups_pkt.get_absolute_url())
    else:
        pktForm=PickTicketForm(ups_pkt.__dict__,instance=ups_pkt, error_class=TitleErrorList)
        phForms=PhInlineFormset(instance=ups_pkt, error_class=TitleErrorList)
    return render(request,"ups/pick_ticket_edit.html", {
        "ups_pkt":ups_pkt, "pktForm":pktForm, "phForms": phForms,
    })

def pick_ticket_file_report(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_file_report.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist'})
    return render(request,'ups/pick_ticket_file_report.html', {'ups_pkt':ups_pkt})

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