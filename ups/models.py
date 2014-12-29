from django.db import models
import urllib2
import re
from django.utils import timezone
import time
import random
import os, sys
import xlrd

def mirai_check_args(args):
    if len(args) < 1:
        raw_input('Please specify a Purchase Order directory, list of Dropbox URLs or list of file(s)\n')
        sys.exit(-1)
    for arg in args:
        "for multiple arguments, assume that all are the same type"
        if os.path.isfile(arg):
            return 1
        if os.path.isdir(arg):
            return 2
        try:
            response = urllib2.urlopen(arg)
            response.close()
            return 3
        except urllib2.HTTPError: # 404, 500, etc..
            pass
    return -1

def mirai_get_files(inputType,args):
    files={}
    if inputType == 1:
        #filenames
        fileNames=args
    if inputType == 2:
        #directory
        # we only handle a single directory, so just pull the first one from args
        fileNames=os.listdir(args[0])
        directory=args[0]
        fileNames=[directory + os.sep + s for s in fileNames]
    if inputType < 3:
        #files or directory
        for poFile in fileNames:
            # don't open directories and hidden files
            reMatch=re.compile(r'(^\..*)|(.*~$)')
            if not os.path.isdir(poFile) and not reMatch.match(poFile):
                try:
                    with open(poFile, 'rt') as fStr:
                        files[fStr.name]=fStr.read()
                except:
                    # failed to open file
                    files[poFile]=['FILE ERROR: unable to open file "' + poFile + '"']
    if inputType == 3:
        # URLs
        for poUrl in args:
            try:
                urlStr = urllib2.urlopen(poUrl)
                files[urlStr.url]=urlStr.read()
            except:
                files[poUrl]=['URL ERROR: unable to open URL "' + poUrl + '"']
    return files

def mirai_initialize_ups_pkt(files,inputType):
    warehouse='SD4'
    company='MIRAI'
    division='001'
    upsShipOrderDir = 'UPS/UpsShipmentOrders'
    timeStamp=time.time()
    fileTimeStamp=timezone.datetime.fromtimestamp(timeStamp).strftime('%y%m%d%H%M%S')
    rand='{:010}'.format(random.randrange(1,999999999,1))
    div='001'
    fileName=upsShipOrderDir+os.sep+warehouse+company+div+'_FF_PICKTIKET_'+rand+'_'+fileTimeStamp
    ups_pkt=PickTicket()
    ups_pkt.DOC_DATE=timezone.datetime.fromtimestamp(timeStamp).strftime('%m/%d/%y %H:%M:%S')
    ups_pkt.warehouse=warehouse
    ups_pkt.CMPY_NAME=company
    ups_pkt.division=division
    ups_pkt.timeStamp='{:08x}'.format(int(timeStamp))
    ups_pkt.fileName=fileName
    ups_pkt.save()
    
    files=mirai_get_files(inputType, files)
    #go through the files and store each row as a CustOrderQueryRow
    for f,contents in files.iteritems():
        fileTimeStamp=timezone.datetime.now()
        header=True
        recordNumber=0
        for fileLine in contents.splitlines():
            thisCo=CustOrderQueryRow()
            if header:
                thisCo.header=True
                header=False
            thisCo.ups_pkt=ups_pkt
            thisCo.record=fileLine
            thisCo.queryRecordNumber=recordNumber
            thisCo.queryId=fileTimeStamp
            thisCo.query=f
            recordNumber+=1
            thisCo.save()
    ups_pkt.read_files()
    return ups_pkt

# Create your models here.
    
