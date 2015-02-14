from django.shortcuts import render
from ssapi import ssapi
from django.conf import settings
from django.core.urlresolvers import reverse
from shipstation.models import parse_orders, get_orderIds, parse_shipments, get_shipmentIds, order_item, parse_datestr_tz, shipment_item
from MiraiDebug.forms import DateSpanQueryForm
from django.http.response import HttpResponseRedirect
from collections import OrderedDict
# Create your views here.

def reorder_ssapi_datestr_to_dbstr(dateString):
    pieces=dateString.split('-')
    return pieces[2]+"-"+pieces[0]+"-"+pieces[1]

def shipstation_shipment_download(request,startDate,stopDate):
    #query the SS API
    ssget=ssapi.get(api_key=settings.SS_API_KEY,api_secret=settings.SS_API_SECRET,api_endpoint=settings.SS_API_ENDPOINT)
    shipmentIds=[]
    pageNo=1
    morePages=True
    while morePages:
        ssget.shipments(shipDateStart=startDate,shipdateDateEnd=stopDate,
                     includeShipmentItems='true',page=pageNo)
        if ssget.json()['total']==0:
            break
        morePages=parse_shipments(ssget)
        shipmentIds+=get_shipmentIds(ssget)
        pageNo+=1
    return shipmentIds

def shipstation_order_download(request,startDate,stopDate):
    #query the SS API
    ssget=ssapi.get(api_key=settings.SS_API_KEY,api_secret=settings.SS_API_SECRET,api_endpoint=settings.SS_API_ENDPOINT)
    ssget.stores()
    stores={}
    for store in ssget.json():
        stores[store['storeName']]=store['storeId']
    orderIds=[]
    for storeName,storeId in stores.iteritems():
        #if storeName=='Amazon' or storeName=='Mirai Clinical':
        #    continue;
        pageNo=1
        morePages=True
        print 'getting orders for store '+storeName
        while morePages:
            ssget.orders(orderDateStart=startDate,orderDateEnd=stopDate,
                         storeId=storeId,page=pageNo)
            if ssget.json()['total']==0:
                break
            morePages=parse_orders(ssget,storeName,storeId)
            orderIds+=get_orderIds(ssget)
            pageNo+=1
    return orderIds

def shipstation_home(request):
    if request.method=="POST":
        dateSpanForm=DateSpanQueryForm(request.POST)
        if dateSpanForm.is_valid():
            startDate=request.POST.get('startDate').replace('/','-')
            stopDate=request.POST.get('stopDate').replace('/','-')
            if request.POST.get('orderDownload'):
                orderIds=shipstation_order_download(request, startDate, stopDate)
                if len(orderIds)==0:
                    return render(request, 'shipstation/shipstation_home.html', {
                        'error_message': "No orders found for this date range",
                        'shipstation':1,
                        'sshome':1,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_reports', args=[startDate,stopDate]))
            if request.POST.get('reports'):
                return HttpResponseRedirect(reverse('shipstation:shipstation_reports', args=[startDate,stopDate]))
            if request.POST.get('shipmentDownload'):
                shipmentIds=shipstation_shipment_download(request, startDate, stopDate)
                if len(shipmentIds)==0:
                    return render(request, 'shipstation/shipstation_home.html', {
                        'error_message': "No shipments found for this date range",
                        'shipstation':1,
                        'sshome':1,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_reports', args=[startDate,stopDate]))
    else:
        dateSpanForm=DateSpanQueryForm()
    return render(request,'shipstation/shipstation_home.html', {'dateSpanForm':dateSpanForm,
                                                                   'shipstation':1,
                                                                   'sshome':1,})

def shipstation_sku_report(request,startDate,stopDate):
    
    #TODO: now query the database to get the sku information
    parsedStartDate=parse_datestr_tz(reorder_ssapi_datestr_to_dbstr(startDate),0,0)
    parsedStopDate=parse_datestr_tz(reorder_ssapi_datestr_to_dbstr(stopDate),23,59)
    orderItems=order_item.objects.filter(order__orderDate__lte=parsedStopDate,
                                          order__orderDate__gte=parsedStartDate).exclude(
                                        order__orderStatus__contains='cancelled')
    shipmentItems=shipment_item.objects.filter(shipment__shipDate__lte=parsedStopDate,
                                          shipment__shipDate__gte=parsedStartDate).exclude(
                                        shipment__voided=1)
    skus={}
    for orderItem in orderItems:
        try:
            formattedKey=str(int(float(orderItem.sku)))
        except:
            formattedKey=orderItem.sku
        if orderItem.sku in skus:
            skus[formattedKey][0]+=1
        else:
            skus[formattedKey]=[1,0]
    for shipmentItem in shipmentItems:
        try:
            formattedKey=str(int(float(shipmentItem.sku)))
        except:
            formattedKey=shipmentItem.sku
        if shipmentItem.sku in skus:
            skus[formattedKey][1]+=1
    sortedSkus = OrderedDict(sorted(skus.items(), key=lambda x: x[1][0], reverse=True))
    return render(request,'shipstation/shipstation_sku_report.html',
                  {'shipstation':1,'startDate':startDate,
                   'stopDate':stopDate,'skus':sortedSkus})

def shipstation_reports(request,startDate,stopDate):
    if request.method == 'POST':
        if request.POST.get('skuQuery'):
            # query the local database for SKUs
            return HttpResponseRedirect(reverse('shipstation:shipstation_sku_report', args=[startDate,stopDate]))
    return render(request,'shipstation/shipstation_reports.html',{
                                                                   'shipstation':1,
                                                                   'startDate':startDate,
                                                                   'stopDate':stopDate
                                                                   })
