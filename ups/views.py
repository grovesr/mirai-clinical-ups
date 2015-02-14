from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from ssapi import ssapi
from django.conf import settings
from shipstation.models import parse_orders, get_orderIds
from ups.models import mirai_check_args, mirai_init_ups_pkt_from_file,mirai_init_ups_pkt_from_ssapi, PickTicket, PH, PD
from ups.forms import FileNameForm, PhForm, PdForm, TitleErrorList
from MiraiDebug.forms import DateSpanQueryForm
from django.forms.models import inlineformset_factory, modelform_factory

# helper functions
def bind_formset(formset):
    """
    Bind initial data to a formset
    """
    if formset.is_bound:
        # do nothing if the formset is already bound
        return formset
    
    bindData={}
    # the formset.get_default_prefix() and form.add_prefix() methods add in the 
    # dict keys that uniquely identify the various form fields with the individual 
    # instance data
    
    # add formset management form data
    bindData[formset.get_default_prefix()+"-TOTAL_FORMS"]=str(formset.management_form['TOTAL_FORMS'].value())
    bindData[formset.get_default_prefix()+"-INITIAL_FORMS"]=str(formset.management_form['INITIAL_FORMS'].value())
    bindData[formset.get_default_prefix()+"-MIN_NUM_FORMS"]=str(formset.management_form['MIN_NUM_FORMS'].value())
    bindData[formset.get_default_prefix()+"-MAX_NUM_FORMS"]=str(formset.management_form['MAX_NUM_FORMS'].value())
    for form in formset:
        if form.instance:
            # field data, get these values from the instance
            for fieldName,fieldValue in form.fields.iteritems():
                try:
                    bindData[form.add_prefix(fieldName)]=getattr(form.instance,
                                                                 fieldName)
                except AttributeError:
                    # this is an added field (i.e. DELETE), not derived from the
                    # model, do nothing with it, since we are only binding instance
                    # data to the form
                    pass
            # hidden field data, get these from the field initial values set
            # when the form was created
            for field in form.hidden_fields():
                bindData[form.add_prefix(field.name)]=field.field.initial
    # create a new bound formset by passing in the bindData dict, this looks
    # to the formset constructor like a request.POST dict 
    newFormset=formset.__class__(bindData,instance=formset.instance,
                                 error_class=formset.error_class)
    return newFormset

# Create your views here.

def ups_home(request):
    return render(request,'ups/ups_home.html',{'ups':1})

def blank(request):
    return render(request,'base/blank.html')