class PickTicket(models.Model):
    '''
    UPS Pickticket object
    '''
    SEP=models.CharField(max_length=5, default='|') # record separator
    # HDR section
    HDR_REC_TYPE=models.CharField(max_length=3, default='HDR')              # 3 char
    DOC_TYPE=models.CharField(max_length=10, default='PICKTICKET')           # 10 char
    CMPY_NAME=models.CharField(max_length=20, default='')                    # 20 char
    DOC_DATE=models.CharField(max_length=17, default=timezone.datetime.now().strftime('%m/%d/%y %H:%M:%S'))                     # 17 char MM/DD/YY HH:MM:SS
    # need accessor for TRANS_ID
    # PH section
    # TRL section
    TRL_REC_TYPE=models.CharField(max_length=3, default='TRL')              # 3 char
    #
    parseErrors=models.TextField(default='') # dictionary of various errors related to parsed files
    fileName=models.URLField(default='')
    fileContents=models.TextField(default='')
    
    def __str__(self):
        res = "PickTicket instance:" + self.fileName
        return res
    
    def hdr(self):
        return((self.HDR_REC_TYPE+self.SEP+self.DOC_TYPE+self.SEP+self.CMPY_NAME+self.SEP+
                self.DOC_DATE+self.SEP+self.trans_id()))
        
    def ph(self):
        phStr=''
        for phItem in self.PH:
            phStr+=phItem.ph_item()
        phStr = phStr[:-1]
        return(phStr)
    
    def trl(self):
        return((self.TRL_REC_TYPE+self.SEP+self.DOC_TYPE+self.SEP+self.CMPY_NAME+self.SEP+
                self.DOC_DATE+self.SEP+self.trans_id()+self.SEP+self.rec_count()))
    
    def trans_id(self):
        #return(self.PH[0].CO[:-1]+'1')
        # let GWS populate this
        return('')
    
    def rec_count(self):
        index=0
        for ph in self.PH:
            index += 3  # PH, PH1, PHI
            for pd in ph.PD:
                index+=1 # PD
        # HDR + TRL + pickticket loops + detail loops
        return('{:07}'.format(2+index))
    
    def read_files(self):
        reMatchZen=re.compile('.*v_orders_id.*')
        reMatchAmazon=re.compile('.*buyer-phone-number.*')
        reMatchSS=re.compile('.*pack-slip-type.*')
        #get the distinct queries for this pickTicket instance
        queryIds=CustOrderQueryRow.objects.filter(ups_pkt_id=self.id).values('queryId').distinct()
        for  queryId in queryIds:
            thisQuery=CustOrderQueryRow.objects.filter(queryId=queryId)
            header=thisQuery.filter(header=True)
            #get the query records for this query
            thisQueryRows=thisQuery.filter(header=False)
            for queryRow in thisQueryRows:
                # create a custOrder instance for this queryRow and parse the query data into it
                coIncr=CustOrder()
                coIncr.queryName=thisQuery.query
                coIncr.queryLineNo=thisQuery.queryRecordNumber
                coIncr.read_header(header)
                coIncr.ups_pkt=self
                if reMatchZen.match(header):
                    result=coIncr.read_zen_line(queryRow.record.rstrip())
                if reMatchSS.match(header):
                    result=coIncr.read_ss_line(queryRow.record.rstrip())
                if reMatchAmazon.match(header):
                    result=coIncr.read_amazon_line(queryRow.record.rstrip())
                
                if result < 0:
                    # improperly formatted record
                    queryRow.parseError='PARSE ERROR: improperly formatted line'
                    queryRow.save()
                coIncr.save()
        self.parse_po_objects()
        
    def parse_po_objects(self):
        phIndex=0
        itemIndex=0
        #find all distinct orderIds
        orderIds=CustOrder.objects.filter(ups_pkt=self.id).values('orderId').distinct()
        #for each order line within a unique orderId (may consist of multiple order lines)
        for orderId in orderIds:
            coLines=CustOrder.filter(pk=orderId)
            #for each custOrder line with a given unique orderId
            for coLine in coLines:
                phIndex+=2
                phItem=PH()
                phItem.WHSE=self.warehouse
                phItem.CO=self.CMPY_NAME
                phItem.DIV=self.division
                phItem.STAT_CODE='10'
                phItem.PKT_PROFILE_ID=self.PKT_PROFILE_ID
                phItem.PKT_CTRL_NBR='MC'+self.timeStamp
                phItem.LANG_ID='EN'
                phItem.PH1_FREIGHT_TERMS='0'
                phItem.PHI_SPL_INSTR_NBR='{:03}'.format(phIndex)
                phItem.PHI_SPL_INSTR_TYPE='QV'
                phItem.PHI_SPL_INSTR_CODE='01,08'
                phItem.ups_pkt=self.id
                if phItem.parse(coLine) < 0:
                    # unable to create a PH object from this. Append to any errors already 
                    coLine.parseError='PARSE ERROR: Unable to create PH item: from CustOrder'
                    coLine.save()
                else:
                    itemIndex+=1
                    phItem.add_detail(itemIndex,coLine)
                    lineError=phItem.check_line()
                    if lineError != '':
                        # some missing information in this line item, generate an error
                        coLine.parseError.append(lineError)
                        coLine.save()
                    phItem.save()
    
    def parse_report(self):
        fileErrors=[]
        lineParseErrors=[]
        reportStr='Report for file "'+self.fileName+'.txt"\n\n'
        for key,value in self.parseErrors.iteritems():
            for errorLine in value:
                if re.split(r':',errorLine)[0] == 'FILE ERROR':
                    fileErrors.append(errorLine)
                if re.split(r':',errorLine)[0] == 'PARSE ERROR':
                    fileErrors.append(errorLine)
                if re.split(r':',errorLine)[0] == 'URL ERROR':
                    fileErrors.append(errorLine)
        for fileError in fileErrors:
            reportStr+=fileError+'\n'
        reportStr+='\n'
        for lineParseError in lineParseErrors:
            reportStr+=lineParseError+'\n'
        reportStr+='\n'
        for phItem in self.PH:
            reportStr+='Customer: '+phItem.SHIPTO_NAME+'\n'
            reportStr+='\tFile: '+phItem.fromFile+'\n'
            reportStr+='\tDate: '+phItem.PH1_ORD_DATE+'\n'
            reportStr+='\tOrder #: '+phItem.PH1_CUST_PO_NBR+'\n'
            reportStr+='\tAddress:\n'
            reportStr+='\t\t'+phItem.SHIPTO_ADDR_1+'\n'
            if phItem.SHIPTO_ADDR_2 != "":
                reportStr+='\t\t'+phItem.SHIPTO_ADDR_2+'\n'
            if phItem.SHIPTO_ADDR_3 != "":
                reportStr+='\t\t'+phItem.SHIPTO_ADDR_3+'\n'
            reportStr+='\t\t'+phItem.SHIPTO_CITY+', '+phItem.SHIPTO_STATE+', '+phItem.SHIPTO_ZIP+', '+phItem.SHIPTO_CNTRY+'\n'
            reportStr+='\tItems:\n'
            for pdItem in phItem.PD:
                reportStr+='\t\t('+pdItem.ORIG_ORD_QTY+') '+pdItem.SIZE_DESC+' (SKU:'+pdItem.CUST_SKU+', file line #: '+str(pdItem.fileLineNo)+')\n'
            reportStr+='\n'
        return(reportStr)
    
    def parse_pkt_report(self):
        fileErrors=[]
        lineParseErrors=[]
        reportStr='Report for file "'+self.fileName+'.txt"\n\n'
        for key,value in self.parseErrors.iteritems():
            for errorLine in value:
                if re.split(r':',errorLine)[0] == 'FILE ERROR':
                    fileErrors.append(errorLine)
                if re.split(r':',errorLine)[0] == 'PARSE ERROR':
                    fileErrors.append(errorLine)
                if re.split(r':',errorLine)[0] == 'URL ERROR':
                    fileErrors.append(errorLine)
        for fileError in fileErrors:
            reportStr+=fileError+'\n'
        reportStr+='\n'
        for lineParseError in lineParseErrors:
            reportStr+=lineParseError+'\n'
        reportStr+='\n'
        for phItem in self.PH:
            reportStr+='Customer: '+phItem.SHIPTO_NAME+'\n'
            reportStr+='\tAddress:\n'
            reportStr+='\t\t'+phItem.SHIPTO_ADDR_1+'\n'
            if phItem.SHIPTO_ADDR_2 != "":
                reportStr+='\t\t'+phItem.SHIPTO_ADDR_2+'\n'
            if phItem.SHIPTO_ADDR_3 != "":
                reportStr+='\t\t'+phItem.SHIPTO_ADDR_3+'\n'
            reportStr+='\t\t'+phItem.SHIPTO_CITY+', '+phItem.SHIPTO_STATE+', '+phItem.SHIPTO_ZIP+', '+phItem.SHIPTO_CNTRY+'\n'
            reportStr+='\tPH1_CUST_PO_NBR: '+phItem.PH1_CUST_PO_NBR+'\n'
            reportStr+='\tSHIP_VIA: '+phItem.SHIP_VIA+'\n'
            reportStr+='\tORD_TYPE: '+phItem.ORD_TYPE+'\n'
            reportStr+='\tPKT_CNTRL_NBR: '+phItem.PKT_CTRL_NBR+'\n'
            reportStr+='\tPH1_PROD_VALUE: '+phItem.PH1_PROD_VALUE+'\n'
            reportStr+='\tPH1_FREIGHT_TERMS: '+phItem.PH1_FREIGHT_TERMS+'\n'
            for code in phItem.PHI_SPL_INSTR_CODE:
                reportStr+='\tPHI_SPL_INSTR_CODE: '+code+'\n'
            reportStr+='\tPHI_SPL_INSTR_DESC: '+phItem.PHI_SPL_INSTR_DESC+'\n'
            reportStr+='\tItems:\n'
            for pdItem in phItem.PD:
                reportStr+='\t\tPKT_SEQ_NBR: '+pdItem.PKT_SEQ_NBR+'\n'
                reportStr+='\t\tORIG_ORD_QTY: '+pdItem.ORIG_ORD_QTY+'\n'
                reportStr+='\t\tPKT_ORD_QTY: '+pdItem.ORIG_PKT_QTY+'\n'
                reportStr+='\t\tCUST_SKU: '+pdItem.CUST_SKU+'\n\n'
            reportStr+='\n'
        return(reportStr)
    
class CustOrderQueryRow(models.Model):
    """
    UPS Customer Order Query
    There may be ,multiple records for a given query
    Each record consists of a TextField with delimeter separated values
    Query may be a filename, URL, or web service call
    QueryId is the unique timestamp that ties together the query rows for a given query
    Sep gives a clue to how to parse the record
    Header is a True/False indicator of whether this is a header record or not.
    A header record will provide the field names for the other record lines for a given query
    parseError holds any errors generated when parsing information out of the row 
    """
    ups_pkt = models.ForeignKey(PickTicket)
    query=models.CharField(max_length=1024, default='')
    queryId=models.DateTimeField(default=timezone.datetime.now())
    queryRecordNumber=models.IntegerField(default=0)
    record=models.TextField(default='')
    header=models.BooleanField(default=False)
    parseError=models.TextField(default='')
    
    
