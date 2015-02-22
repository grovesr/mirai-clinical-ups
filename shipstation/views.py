from django.shortcuts import render
from ssapi import ssapi
from django.conf import settings
from django.core.urlresolvers import reverse
import datetime
from shipstation.models import parse_orders, get_orderIds, parse_shipments, parse_customers, get_shipmentIds, get_customerIds, order_item, parse_datestr_tz, shipment_item,customer, order, shipment
from MiraiDebug.forms import DateSpanQueryForm
from django.http.response import HttpResponseRedirect
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.decorators import login_required
# Create your views here.
def shipstation_get_customers_orders(orderedItems):
    # build a customer dictionary, each one contains a dictionary of skus ordered and how many
    customers={}
    orders={}
    for orderedItem in orderedItems:
        customerKey=(orderedItem['order__order_ship_to_address__name']+"|"+
                    orderedItem['order__order_ship_to_address__street1']+"|"+
                    orderedItem['order__order_ship_to_address__city']+"|"+
                    orderedItem['order__order_ship_to_address__state']+"|"+
                    orderedItem['order__order_ship_to_address__postalCode']
                    )
        try:
            formattedKey=str(int(float(orderedItem['sku'])))
        except:
            formattedKey=orderedItem['sku']
        
        if customerKey not in customers:
            customers[customerKey]={}
        if formattedKey not in customers[customerKey]:
            customers[customerKey][formattedKey]=0
        if customerKey not in orders:
            orders[customerKey]={}
        if orderedItem['order_id'] not in orders[customerKey]:
            orders[customerKey][orderedItem['order_id']]=0
        customers[customerKey][formattedKey]+=1
        orders[customerKey][orderedItem['order_id']]+=1
    # sort customers by number of items ordered
    sortedCustomers = OrderedDict(sorted(customers.items(), key=lambda x: sum(x[1].values()), reverse=True))
    # sort customers by number of orders shipped
    sortedOrders = OrderedDict(sorted(orders.items(), key=lambda x: len(x[1].values()), reverse=True))
    return (sortedCustomers,sortedOrders)

def reorder_ssapi_datestr_to_dbstr(dateString):
    pieces=dateString.split('-')
    return pieces[2]+"-"+pieces[0]+"-"+pieces[1]

@login_required()
def shipstation_customer_download(request, overwrite=False):
    #query the SS API
    ssget=ssapi.get(api_key=settings.SS_API_KEY,api_secret=settings.SS_API_SECRET,api_endpoint=settings.SS_API_ENDPOINT)
    customerIds=[]
    pageNo=1
    morePages=True
    while morePages:
        ssget.customers(page=pageNo)
        if ssget.json()['total']==0:
            break
        morePages=parse_customers(ssget,overwrite=overwrite)
        customerIds+=get_customerIds(ssget)
        pageNo+=1
    return customerIds

@login_required()
def shipstation_shipment_download(request,startDate,stopDate, overwrite=False):
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
        morePages=parse_shipments(ssget,overwrite=overwrite)
        shipmentIds+=get_shipmentIds(ssget)
        pageNo+=1
    return shipmentIds

@login_required()
def shipstation_order_download(request,startDate,stopDate, overwrite=False):
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
            morePages=parse_orders(ssget,storeName,storeId,overwrite=overwrite)
            orderIds+=get_orderIds(ssget)
            pageNo+=1
    return orderIds