def pick_ticket_detail(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_detail.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist'})
    if request.method == "POST":
        if 'Delete' in request.POST:
            ups_pkt.delete()
            return HttpResponseRedirect(reverse('ups:pick_ticket_index'))
    return render(request,'ups/pick_ticket_detail.html', {'ups_pkt':ups_pkt,
                                                          "ups":1,
                                                          "picktickets":1,})

def pick_ticket_edit_ph(request, pk):
    try:
        ups_ph=PH.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_edit_ph.html', {'error_message':'PickTicket PH '+str(pk)+' doesn''t exist',})
    PdInlineFormset=inlineformset_factory(PH, PD, extra=0, form=PdForm)
    pdQuerySet=ups_ph.pd_set
    #pktForm=PickTicketForm(instance=ups_pkt)
    if request.method == "POST":
        pdForms=PdInlineFormset(request.POST,instance=ups_ph, queryset=pdQuerySet, error_class=TitleErrorList)
        if pdForms.is_valid():
            pdForms.save()
            return HttpResponseRedirect(reverse('ups:pick_ticket_edit_ph',
                                                args=[ups_ph.id,]),{"ups":1,
                                                "picktickets":1,
                                                })
    else:
        pdForms=PdInlineFormset(instance=ups_ph, error_class=TitleErrorList)
        pdForms=bind_formset(pdForms)
        # set errors if any
    if pdForms.is_valid():
        warning_message="No errors"
    else:
        warning_message="Errors found, fix items highlighted in red before saving"
    return render(request,"ups/pick_ticket_edit_ph.html", {"ups_ph":ups_ph,
                                                           "ups":1,
                                                           "picktickets":1,
                "pdForms": pdForms,"warning_message":warning_message,
    })

def pick_ticket_edit(request, pk):
    try:
        ups_pkt=PickTicket.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request,'ups/pick_ticket_edit.html', {'error_message':'PickTicket '+str(pk)+' doesn''t exist',})
    pktFields=['DOC_DATE','fileName']
    PhInlineFormset=inlineformset_factory(PickTicket,PH,extra=0, form=PhForm)
    PickTicketForm=modelform_factory(PickTicket,fields=pktFields)
    if request.method == "POST":
        pktForm=PickTicketForm(request.POST,instance=ups_pkt, error_class=TitleErrorList)
        phForms=PhInlineFormset(request.POST,instance=ups_pkt, error_class=TitleErrorList)
        if 'Save' in request.POST:
            if phForms.is_valid() and pktForm.is_valid():
                phForms.save()
                pktForm.save()
                return HttpResponseRedirect(reverse('ups:pick_ticket_edit',args=[ups_pkt.id,]),
                                                {"ups":1,
                                                "picktickets":1,
                                                })
        if 'Delete' in request.POST:
            ups_pkt.delete()
            return HttpResponseRedirect(reverse('ups:pick_ticket_index'))
    else:
        pktForm=PickTicketForm(ups_pkt.__dict__,instance=ups_pkt, error_class=TitleErrorList)
        phForms=PhInlineFormset(instance=ups_pkt, error_class=TitleErrorList)
        phForms=bind_formset(phForms)
        # set errors if any
    if pktForm.is_valid() and phForms.is_valid() and ups_pkt.num_ph_errors() == 0:
        warning_message="No errors"
    else:
        warning_message="Errors found, fix items highlighted in red before saving"
    return render(request,"ups/pick_ticket_edit.html", {
        "ups_pkt":ups_pkt, "pktForm":pktForm, "phForms": phForms,
        'ups':1,'picktickets':1,
        "warning_message":warning_message,
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
                return render(request, 'ups/pick_ticket_index.html', {
                    'error_message': "No files selected.",
                    "ups":1,
                    "picktickets":1,
                })
            inputType=mirai_check_args(files)
            if  inputType== -1:
                return render(request, 'ups/pick_ticket_index.html', {
                    'error_message': "Problem with the files.",
                    "ups":1,
                    "picktickets":1,
                })
            upsPktId=mirai_init_ups_pkt_from_file(files,inputType)
            if upsPktId == -1:
                return render(request, 'ups/pick_ticket_index.html', {
                    'error_message': "Problem with the files.",
                    "ups":1,
                    "picktickets":1,
                })
            #
            # redirect to a new URL:)
            return HttpResponseRedirect(reverse('ups:pick_ticket_detail',args=[upsPktId,]),
                                        {"ups":1,
                                        "picktickets":1,
                                         })
    # if a GET (or any other method) we'll create a blank form
    else:
        form=FileNameForm()
        errorMessage=""
        if pkt_list.count()==0:
            errorMessage="No PickTickets"
    return render(request, 'ups/pick_ticket_index.html', {'form': form,
                                                          'pkt_list':pkt_list,
                                                          'ups':1,
                                                          'picktickets':1,
                                                          'error_message':errorMessage,})
    
    
    if len(pkt_list)==0:
        return render(request,'ups/pick_ticket_index.html', {'error_message':'No PickTickets to display'})
    return render(request,'ups/pick_ticket_index.html', {'pkt_list':pkt_list})

def pick_ticket_from_ssapi(request):
    if request.method=="POST":
        dateSpanForm=DateSpanQueryForm(request.POST)
        if dateSpanForm.is_valid():
            startDate=request.POST.get('startDate').replace('/','-')
            stopDate=request.POST.get('stopDate').replace('/','-')
            ssget=ssapi.get(api_key=settings.SS_API_KEY,api_secret=settings.SS_API_SECRET,api_endpoint=settings.SS_API_ENDPOINT)
            ssget.stores()
            stores={}
            for store in ssget.json():
                stores[store['storeName']]=store['storeId']
            orderIds=[]
            for storeName,storeId in stores.iteritems():
                pageNo=1
                morePages=True
                while morePages:
                    ssget.orders(orderDateStart=startDate,orderDateEnd=stopDate,
                                 orderStatus='awaiting_shipment',storeId=storeId,page=pageNo)
#                     ssget.orders(orderDateStart=startDate,orderDateEnd=stopDate,
#                                  storeId=storeId,page=pageNo)
                    if ssget.json()['total']==0:
                        break
                    print ssget.json()['total']
                    morePages=parse_orders(ssget,storeName,storeId)
                    orderIds+=get_orderIds(ssget)
            if len(orderIds)==0:
                return render(request, 'ups/pick_ticket_from_ssapi.html', {
                    'error_message': "No orders found awaiting shipment for this date range",
                    'dateSpanForm':dateSpanForm,
                    "ups":1,
                    "picktickets":1,
                })
            upsPktId=mirai_init_ups_pkt_from_ssapi(ssget,orderIds)
            if upsPktId == -1:
                return render(request, 'ups/pick_ticket_from_ssapi.html', {
                    'error_message': "Problem with the ssapi API call.",
                    'dateSpanForm':dateSpanForm,
                    "ups":1,
                    "picktickets":1,
                })
            return HttpResponseRedirect(reverse('ups:pick_ticket_detail',args=[upsPktId,]),
                                        {
                                         'dateSpanForm':dateSpanForm,
                                        "ups":1,
                                        "picktickets":1,})
    else:
        dateSpanForm=DateSpanQueryForm()
    return render(request,'ups/pick_ticket_from_ssapi.html', {'dateSpanForm':dateSpanForm,
                                                              "ups":1,
                                                              "picktickets":1,})