class PH(models.Model):
    '''
    UPS Pickticket Loop, contained in a PickTicket (Shipment Order)
    '''
    SEP=models.CharField(max_length=1,default='|') # record separator
    itemIndex = models.IntegerField(default=0)
    ups_pkt=models.ForeignKey(PickTicket)
    REC_TYPE=models.CharField(max_length=2,default='PH')                   # 2 char
    WHSE=models.CharField(max_length=3,default='')                         # 3 char
    CO=models.CharField(max_length=10,default='')                          # 10 char
    DIV=models.CharField(max_length=10,default='')                         # 10 char
    STAT_CODE=models.CharField(max_length=2,default='10')                  # 2 char
    PKT_PROFILE_ID=models.CharField(max_length=10,default='')              # 10 char
    PKT_CTRL_NBR=models.CharField(max_length=10,default='')                # 10 char
    PKT_NBR=models.CharField(max_length=11,default='',blank=True)           # opt. 11 char
    PKT_SFX=models.CharField(max_length=3,default='',blank=True)            # opt. 3 char
    ORD_NBR=models.CharField(max_length=3,default='',blank=True)            # opt. 3 char
    ORD_SFX=models.CharField(max_length=3,default='',blank=True)            # opt. 3 char
    ORD_TYPE=models.CharField(max_length=2,default='',blank=True)           #opt. 2 char
    SHIPTO=models.CharField(max_length=10,default='',blank=True)            # opt 10 char
    SHIPTO_NAME=models.CharField(max_length=35,default='')                 # 35 characters
    SHIPTO_CONTACT=models.CharField(max_length=30,default='')              # 30 characters
    SHIPTO_ADDR_1=models.CharField(max_length=75,default='',blank=True)     # opt. 75 char
    SHIPTO_ADDR_2=models.CharField(max_length=75,default='',blank=True)     # opt. 75 char
    SHIPTO_ADDR_3=models.CharField(max_length=75,default='',blank=True)     # opt. 75 char
    SHIPTO_CITY=models.CharField(max_length=40,default='',blank=True)       # opt. 40 char
    SHIPTO_STATE=models.CharField(max_length=3,default='',blank=True)       # opt. 3 char
    SHIPTO_ZIP=models.CharField(max_length=11,default='',blank=True)        # opt. 11 char
    SHIPTO_CNTRY=models.CharField(max_length=4,default='',blank=True)       # opt. 4 char
    TEL_NBR=models.CharField(max_length=15,default='',blank=True)           # opt. 15 char
    SOLDTO=models.CharField(max_length=10,default='',blank=True)            # opt. 10 char
    SOLDTO_NAME=models.CharField(max_length=35,default='',blank=True)       # opt. 35 char
    SOLDTO_ADDR_1=models.CharField(max_length=75,default='',blank=True)     # opt. 75 char
    SOLDTO_ADDR_2=models.CharField(max_length=75,default='',blank=True)     # opt. 75 char
    SOLDTO_ADDR_3=models.CharField(max_length=75,default='',blank=True)     # opt. 75 char
    SOLDTO_CITY=models.CharField(max_length=40,default='',blank=True)       # opt. 40 char
    SOLDTO_STATE=models.CharField(max_length=3,default='',blank=True)       # opt. 3 char
    SOLDTO_ZIP=models.CharField(max_length=11,default='',blank=True)        # opt. 11 char
    SOLDTO_CNTRY=models.CharField(max_length=4,default='',blank=True)       # opt. 4 char
    SHIP_VIA=models.CharField(max_length=4,default='UUS2',blank=True)       # opt. 4 char (Surepost=UUS2, UPS grnd=UU10)
    CARTON_LABEL_TYPE=models.CharField(max_length=3,default='',blank=True)  # opt. 3 char
    NBR_OF_LABEL=models.CharField(max_length=3,default='',blank=True)       # opt. 3 char
    CONTNT_LABEL_TYPE=models.CharField(max_length=3,default='',blank=True)  # opt. 3 char
    NBR_OF_CONTNT_LABEL=models.CharField(max_length=3,default='',blank=True)# opt. 3 char
    NBR_OF_PAKING_SLIPS=models.CharField(max_length=3,default='',blank=True)# opt. 3 char
    PACK_SLIP_TYPE=models.CharField(max_length=2,default='',blank=True)     # opt. 2 char
    LANG_ID=models.CharField(max_length=3,default='',blank=True)            # opt. 3 char
                                        # opt. PH1 section
    # PH1 section
    PH1_REC_TYPE=models.CharField(max_length=3,default='PH1')                    # 3 char
    PH1_ACCT_RCVBL_ACCT_NBR=models.CharField(max_length=10,default='',blank=True) # opt. 10 char
    PH1_ACCT_RCVBL_CODE=models.CharField(max_length=2,default='',blank=True)      # opt. 2 char
    PH1_CUST_PO_NBR=models.CharField(max_length=26,default='',blank=True)         # opt. 26 char
    PH1_PRTY_CODE=models.CharField(max_length=2,default='',blank=True)            # opt. 2 char
    PH1_PRTY_SFX=models.CharField(max_length=3,default='',blank=True)             # opt. 2 char
    PH1_ORD_DATE=models.CharField(max_length=14,default='',blank=True)            # opt. 14 char MM/DD/YY
    PH1_START_SHIP_DATE=models.CharField(max_length=14,default='',blank=True)     # opt. 14 char MM/DD/YY
    PH1_STOP_SHIP_DATE=models.CharField(max_length=14,default='',blank=True)      # opt. 14 char MM/DD/YY
    PH1_SCHED_DLVRY_DATE=models.CharField(max_length=14,default='',blank=True)    # opt. 14 char MM/DD/YY
    PH1_EARLIEST_DLVRY_TIME=models.CharField(max_length=4,default='',blank=True)  # opt. 4 char 1200??
    PH1_SCHED_DLVRY_DATE_END=models.CharField(max_length=10,default='',blank=True)# opt. 14 char MM/DD/YY
    PH1_RTE_GUIDE_NBR=models.CharField(max_length=10,default='',blank=True)       # opt. 10 char
    PH1_CUST_RTE=models.CharField(max_length=1,default='',blank=True)             # opt. 1 char (Y,N)
    PH1_RTE_ATTR=models.CharField(max_length=30,default='',blank=True)            # opt. 30 char
    PH1_RTE_ID=models.CharField(max_length=10,default='',blank=True)              # opt. 10 char
    PH1_RTE_STOP_SEQ=models.CharField(max_length=5,default='',blank=True)         # opt. 5 char
    PH1_RTE_TO=models.CharField(max_length=10,default='',blank=True)              # opt. 10 char
    PH1_RTE_TYPE_1=models.CharField(max_length=2,default='',blank=True)           # opt. 2 char
    PH1_RTE_TYPE_2=models.CharField(max_length=2,default='',blank=True)           # opt. 2 char
    PH1_RTE_ZIP=models.CharField(max_length=11,default='',blank=True)             # opt. 11 char
    PH1_RTE_SWC_NBR=models.CharField(max_length=10,default='',blank=True)         # opt. 10 char
    PH1_CONSOL_NBR=models.CharField(max_length=10,default='',blank=True)          # opt. 10 char
    PH1_TOTAL_DLRS_UNDISC=models.CharField(max_length=11,default='',blank=True)   # opt. 11 char
    PH1_TOTAL_DLRS_DISC=models.CharField(max_length=11,default='',blank=True)     # opt. 11 char
    PH1_CURR_CODE=models.CharField(max_length=10,default='',blank=True)           # opt. 10 char
    PH1_PROD_VALUE=models.CharField(max_length=11,default='',blank=True)          # opt. 11 char
    PH1_FREIGHT_TERMS=models.CharField(max_length=1,default='',blank=True)        # opt. 1 char 0 = Prepaid (Default),1 = Collect Billing,1 0:1,2 = Consignee Billing.3 = Third Party Billing
    PH1_MARK_FOR=models.CharField(max_length=25,default='',blank=True)            # opt. 25 char
    PH1_INCO_TERMS=models.CharField(max_length=3,default='',blank=True)           # opt. 3 char
    PH1_BILL_ACCT_NBR=models.CharField(max_length=10,default='',blank=True)       # opt. 10 char
    PH1_COD_FUNDS=models.CharField(max_length=1,default='',blank=True)            # OPT. 1 CHAR
    PH1_INTL_GOODS_DESC=models.CharField(max_length=35,default='',blank=True)     # opt. 35 char
    # PHI
    PHI_REC_TYPEE=models.CharField(max_length=3,default='PHI')                   # 3 char
    PHI_SPL_INSTR_NBR=models.CharField(max_length=3,default='')                  # 3 char
    PHI_SPL_INSTR_TYPE=models.CharField(max_length=2,default='')                 # 2 char
    PHI_SPL_INSTR_CODE=models.CommaSeparatedIntegerField(max_length=2,default='08')# 2 char list from: (01=shipment,02=delivery,04=exception,08=delivery failure)
    PHI_SPL_INSTR_DESC=models.CharField(max_length=135,default='')               # 135 char
    PHI_PKT_PROFILE_ID=models.CharField(max_length=10,default='')                # 10 char



    
    def __unicode__(self):
        return 'PH instance ['+self.PKT_CTRL_NBR+']'
    
    def parse(self,coLine):
        try:
            self.PH1_ORD_DATE=coLine.purchaseDate[:10]
            self.PH1_START_SHIP_DATE=coLine.purchaseDate[:10]
            self.PH1_CUST_PO_NBR=coLine.orderId
            self.SHIPTO_NAME=coLine.shipToName
            self.SHIPTO_ADDR_1=coLine.shipToAddress1
            self.SHIPTO_ADDR_2=coLine.shipToAddress2
            self.SHIPTO_ADDR_3=coLine.shipToAddress3
            self.SHIPTO_CITY=coLine.shipToCity
            self.SHIPTO_STATE=coLine.shipToState
            self.SHIPTO_ZIP=coLine.shipToZip
            self.SHIPTO_CNTRY=coLine.shipToCntry
            self.PACK_SLIP_TYPE=coLine.packSlipType
            self.CARRIER=coLine.carrier
            self.ORD_TYPE=coLine.orderType[:2]
            self.SHIP_VIA=self.parse_ship_via(coLine.serviceLevel)
            self.PHI_SPL_INSTR_DESC=coLine.buyerEmail
        except:
            return(-1)
        return(0)
    
    def parse_ship_via(self,shipVia):
        #TODO: get full mapping of ship codes that come from Amazon, Zen and SS
        if shipVia == 'UPS Ground':
            return('UU10')
        elif shipVia == 'SUREPOST':
            return('UUSP')
        else:
            return('UUSP')
    def add_detail(self,index,coLine):
        pdItem=PD()
        pdItem.CUST_SKU=coLine.sku
        pdItem.SIZE_DESC=coLine.productName
        pdItem.ORIG_ORD_QTY=coLine.quantity
        pdItem.ORIG_PKT_QTY=coLine.quantity
        pdItem.PKT_SEQ_NBR='{:09}'.format(index)
        pdItem.STAT_CODE='00'
        lineError=pdItem.check_line()
        if lineError != '':
            # some missing information in this line item, generate an error
            coLine.parseError.append(lineError)
            coLine.save()
        pdItem.save()
    
    def check_line(self):
        errorLine=''
        if ((self.ORD_NBR == '' and self.PH1_CUST_PO_NBR == '') or self.SHIPTO_NAME == '' or 
            self.SHIPTO_ADDR_1 == '' or self.SHIPTO_CITY == '' or self.SHIPTO_STATE == '' or 
            self.SHIPTO_CNTRY == '' or self.SHIPTO_ZIP == '' or self.PH1_FREIGHT_TERMS == '' or 
            self.ORD_TYPE == '' or self.SHIP_VIA == '' or self.PKT_CTRL_NBR == '' or 
            self.PHI_SPL_INSTR_NBR == '' or self.PHI_SPL_INSTR_TYPE == '' or self.PHI_SPL_INSTR_CODE == ''):
            errorLine='PARSE ERROR: missing data on line '+str(self.fileLineNo)+' in file "'+self.filename+'":\n\t'
            if self.PH1_CUST_PO_NBR == '':
                errorLine+='"Customer PO # (ordere #)" missing, '
            if self.SHIPTO_NAME == '':
                errorLine+='"Ship to Name" missing, '
            if self.SHIPTO_ADDR_1 == '':
                errorLine+='"Ship to Address line 1" missing, '
            if self.SHIPTO_CITY == '':
                errorLine+='"Ship to City" missing, '
            if self.SHIPTO_STATE == '':
                errorLine+='"Ship to State" missing, '
            if self.SHIPTO_CNTRY == '':
                errorLine+='"Ship to Country" missing, '
            if self.SHIPTO_ZIP == '':
                errorLine+='"Ship to Zip" missing, '
            if self.ORD_TYPE=='':
                errorLine+='"Order Type" missing, '
            if self.SHIP_VIA == '':
                errorLine+='"Shipping Service Level" missing, '
            if self.PH1_FREIGHT_TERMS == '':
                errorLine+='"Freight Terms" missing, '
            if self.PKT_CTRL_NBR == '':
                errorLine+='"Pickticket Control Number" missing, '
            if self.PHI_SPL_INSTR_NBR == '':
                errorLine+='"Special Instruction Number" missing, '
            if self.PHI_SPL_INSTR_TYPE == '':
                errorLine+='"Special Instruction Type" missing, '
            if self.PHI_SPL_INSTR_CODE == '':
                errorLine+='"Special Instruction Code" missing, '
        return(errorLine)
    
    def ph_item(self):
        phItem=''
        phItem+=(self.REC_TYPE[:3]+self.SEP+self.WHSE[:3]+self.SEP+self.CO[:10]+self.SEP+self.DIV[:10]+self.SEP+
                 self.STAT_CODE[:2]+self.SEP+self.PKT_PROFILE_ID[:10]+self.SEP+
                 self.PKT_CTRL_NBR[:10]+self.SEP+self.PKT_NBR[:11]+self.SEP+self.PKT_SFX[:3]+self.SEP+
                 self.ORD_NBR[:8]+self.SEP+self.ORD_SFX[:3]+self.SEP+self.ORD_TYPE[:2]+self.SEP+
                 self.SHIPTO[:10]+self.SEP+self.SHIPTO_NAME[:35]+self.SEP+self.SHIPTO_CONTACT[:30]+self.SEP+
                 self.SHIPTO_ADDR_1[:75]+self.SEP+self.SHIPTO_ADDR_2[:75]+self.SEP+self.SHIPTO_ADDR_3[:75]+self.SEP+
                 self.SHIPTO_CITY[:40]+self.SEP+self.SHIPTO_STATE[:3]+self.SEP+self.SHIPTO_ZIP[:11]+self.SEP+
                 self.SHIPTO_CNTRY[:4]+self.SEP+self.TEL_NBR[:15]+self.SEP+
                 self.SOLDTO[:10]+self.SEP+self.SOLDTO_NAME[:35]+self.SEP+
                 self.SOLDTO_ADDR_1[:75]+self.SEP+self.SOLDTO_ADDR_2[:75]+self.SEP+self.SOLDTO_ADDR_3[:75]+self.SEP+
                 self.SOLDTO_CITY[:40]+self.SEP+self.SOLDTO_STATE[:3]+self.SEP+self.SOLDTO_ZIP[:11]+self.SEP+
                 self.SOLDTO_CNTRY[:4]+self.SEP+self.SHIP_VIA[:4]+self.SEP+self.CARTON_LABEL_TYPE[:3]+self.SEP+
                 self.NBR_OF_LABEL[:3]+self.SEP+self.CONTNT_LABEL_TYPE[:3]+self.SEP+self.NBR_OF_CONTNT_LABEL[:3]+self.SEP+
                 self.NBR_OF_PAKING_SLIPS[:3]+self.SEP+self.PACK_SLIP_TYPE[:2]+self.SEP+self.LANG_ID[:3]+os.linesep+
                 self.PH1_REC_TYPE[:3]+self.SEP+self.PH1_ACCT_RCVBL_ACCT_NBR[:10]+self.SEP+self.PH1_ACCT_RCVBL_CODE[:2]+self.SEP+
                 self.PH1_CUST_PO_NBR[:26]+self.SEP+self.PH1_PRTY_CODE[:2]+self.SEP+self.PH1_PRTY_SFX[:2]+self.SEP+
                 self.PH1_ORD_DATE[:14]+self.SEP+self.PH1_START_SHIP_DATE[:14]+self.SEP+self.PH1_STOP_SHIP_DATE[:14]+self.SEP+
                 self.PH1_SCHED_DLVRY_DATE[:14]+self.SEP+self.PH1_EARLIEST_DLVRY_TIME[:4]+self.SEP+
                 self.PH1_SCHED_DLVRY_DATE_END[:14]+self.SEP+self.PH1_RTE_GUIDE_NBR[:10]+self.SEP+self.PH1_CUST_RTE[:1]+self.SEP+
                 self.PH1_RTE_ATTR[:30]+self.SEP+self.PH1_RTE_ID[:10]+self.SEP+self.PH1_RTE_STOP_SEQ[:5]+self.SEP+
                 self.PH1_RTE_TO[:10]+self.SEP+self.PH1_RTE_TYPE_1[:2]+self.SEP+self.PH1_RTE_TYPE_2[:2]+self.SEP+
                 self.PH1_RTE_ZIP[:11]+self.SEP+self.PH1_RTE_SWC_NBR[:10]+self.SEP+self.PH1_CONSOL_NBR[:10]+self.SEP+
                 self.PH1_TOTAL_DLRS_UNDISC[:11]+self.SEP+self.PH1_TOTAL_DLRS_DISC[:11]+self.SEP+self.PH1_CURR_CODE[:10]+self.SEP+
                 self.PH1_PROD_VALUE[:11]+self.SEP+self.PH1_FREIGHT_TERMS[:1]+self.SEP+self.PH1_MARK_FOR[:25]+self.SEP+
                 self.PH1_INCO_TERMS[:3]+self.SEP+self.PH1_BILL_ACCT_NBR[:10]+self.SEP+self.PH1_COD_FUNDS[:1]+self.SEP+
                 self.PH1_INTL_GOODS_DESC[:35]+os.linesep)
        indx=int(self.PHI_SPL_INSTR_NBR[:3])
        for si in self.PHI_SPL_INSTR_CODE:

            phItem+=(self.PHI_REC_TYPE[:3]+self.SEP+'{:03}'.format(indx)+self.SEP+self.PHI_SPL_INSTR_TYPE[:2]+self.SEP+
                     si[:2]+self.SEP+self.PHI_SPL_INSTR_DESC[:135]+self.SEP+
                     self.PHI_PKT_PROFILE_ID[:10]+os.linesep)
            indx+=1
        for pdItem in self.PD:
            phItem+=pdItem.pd_item(self.CO,self.DIV)+os.linesep
        return(phItem)