@login_required()
def shipstation_home_dates(request,startDate,stopDate,lastOrderDate=None):
    lastShipmentShipDate=shipment.objects.all().order_by('-shipDate').values('shipDate')[0]
    lastShipmentShipDate=lastShipmentShipDate['shipDate']
    if not lastOrderDate:
        lastOrderDate=order.objects.all().order_by('-orderDate').values('orderDate')[0]
        lastOrderDate=lastOrderDate['orderDate']
    now=datetime.datetime.now()
    nowstr=now.strftime('%Y-%m-%dT%H:%M:%S')
    today=parse_datestr_tz(nowstr, now.time().hour,now.time().min)
    addShipmentUpdateButton=False
    if lastShipmentShipDate<today:
        addShipmentUpdateButton=True
    if lastOrderDate<today:
        addOrderUpdateButton=True
    if request.method=="POST":
        dateSpanForm=DateSpanQueryForm(request.POST)
        if dateSpanForm.is_valid():
            startDate=request.POST.get('startDate').replace('/','-')
            stopDate=request.POST.get('stopDate').replace('/','-')
            if request.POST.get('orderDownload'):
                orderIds=shipstation_order_download(request, startDate, stopDate, overwrite=False)
                if len(orderIds)==0:
                    return render(request, 'shipstation/shipstation_home_dates.html', {
                        'error_message': "No orders found for this date range",
                        'shipstation':1,
                        'sshome':1,
                        'startDate':startDate,
                        'stopDate':stopDate,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_home_dates', args=[startDate,stopDate]))
            if request.POST.get('shipmentDownload'):
                shipmentIds=shipstation_shipment_download(request, startDate, stopDate, overwrite=False)
                if len(shipmentIds)==0:
                    return render(request, 'shipstation/shipstation_home_dates.html', {
                        'error_message': "No shipments found for this date range",
                        'shipstation':1,
                        'sshome':1,
                        'startDate':startDate,
                        'stopDate':stopDate,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_home_dates', args=[startDate,stopDate]))
            if request.POST.get('shipmentLatestDownload'):
                shipStartDate=lastShipmentShipDate.strftime('%m-%d-%Y')
                shipStopDate=now.strftime('%m-%d-%Y')
                shipmentIds=shipstation_shipment_download(request, shipStartDate, shipStopDate, overwrite=False)
                if len(shipmentIds)==0:
                    return render(request, 'shipstation/shipstation_home_dates.html', {
                        'error_message': "No shipments found for this date range",
                        'shipstation':1,
                        'sshome':1,
                        'startDate':shipStartDate,
                        'stopDate':shipStopDate,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_home_dates', args=[startDate,stopDate]))
            if request.POST.get('orderLatestDownload'):
                orderStartDate=lastOrderDate.strftime('%m-%d-%Y')
                orderStopDate=now.strftime('%m-%d-%Y')
                orderIds=shipstation_order_download(request, orderStartDate, orderStopDate, overwrite=False)
                if len(orderIds)==0:
                    return render(request, 'shipstation/shipstation_home_dates.html', {
                        'error_message': "No orders found for this date range",
                        'shipstation':1,
                        'sshome':1,
                        'startDate':orderStartDate,
                        'stopDate':orderStopDate,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_home_dates', args=[startDate,stopDate]))
            if request.POST.get('skuReport'):
                # query the local database for SKUs
                return HttpResponseRedirect(reverse('shipstation:shipstation_sku_report', args=[startDate,stopDate]))
            if request.POST.get('customerReport'):
                # query the local database for Customers
                return HttpResponseRedirect(reverse('shipstation:shipstation_customer_report',
                                            args=[startDate,stopDate]))
            if request.POST.get('customerDownload'):
                customerIds=shipstation_customer_download(request, overwrite=True)
                if len(customerIds)==0:
                    return render(request, 'shipstation/shipstation_home.html', {
                        'error_message': "No customers found",
                        'shipstation':1,
                        'sshome':1,
                        'startDate':startDate,
                        'stopDate':stopDate,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_home_dates', args=[startDate,stopDate]))
            if request.POST.get('customerLatestDownload'):
                customerIds=shipstation_customer_download(request, overwrite=False)
                if len(customerIds)==0:
                    return render(request, 'shipstation/shipstation_home.html', {
                        'error_message': "No customers found",
                        'shipstation':1,
                        'sshome':1,
                        'startDate':startDate,
                        'stopDate':stopDate,
                    })
                return HttpResponseRedirect(reverse('shipstation:shipstation_home_dates', args=[startDate,stopDate]))
    else:
        dateSpanForm=DateSpanQueryForm()
    return render(request,'shipstation/shipstation_home.html', {'dateSpanForm':dateSpanForm,
                                                                   'shipstation':1,
                                                                   'sshome':1,
                                                                   'lastOrderDate':lastOrderDate,
                                                                   'addOrderUpdateButton':addOrderUpdateButton,
                                                                   'lastShipmentShipDate':lastShipmentShipDate,
                                                                   'addShipmentUpdateButton':addShipmentUpdateButton,
                                                                    'startDate':startDate,
                                                                    'stopDate':stopDate,})

@login_required()
def shipstation_home(request):
    lastOrderDate=order.objects.all().order_by('-orderDate').values('orderDate')[0]
    startDate=lastOrderDate['orderDate'].strftime('%m-%d-%Y')
    stopDate=lastOrderDate['orderDate'].strftime('%m-%d-%Y')
    return shipstation_home_dates(request,startDate,stopDate,lastOrderDate=lastOrderDate['orderDate'])


@login_required()
def shipstation_sku_report(request,startDate,stopDate):
    
    parsedStartDate=parse_datestr_tz(reorder_ssapi_datestr_to_dbstr(startDate),0,0)
    parsedStopDate=parse_datestr_tz(reorder_ssapi_datestr_to_dbstr(stopDate),23,59)
    orderItems=order_item.objects.filter(order__shipDate__lte=parsedStopDate,
                                          order__shipDate__gte=parsedStartDate,
                                          order__orderStatus__contains='shipped')
    shipmentItems=shipment_item.objects.filter(shipment__shipDate__lte=parsedStopDate,
                                          shipment__shipDate__gte=parsedStartDate,shipment__voided=0)
    skus={}
    # ordered and shipped items
    for orderItem in orderItems:
        try:
            formattedKey=str(int(float(orderItem.sku)))
        except:
            formattedKey=orderItem.sku
        if orderItem.sku in skus:
            skus[formattedKey][0]+=1
        else:
            skus[formattedKey]=[1,0]
    totalShippedSkus=0
    # shipped items
    for shipmentItem in shipmentItems:
        try:
            formattedKey=str(int(float(shipmentItem.sku)))
        except:
            formattedKey=shipmentItem.sku
        if shipmentItem.sku in skus:
            skus[formattedKey][1]+=1
            totalShippedSkus+=1
    sortedSkus = OrderedDict(sorted(skus.items(), key=lambda x: x[1][0], reverse=True))
    
    return render(request,'shipstation/shipstation_sku_report.html',
                  {'shipstation':1,'startDate':startDate,
                   'stopDate':stopDate,'skus':sortedSkus,
                   'totalShippedSkus':totalShippedSkus})
    
@login_required()
def shipstation_customer_report(request,startDate,stopDate):
    parsedStartDate=parse_datestr_tz(reorder_ssapi_datestr_to_dbstr(startDate),0,0)
    parsedStopDate=parse_datestr_tz(reorder_ssapi_datestr_to_dbstr(stopDate),23,59)
    # ordered items
    orderedItems=order_item.objects.filter(
                                order__orderDate__gte=parsedStartDate,
                                order__orderDate__lte=parsedStopDate,
                                order__orderStatus='shipped').values(
                                'order_id','sku','quantity','name',
                                'order__order_ship_to_address__name',
                                'order__order_ship_to_address__street1',
                                'order__order_ship_to_address__city',
                                'order__order_ship_to_address__state',
                                'order__order_ship_to_address__postalCode')
    # build a customer dictionary, each one contains a dictionary of skus ordered and how many
    sortedCustomers,sortedOrders=shipstation_get_customers_orders(orderedItems)
    # top 10 customers
    top={}
    multipleOrders=0
    totalOrders=order.objects.filter(
                                orderDate__gte=parsedStartDate,
                                orderDate__lte=parsedStopDate,
                                orderStatus='shipped').count()
    totalCustomers=len(sortedCustomers)
    for customerItem in sortedCustomers.items():
        # only add to the list if this customer ordered more than one item
        if len(sortedOrders[customerItem[0]].values()) < 2:
            continue
        else:
            multipleOrders+=1
        customerName,customerStreet1,customerCity,customerState,customerZip=customerItem[0].split('|')
        try:
            # try to get the customer ID if possible
            thisCustomer=customer.objects.get(name__icontains=customerName,
                                          street1__icontains=customerStreet1,
                                          city__icontains=customerCity,
                                          state__icontains=customerState,
                                          postalCode__icontains=customerZip)
            custId=thisCustomer.customerId
        except (ObjectDoesNotExist,MultipleObjectsReturned):
            custId=custId=customerName+" "+customerStreet1+" "+customerCity+" "+customerState+" "+customerZip 
        sortedSkus = OrderedDict(sorted(customerItem[1].items(), key=lambda x: x[1], reverse=True))
        top[customerName+":"+str(custId)+"(orders:"+str(len(sortedOrders[customerItem[0]].values()))+", items:"+str(sum(sortedSkus.values()))+")"]=sortedSkus
    sortedTop = OrderedDict(sorted(top.items(), key=lambda x: sum(x[1].values()), reverse=True))
    return render(request,'shipstation/shipstation_customer_report.html',
                  {'shipstation':1,
                   'top':sortedTop,
                   'totalOrders':totalOrders,
                   'totalCustomers':totalCustomers,
                   'multipleOrders':multipleOrders,
                   'startDate':startDate,
                   'stopDate':stopDate})
    