class PD(models.Model):
    '''
    UPS Detail Loop, contained in a PH (Pickticket loop)
    '''
    SEP=models.CharField(max_length=1,default='|') # record separator
    ups_ph=models.ForeignKey(PH)
    
    # PD section
    # key for PD hash tables is PKT_SEQ_NBR
    REC_TYPE=models.CharField(max_length=2,default='PD')                       # 2 char
    PKT_SEQ_NBR=models.CharField(max_length=9,default='')                      # 9 char
    STAT_CODE=models.CharField(max_length=2,default='')                        # 2 char
    PKT_PROFILE_ID=models.CharField(max_length=2,default='',blank=True)        # opt. 2 char
    SEASON=models.CharField(max_length=2,default='',blank=True)                # opt. 2 char
    SEASON_YR=models.CharField(max_length=2,default='',blank=True)             # opt. 2 char
    STYLE=models.CharField(max_length=8,default='',blank=True)                 # opt. 8 char
    STYLE_SFX=models.CharField(max_length=8,default='',blank=True)             # opt. 8 char
    COLOR=models.CharField(max_length=4,default='',blank=True)                 # opt. 4 char
    COLOR_SFX=models.CharField(max_length=2,default='',blank=True)             # opt. 2 char
    SEC_DIM=models.CharField(max_length=3,default='',blank=True)               # opt. 3 char
    QUAL=models.CharField(max_length=1,default='',blank=True)                  # opt. 1 char
    SIZE_RANGE_CODE=models.CharField(max_length=4,default='',blank=True)       # opt. 4 char
    SIZE_REL_POSN_IN_TABLE=models.CharField(max_length=4,default='',blank=True)# opt. 2 char
    SIZE_DESC=models.CharField(max_length=15,default='',blank=True)            # opt. 15 char
    ORIG_ORD_QTY=models.CharField(max_length=9,default='',blank=True)          # 9 char
    ORIG_PKT_QTY=models.CharField(max_length=9,default='',blank=True)          # 9 char
    CANCEL_QTY=models.CharField(max_length=9,default='',blank=True)            # opt. 9 char
    CUBE_MULT_QTY=models.CharField(max_length=9,default='',blank=True)         # opt. 9 char
    BACK_ORD_QTY=models.CharField(max_length=9,default='',blank=True)          # opt. 9 char
    CUST_SKU=models.CharField(max_length=20,default='',blank=True)             # opt. 20 char
                                        # opt. PD1 section
                                        # opt. PD2 section
                                        # opt. PD3 section
                                        # opt. PDI section


    
    def __unicode__(self):
        return "PD instance"
    
    def pd_item(self,co,div):
        pdItem=''
        pdItem+=(self.REC_TYPE[:3]+self.SEP+self.PKT_SEQ_NBR[:9]+self.SEP+co[:10]+self.SEP+div[:10]+self.SEP+
                 self.STAT_CODE[:2]+self.SEP+self.PKT_PROFILE_ID[:10]+self.SEP+self.SEASON[:2]+self.SEP+
                 self.SEASON_YR[:2]+self.SEP+self.STYLE[:8]+self.SEP+self.STYLE_SFX[:8]+self.SEP+
                 self.COLOR[:4]+self.SEP+self.COLOR_SFX[:2]+self.SEP+self.SEC_DIM[:3]+self.SEP+
                 self.QUAL[:1]+self.SEP+self.SIZE_RANGE_CODE[:4]+self.SEP+self.SIZE_REL_POSN_IN_TABLE[:2]+self.SEP+
                 self.SIZE_DESC[:15]+self.SEP+self.ORIG_ORD_QTY[:9]+self.SEP+self.ORIG_PKT_QTY[:9]+self.SEP+
                 self.CANCEL_QTY[:9]+self.SEP+self.CUBE_MULT_QTY[:9]+self.SEP+self.BACK_ORD_QTY[:9]+self.SEP+
                 self.CUST_SKU[:20])
        return(pdItem)
    
    def check_line(self):
        errorLine=''
        if self.CUST_SKU == '' or self.ORIG_ORD_QTY == '' or self.PKT_SEQ_NBR:
            errorLine='PARSE ERROR: missing data on line '+str(self.fileLineNo)+' in file "'+self.filename+'":\n\t'
            if self.CUST_SKU == '':
                errorLine+='"SKU" missing, '
            if self.ORIG_ORD_QTY == '':
                errorLine+='"Quantity" missing, '
            if self.PKT_SEQ_NBR == '':
                errorLine+='"Pickticket Sequence Number" missing, '
        return(errorLine)
    
class CustOrder(models.Model):
    '''
    UPS customer order line item
    '''
    
    headers=[] # holds headers in order read from file
    sep=models.CharField(max_length=1,default='\t')
    ups_pkt=models.ForeignKey(PickTicket, blank=True)
    queryLineNo=models.IntegerField(default=0)
    queryName=models.URLField(default='')
    type=models.CharField(max_length=20, default='')
    purchaseDate=models.DateField(blank=True)
    orderId=models.CharField(max_length=50, default='')
    shipToName=models.CharField(max_length=50, default='')
    shipToAddress1=models.CharField(max_length=100, default='')
    shipToAddress2=models.CharField(max_length=100, default='')
    shipToAddress3=models.CharField(max_length=100, default='')
    shipToCity=models.CharField(max_length=100,default='')
    shipToState=models.CharField(max_length=100,default='')
    shipToZip=models.CharField(max_length=100,default='')
    shipToCntry=models.CharField(max_length=100,default='')
    packSlipType=models.CharField(max_length=50,default='')
    carrier=models.CharField(max_length=50,default='')
    orderType=models.CharField(max_length=50,default='')
    serviceLevel=models.CharField(max_length=50,default='')
    buyerEmail=models.EmailField(max_length=254,default='')
    sku=models.CharField(max_length=50,default='')
    productName=models.CharField(max_length=100,default='')
    quantity=models.IntegerField(default=0)
    parseError=models.TextField(default='')
    
    def __unicode__(self):
        return 'CustOrder abstract class'
    
    def read_header(self,line):
        self.headers=re.split(r'\t', line.rstrip())
        
    def read_zen_line(self,line):
        self.type='Zen'
        res=re.split(self.sep, line.rstrip())
        if line[-2:-1]==self.sep:
            res.append('')
        if len(res) != len(self.headers):
            return(-1) # improperly formatted line
        for item in self.headers:
            if item == 'v_date_purchased':
                self.purchaseDate=res[self.headers.index(item)]
            if item == 'v_orders_id':
                self.orderId=res[self.headers.index(item)]
            if item == 'v_customers_name':
                self.shipToName=res[self.headers.index(item)]
            if item == 'v_customers_street_address':
                self.shipToAddress1=res[self.headers.index(item)]
            if item == 'v_customers_suburb':
                self.shipToAddress2=res[self.headers.index(item)]
            if item == 'v_customers_city':
                self.shipToCity=res[self.headers.index(item)]
            if item == 'v_customers_postcode':
                self.shipToZip=res[self.headers.index(item)]
            if item == 'v_customers_country':
                self.shipToCntry=res[self.headers.index(item)]
            if item == 'v_customers_email_address':
                self.buyerEmail=res[self.headers.index(item)]
            if item == 'v_products_model':
                self.sku=res[self.headers.index(item)]
            if item == 'v_products_name':
                self.productName=res[self.headers.index(item)]
        #self.parse_zen_date()
        return(0)
        
    def parse_zen_date(self):
        #format: 2014-08-14 14:20:46
        try:
            pieces=re.split(r' ',self.purchaseDate)
            ymd=re.split(r'-',pieces[0])
            #drop off final number separated by a +/-.  Is it some GMT adder?
            # doesn't seem to correlate with actual timesone of purchaser
            self.purchaseDate=ymd[1]+'/'+ymd[2]+'/'+ymd[0]+' '+pieces[1]
        except:
            self.purchaseDate='00/00/00 00:00:00'
    
    def read_ss_line(self,line):
        self.type='SS'
        res=re.split(self.sep, line.rstrip())
        if len(res) != len(self.headers):
            # improperly formatted line
            if len(res) > len(self.headers):
                # the line is too long
                return(-1)
            # assume that there are empty cells at the end of the line, just add empty strings
            for indx in range(len(self.headers)-len(res)):
                res.append('')
        for item in self.headers:
            if item == 'sku':
                self.sku=res[self.headers.index(item)]
            if item == 'product-name':
                self.productName=res[self.headers.index(item)]
            if item == 'order-id':
                self.orderId=res[self.headers.index(item)]
            if item == 'order-type':
                self.orderType=res[self.headers.index(item)]
            if item == 'quantity-purchased':
                self.quantity=res[self.headers.index(item)]
            if item == 'purchase-date':
                self.purchaseDate=res[self.headers.index(item)]
            if item == 'ship-service-level':
                self.serviceLevel=res[self.headers.index(item)]
            if item == 'recipient-name':
                self.shipToName=res[self.headers.index(item)]
            if item == 'buyer-email':
                self.buyerEmail=res[self.headers.index(item)]
            if item == 'ship-address-1':
                self.shipToAddress1=res[self.headers.index(item)]
            if item == 'ship-address-2':
                self.shipToAddress2=res[self.headers.index(item)]
            if item == 'ship-address-3':
                self.shipToddress3=res[self.headers.index(item)]
            if item == 'ship-city':
                self.shipToCity=res[self.headers.index(item)]
            if item == 'ship-state':
                self.shipToState=res[self.headers.index(item)]
            if item == 'ship-postal-code':
                self.shipToZip=res[self.headers.index(item)]
            if item == 'ship-country':
                self.shipToCntry=res[self.headers.index(item)]
            if item == 'carrier':
                self.carrier=res[self.headers.index(item)]
            if item == 'pack-slip-type':
                self.packSlipType=res[self.headers.index(item)]
        return(0)
    
    def read_amazon_line(self,line):
        self.type='Amazon'
        res=re.split(self.sep, line.rstrip())
        if line[-2:-1]==self.sep:
            res.append('')
        if len(res) != len(self.headers):
            return(-1) # improperly formatted line
        for item in self.headers:
            if item == 'buyer-name':
                self.shipToName=res[self.headers.index(item)]
            if item == 'buyer-email':
                self.buyerEmail=res[self.headers.index(item)]
            if item == 'sku':
                self.sku=res[self.headers.index(item)]
            if item == 'product-name':
                self.productName=res[self.headers.index(item)]
            if item == 'purchase-date':
                self.purchaseDate=res[self.headers.index(item)]
            if item == 'order-id':
                self.orderId=res[self.headers.index(item)]
            if item == 'quantity-purchased':
                self.quantity=res[self.headers.index(item)]
            if item == 'ship-service-level':
                self.serviceLevel=res[self.headers.index(item)]
            if item == 'recipient-name':
                self.shipToName=res[self.headers.index(item)]
            if item == 'ship-address-1':
                self.shipToAddress1=res[self.headers.index(item)]
            if item == 'ship-address-2':
                self.shipAddress2=res[self.headers.index(item)]
            if item == 'ship-address-3':
                self.shipAddress3=res[self.headers.index(item)]
            if item == 'ship-city':
                self.shipToCity=res[self.headers.index(item)]
            if item == 'ship-state':
                self.shipToState=res[self.headers.index(item)]
            if item == 'ship-postal-code':
                self.shipToZip=res[self.headers.index(item)]
            if item == 'ship-country':
                self.shipToCntry=res[self.headers.index(item)]
            if item == 'carrier':
                self.carrier=res[self.headers.index(item)]
            if item == 'pack-slip-type':
                self.packSlipType=res[self.headers.index(item)]
        
        #self.parse_amazon_date()
        return(0)
    
    def parse_amazon_date(self):
        #format: 2014-09-08T13:08:30-07:00
        try:
            pieces=re.split(r'T',self.purchaseDate)
            ymd=re.split(r'-',pieces[0])
            timeGmt=re.split(r'[+-]',pieces[1])
            #drop off final number separated by a +/-.  Is it some GMT adder?
            # doesn't seem to correlate with actual timezone of purchaser
            self.purchaseDate=ymd[1]+'/'+ymd[2]+'/'+ymd[0]+' '+timeGmt[0]
        except:
            self.purchaseDate='00/00/00 00:00:00'


class ShipmentOrderReport(models.Model):
    '''
    UPS shipped orders report object
    '''
    workbook='' # excel workbook to read from
    filename='' # filename for excel workbook
    headers=[] # headers in the file
    SO=[] # list of shipped order line items
    parseErrors={} # dictionary of various errors related to parsed files
    amazonSep='|'
    zenSep='|'
    
    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(ShipmentOrderReport,self).__init__()
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'workbook':
                    self.workbook=value
                if key == 'filename':
                    self.filename=value
                if key == 'SO':
                    self.SO=value
                if key == 'amazonSep':
                    self.amazonSep=value
                if key == 'zenSep':
                    self.zenSep=value
        else:
            raise TypeError("Invalid data type passed to ShipmentOrderReport __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "ShipmentOrderReport instance"
    
    def open_workbook(self,filename):
        self.parseErrors[self.filename]=[]
        try:
            self.workbook=xlrd.open_workbook(filename)
        except:
            self.parseErrors[self.filename].append('FILE ERROR: unable to open Shipped Orders spreadsheet "' + self.filename + '"')
            return(-1)
        return(0)
    
    def read_header(self):
        sheet = self.workbook.sheet_by_index(0)
        foundHeader=False
        for rowIndex in range(sheet.nrows):
            for colIndex in range(sheet.ncols):
                cell=sheet.cell(rowIndex,colIndex).value
                if cell == 'Warehouse' and not foundHeader:
                    # assume first header is 'Warehouse'
                    foundHeader=True
                if foundHeader:
                    self.headers.append(cell)
            if foundHeader:
                return(0)
        # No headers in the file
        self.parseErrors.append('PARSE ERROR: unable to locate header line in "' + self.filename.rsplit(os.sep,1)[1] + '"')
        return(-1)
    
    def read_lines(self):
        try:
            # Assume that the first sheet is the one to parse
            sheet = self.workbook.sheet_by_index(0)
            foundHeader=False
            headerLine=1e6
            for rowIndex in range(sheet.nrows):
                # Find the header row
                if rowIndex < headerLine:
                    for colIndex in range(sheet.ncols):
                        cell=sheet.cell(rowIndex,colIndex).value
                        if cell == 'Warehouse' and not foundHeader:
                            foundHeader=True
                            headerLine=rowIndex
                            break
                else:
                    # Assume rows after the header row contain line items
                    line=''
                    # build up a tab separated line that ShipmentOrderRow line items know how to parse 
                    for colIndex in range(sheet.ncols):
                        cell=sheet.cell(rowIndex,colIndex)
                        # parse the cell information base on cell type
                        if cell.ctype == xlrd.XL_CELL_TEXT:
                            line+=cell.value+'\t'
                        elif cell.ctype == xlrd.XL_CELL_EMPTY:
                            line+='\t'
                        elif cell.ctype == xlrd.XL_CELL_NUMBER:
                            line+=str(cell.value)+'\t'
                        elif cell.ctype == xlrd.XL_CELL_DATE:
                            line+=self.parse_date(cell)+'\t'
                        else:
                            # unspecified cell type, just output a blank
                            line+='\t'
                            self.parseErrors[self.filename].append('PARSE WARNING: unknown data type in cell ('+ xlrd.cellname(rowIndex,colIndex) +'), set to blank ')
                    so=ShipmentOrderRow({'headers':self.headers,'fileLineNo':rowIndex+1})
                    so.read_line(line[:-1])
                    lineError=so.check_line()
                    if lineError != '':
                        # some missing information in this line item, generate an error
                        self.parseErrors[self.filename].append(lineError)
                    self.SO.append(so)
        except:
            self.parseErrors[self.filename].append('PARSE ERROR: unspecified error occurred while reading lines from "' + self.filename.rsplit(os.sep,1)[1] + '"')
            return(-1)
        if headerLine == 1e6:
            # we never found a header line
            self.parseErrors[self.filename].append('PARSE ERROR: unable to locate header line in "' + self.filename.rsplit(os.sep,1)[1] + '"')
            return(-1)
        return(0)
    
    def parse_date(self,cell):
        #format: excel date object
        timeValue =xlrd.xldate_as_tuple(cell.value,self.workbook.datemode)
        return timezone.datetime(*timeValue).strftime('%m/%d/%y %H:%M:%S')
    
    def parse_report(self):
        fileErrors=[]
        lineParseErrors=[]
        reportStr='Report for file "'+self.filename+'"\n\n'
        if len(self.amazon_shipped().split('\n')) > 2:
            reportStr+='Created Amazon Shipped Orders Upload file\n'
        else:
            reportStr+='No Amazon Shipped Orders Upload file created.  No items shipped or errors were encountered.\n'
        if len(self.zen_shipped().split('\n')) > 2:
            reportStr+='Created Zen Shipped Orders Upload file\n'
        else:
            reportStr+='No Zen Shipped Orders Upload file created.  No items shipped or errors were encountered.\n'
        for key,value in self.parseErrors.iteritems():
            for errorLine in value:
                if re.split(r':',errorLine)[0] == 'FILE ERROR':
                    fileErrors.append(errorLine)
                if re.split(r':',errorLine)[0] == 'PARSE ERROR':
                    lineParseErrors.append(errorLine)
        for fileError in fileErrors:
            reportStr+=fileError+'\n'
        reportStr+='\n'
        for lineParseError in lineParseErrors:
            reportStr+=lineParseError+'\n'
        reportStr+='\n'
        for soItem in self.SO:
            reportStr+='Order Number: '+soItem.ORD_NBR+'\n'
            reportStr+='\tFile Line No: '+str(soItem.fileLineNo)+'\n'
            reportStr+='\tShip Date: '+soItem.MOD_DATE+'\n'
            reportStr+='\tTracking Number: '+soItem.TRACKING_NBR+'\n'
            reportStr+='\tOrder Type: '+soItem.ORD_TYPE+'\n'
            reportStr+='\tShip Via: '+soItem.SHIP_VIA+'\n\n'
        return(reportStr)
    
    def amazon_shipped(self):
        amazonStr=('order-id'+self.amazonSep+'order-item-id'+self.amazonSep+'quantity'+self.amazonSep+
             'ship-date'+self.amazonSep+'carrier-code'+self.amazonSep+'carrier-name'+self.amazonSep+
             'tracking-number'+self.amazonSep+'ship-method\n')
        for order in self.SO:
            if order.ORD_TYPE=='AMAZON':
                amazonStr+=(order.ORD_NBR+self.amazonSep+order.ORD_SFX+self.amazonSep+order.TOTAL_UNIT_QTY+self.amazonSep+
                      order.MOD_DATE+self.amazonSep+'UPS'+self.amazonSep+''+self.amazonSep+order.TRACKING_NBR+self.amazonSep+
                      order.SHIP_VIA+'\n')
        return(amazonStr)
    
    def zen_shipped(self):
        zenStr=('order-id'+self.zenSep+'order-item-id'+self.zenSep+'quantity'+self.zenSep+
             'ship-date'+self.zenSep+'carrier-code'+self.zenSep+'carrier-name'+self.zenSep+
             'tracking-number'+self.zenSep+'ship-method\n')
        for order in self.SO:
            if order.ORD_TYPE=='ZEN':
                zenStr+=(order.ORD_NBR+self.zenSep+order.ORD_SFX+self.zenSep+order.TOTAL_UNIT_QTY+self.zenSep+
                      order.MOD_DATE+self.zenSep+'UPS'+self.zenSep+''+self.zenSep+order.TRACKING_NBR+self.zenSep+
                      order.SHIP_VIA+'\n')
        return(zenStr)

class ShipmentOrderRow(models.Model):
    '''
    UPS shipped orders line item object
    '''
    headers=[]
    fileLineNo=0
    WHSE='' # from PH (Warehouse)
    CMPY_NAME='' # from HD (Company)
    DIV='' # from PH (Division)
    PKT_CTRL_NBR='' # from PH (Pickticket Control Number)
    PKT_NBR='' # from PH (Pickticket Number)
    PKT_SFX='' # from PH (Pickticket Suffix)
    ORD_NBR='' # from PH (Order Number)
    ORD_SFX='' # from PH (Order Number Suffix)
    ORD_TYPE='' # from PH (Order Type)
    ORD_STATUS='' # ??? unique to Shipped Order (Order Status)
    SHIPTO_NBR='' # ???is this really just SHIPTO from PH? (Ship to Number))
    SHIPTO_NAME='' # from PH (Ship to Name)
    SHIPTO_CONTACT='' # from PH (Ship to Contact)
    SHIPTO_ADDR_1='' # from PH (Ship to Address Line 1)
    SHIPTO_ADDR_2='' # from PH (Ship to Address Line 2)
    SHIPTO_ADDR_3='' # from PH (Ship to Address Line 3)
    SHIPTO_CITY='' # from PH (Ship to State)
    SHIPTO_STATE='' # from PH (Ship to State)
    SHIPTO_ZIP='' # from PH (Ship to Postal Code)
    SHIPTO_CNTRY='' # from PH (Ship to Country)
    SHIP_VIA='' # from PH (Ship Via)
    CUST_PO_NBR='' # from PH (Customer PO Number)
    THRD_PARTY_BILL_ACCT='' # ???is this really BILL_ACCT_NBR from PH? (Third Party Billing Acct)
    BILL_OF_LADING_NBR='' # ??? unique to Shipped Order (Bill of Lading Number)
    MANIFEST_NBR='' # ??? unique to Shipped Order (Manifest Number)
    SHIP_W_CTRL_NBR='' # from PH (Ship With Control Number)
    SHIPMENT_NBR='' # ??? unique to Shipped Order (Shipment Number)
    MASTER_BOL='' # ??? unique to Shipped Order (Master BOL)
    PALLET_NBR='' # ??? unique to Shipped Order (Pallet Number)
    CARTON_NBR='' # ??? unique to Shipped Order (Carton Number)
    CARTON_STATUS='' # ??? unique to Shipped Order (Carton Status)
    TRACKING_NBR='' # ??? unique to Shipped Order (Tracking Number)
    CARTON_TYPE='' # ??? unique to Shipped Order (Carton Type)
    CARTON_SIZE='' # ??? unique to Shipped Order (Carton Size)
    CARTON_VOLUME='' # ??? unique to Shipped Order (Carton Volume)
    VOLUME_UOM='' # ??? unique to Shipped Order (Vol.UOM)
    ESTIMATED_WEIGHT='' # ??? unique to Shipped Order (Estimated Weight)
    ACTUAL_WEIGHT='' # ??? unique to Shipped Order (Actual Weight)
    WEIGHT_UOM='' # ??? unique to Shipped Order (Wt.UOM)
    #TOTAL_NBR_CARTONS='' # ??? unique to Shipped Order (Total Number of Cartons)
    SHIP_CHRGS='' # ??? unique to Shipped Order (Shipping Charges)
    CURRENCY='' # ??? unique to Shipped Order (Currency)
    CARTON_X_Y='' # ??? unique to Shipped Order (Carton  X  of Y)
    TOTAL_UNIT_QTY='' # ??? unique to Shipped Order (Total Unit Quantity)
    MOD_DATE='' # ??? unique to Shipped Order (Carton Modified Date & Time)
    #CREATE_DATE='' # ??? unique to Shipped Order (Date & Time Created)
    #INVOICE_DATE='' # ??? unique to Shipped Order (Date & Time Invoiced)
    
    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(ShipmentOrderRow,self).__init__()
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'headers':
                    self.headers=value
                if key == 'fileLineNo':
                    self.fileLineNo=value
                if key == 'Warehouse':
                    self.WHSE=value
                if key == 'Company':
                    self.CMPY_NAME=value
                if key == 'Division':
                    self.DIV=value
                if key == 'Pickticket Control Number':
                    self.PKT_CTRL_NBR=value
                if key == 'Pickticket Number':
                    self.PKT_NBR=value
                if key == 'Pickticket Number':
                    self.PKT_SFX=value
                if key == 'Order Number':
                    self.ORD_NBR=value
                if key == 'Order Number Suffix':
                    self.ORD_SFX=value
                if key == 'Order Type':
                    self.ORD_TYPE=value
                if key == 'Order Status':
                    self.ORD_STATUS=value
                if key == 'Ship to Number':
                    self.SHIPTO_NBR=value
                if key == 'Ship to Name':
                    self.SHIPTO_NAME=value
                if key == 'Ship to Contact':
                    self.SHIPTO_CONTACT=value
                if key == 'Ship to Address Line 1':
                    self.SHIPTO_ADDR_1=value
                if key == 'Ship to Address Line 2':
                    self.SHIPTO_ADDR_2=value
                if key == 'Ship to Address Line 3':
                    self.SHIPTO_ADDR_3=value
                if key == 'Ship to City':
                    self.SHIPTO_CITY=value
                if key == 'Ship to State':
                    self.SHIPTO_STATE=value
                if key == 'Ship to Postal Code':
                    self.SHIPTO_ZIP=value
                if key == 'Ship to Country':
                    self.SHIPTO_CNTRY=value
                if key == 'Ship Via':
                    self.SHIP_VIA=value
                if key == 'Customer PO Number':
                    self.CUST_PO_NBR=value
                if key == 'Third Party Billing Acct':
                    self.THRD_PARTY_BILL_ACCT=value
                if key == 'Bill of Lading Number':
                    self.BILL_OF_LADING_NBR=value
                if key == 'Manifest Number':
                    self.MANIFEST_NBR=value
                if key == 'Ship With Control Number':
                    self.SHIP_W_CTRL_NBR=value
                if key == 'Shipment Number':
                    self.SHIPMENT_NBR=value
                if key == 'Master BOL':
                    self.MASTER_BOL=value
                if key == 'Pallet Number':
                    self.PALLET_NBR=value
                if key == 'Carton Number':
                    self.CARTON_NBR=value
                if key == 'Carton Status':
                    self.CARTON_STATUS=value
                if key == 'Tracking Number':
                    self.TRACKING_NBR=value
                if key == 'Carton Type':
                    self.CARTON_TYPE=value
                if key == 'Carton Size':
                    self.CARTON_SIZE=value
                if key == 'Carton Volume':
                    self.CARTON_VOLUME=value
                if key == 'Vol.UOM':
                    self.VOLUME_UOM=value
                if key == 'Estimated Weight':
                    self.ESTIMATED_WEIGHT=value
                if key == 'Actual Weight':
                    self.ACTUAL_WEIGHT=value
                if key == 'Wt.UOM':
                    self.WEIGHT_UOM=value
                if key == 'Total Number of Cartons':
                    self.TOTAL_NBR_CARTONS=value
                if key == 'Shipping Charges':
                    self.SHIP_CHRGS=value
                if key == 'Currency':
                    self.CURRENCY=value
                if key == 'Carton  X  of Y':
                    self.CARTON_X_Y=value
                if key == 'Total Unit Quantity':
                    self.TOTAL_UNIT_QTY=value
                if key == 'Total Unit Quantity':
                    self.TOTAL_UNIT_QTY=value
                if key == 'Carton Modified Date & Time':
                    self.MOD_DATE=value
                if key == 'Date & Time Invoiced':
                    self.INVOICE_DATE=value
        else:
            raise TypeError("Invalid data type passed to ShipmentOrderRow __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "ShipmentOrderRow instance"
    
    def read_line(self,line):
        res=re.split(r'\t', line.rstrip())
        if len(res) != len(self.headers):
            return(-1) # improperly formatted line
        for item in self.headers:
            if item == 'Warehouse':
                self.WHSE=res[self.headers.index(item)]
            if item == 'Company':
                self.CMPY_NAME=res[self.headers.index(item)]
            if item == 'Division':
                self.DIV=res[self.headers.index(item)]
            if item == 'Pickticket Control Number':
                self.PKT_CTRL_NBR=res[self.headers.index(item)]
            if item == 'Pickticket Number':
                self.PKT_NBR=res[self.headers.index(item)]
            if item == 'Pickticket Suffix':
                self.PKT_SFX=res[self.headers.index(item)]
            if item == 'Order Number':
                self.ORD_NBR=res[self.headers.index(item)]
            if item == 'Order Number Suffix':
                self.ORD_SFX=res[self.headers.index(item)]
            if item == 'Order Type':
                self.ORD_TYPE=res[self.headers.index(item)]
            if item == 'Order Status':
                self.ORD_STATUS=res[self.headers.index(item)]
            if item == 'Ship to Number':
                self.SHIPTO_NBR=res[self.headers.index(item)]
            if item == 'Ship to Name':
                self.SHIPTO_NAME=res[self.headers.index(item)]
            if item == 'Ship to Contact':
                self.SHIPTO_CONTACT=res[self.headers.index(item)]
            if item == 'Ship to Address Line 1':
                self.SHIPTO_ADDR_1=res[self.headers.index(item)]
            if item == 'Ship to Address Line 2':
                self.SHIPTO_ADDR_2=res[self.headers.index(item)]
            if item == 'Ship to Address Line 3':
                self.SHIPTO_ADDR_3=res[self.headers.index(item)]
            if item == 'Ship to City':
                self.SHIPTO_CITY=res[self.headers.index(item)]
            if item == 'Ship to State':
                self.SHIPTO_STATE=res[self.headers.index(item)]
            if item == 'Ship to Postal Code':
                self.SHIPTO_ZIP=res[self.headers.index(item)]
            if item == 'Ship to Country':
                self.SHIPTO_CNTRY=res[self.headers.index(item)]
            if item == 'Ship Via':
                self.SHIP_VIA=res[self.headers.index(item)]
            if item == 'Customer PO Number':
                self.CUST_PO_NBR=res[self.headers.index(item)]
            if item == 'Third Party Billing Acct':
                self.THRD_PARTY_BILL_ACCT=res[self.headers.index(item)]
            if item == 'Bill of Lading Number':
                self.BILL_OF_LADING_NBR=res[self.headers.index(item)]
            if item == 'Manifest Number':
                self.MANIFEST_NBR=res[self.headers.index(item)]
            if item == 'Ship With Control Number':
                self.SHIP_W_CTRL_NBR=res[self.headers.index(item)]
            if item == 'Shipment Number':
                self.SHIPMENT_NBR=res[self.headers.index(item)]
            if item == 'Master BOL':
                self.MASTER_BOL=res[self.headers.index(item)]
            if item == 'Pallet Number':
                self.PALLET_NBR=res[self.headers.index(item)]
            if item == 'Carton Number':
                self.CARTON_NBR=res[self.headers.index(item)]
            if item == 'Carton Status':
                self.CARTON_STATUS=res[self.headers.index(item)]
            if item == 'Tracking Number':
                self.TRACKING_NBR=res[self.headers.index(item)]
            if item == 'Carton Type':
                self.CARTON_TYPE=res[self.headers.index(item)]
            if item == 'Carton Size':
                self.CARTON_SIZE=res[self.headers.index(item)]
            if item == 'Carton Volume':
                self.CARTON_VOLUME=res[self.headers.index(item)]
            if item == 'Vol.UOM':
                self.VOLUME_UOM=res[self.headers.index(item)]
            if item == 'Estimated Weight':
                self.ESTIMATED_WEIGHT=res[self.headers.index(item)]
            if item == 'Actual Weight':
                self.ACTUAL_WEIGHT=res[self.headers.index(item)]
            if item == 'Wt.UOM':
                self.WEIGHT_UOM=res[self.headers.index(item)]
            if item == 'Total Number of Cartons':
                self.TOTAL_NBR_CARTONS=res[self.headers.index(item)]
            if item == 'Shipping Charges':
                self.SHIP_CHRGS=res[self.headers.index(item)]
            if item == 'Currency':
                self.CURRENCY=res[self.headers.index(item)]
            if item == 'Carton  X  of Y':
                self.CARTON_X_Y=res[self.headers.index(item)]
            if item == 'Total Unit Quantity':
                self.TOTAL_UNIT_QTY=res[self.headers.index(item)]
            if item == 'Carton Modified Date & Time':
                self.MOD_DATE=res[self.headers.index(item)]
            if item == 'Date & Time Created':
                self.CREATE_DATE=res[self.headers.index(item)]
            if item == 'Date & Time Invoiced':
                self.INVOICE_DATE=res[self.headers.index(item)]
        return(0)
    def check_line(self):
        errorLine=''
        if self.ORD_NBR == '' or self.SHIP_VIA == '' or self.MOD_DATE == '' or self.TRACKING_NBR == '' or self.ORD_TYPE=='':
            errorLine='PARSE ERROR: missing data on line '+str(self.fileLineNo)+':\n\t'
            if self.ORD_NBR == '':
                errorLine+='"Order Number" missing, '
            if self.SHIP_VIA=='':
                errorLine+='"Ship Via" missing, '
            if self.TRACKING_NBR=='':
                errorLine+='"Tracking Number" missing, '
            if self.MOD_DATE=='':
                errorLine+='"Carton Modified Date & Time" missing, '
            if self.ORD_TYPE=='':
                errorLine+='"Order Type" missing, '
        return(errorLine)