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
                        files[fStr.name]=fStr.readlines()
                except:
                    # failed to open file
                    files[poFile]=['FILE ERROR: unable to open file "' + poFile + '"']
    if inputType == 3:
        # URLs
        for poUrl in args:
            try:
                urlStr = urllib2.urlopen(poUrl)
                files[urlStr.url]=urlStr.readlines()
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
    ups_pkt=UPS_PKT()
    ups_pkt.DOC_DATE=timezone.datetime.fromtimestamp(timeStamp).strftime('%m/%d/%y %H:%M:%S')
    ups_pkt.warehouse=warehouse
    ups_pkt.CMPY_NAME=company
    ups_pkt.division=division
    ups_pkt.timeStamp='{:08x}'.format(int(timeStamp))
    ups_pkt.fileName=fileName
    ups_pkt.save()
    
    files=mirai_get_files(inputType, files)
    ups_co_fileids=[]
    for f,contents in files.iteritems():
        this_ups_co_file=UPS_CO_FILE()
        this_ups_co_file.filename=f
        this_ups_co_file.contents=contents
        this_ups_co_file.ups_pkt=ups_pkt
        this_ups_co_file.save()
        ups_co_fileids.append(this_ups_co_file.id)
    ups_pkt.read_files(ups_co_fileids)
    return ups_pkt

# Create your models here.
    
class UPS_PKT(models.Model):
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
    PH=[]                           # holds pickticket loop items
    # TRL section
    TRL_REC_TYPE=models.CharField(max_length=3, default='TRL')              # 3 char
    #
    poObjects={} # orders from all sources
    parseErrors={} # dictionary of various errors related to parsed files
    timeStamp=''
    fileName=models.URLField(default='')
    fileContents=models.TextField(default='')
    warehouse='' # for passing down into the PH object
    division='' # for passing down into the PH object
    
    def __str__(self):
        res = "UPS_PKT instance:" + self.fileName
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
    
    def read_files(self,fileids):
        mirai={}
        amazon={}
        ss={}
        for fileid in fileids:
            try:
                fileName=UPS_CO_FILE.get(fileid).fileName
                poFile=UPS_CO_FILE.get(fileid).contents.splitlines()
                mirai[fileName]=[]
                amazon[fileName]=[]
                ss[fileName]=[]
                lineNo = 0
                header=poFile[0]
                lineNo += 1
                # identify file type
                reMatch=re.compile('.*v_orders_id.*')
                if reMatch.match(header):
                    #print 'found Mirai file:"'+poFile+'"'
                    self.parseErrors[fileName]=[]
                    for line in poFile[1:]:
                        lineNo += 1
                        miraiIncr=Zen_CO()
                        miraiIncr.fromFile=fileName
                        miraiIncr.fileLineNo=lineNo
                        miraiIncr.filename=fileName
                        miraiIncr.read_header(header)
                        if miraiIncr.read_line(line.rstrip()) < 0:
                            # improperly formatted record
                            self.parseErrors[fileName].append('PARSE ERROR: improperly formatted line: # '+str(lineNo)+ ' in "' + fileName + '"')
                        mirai[fileName].append(miraiIncr)
                reMatch=re.compile('.*buyer-phone-number.*')
                if reMatch.match(header):
                    #print 'found Amazon file:"'+poFile+'"'
                    self.parseErrors[fileName]=[]
                    for line in poFile[1:]:
                        lineNo += 1
                        amazonIncr=Amazon_CO()
                        amazonIncr.fromFile=fileName
                        amazonIncr.fileLineNo=lineNo
                        amazonIncr.filename=fileName
                        amazonIncr.read_header(header)
                        if amazonIncr.read_line(line.rstrip()) < 0:
                            # improperly formatted record
                            self.parseErrors[fileName].append('PARSE ERROR: improperly formatted line: # '+str(lineNo)+ ' in "' + fileName + '"')
                        amazon[fileName].append(amazonIncr)
                reMatch=re.compile('.*pack-slip-type.*')
                if reMatch.match(header):
                    #print 'found ShipStation file:"'+poFile+'"'
                    self.parseErrors[fileName]=[]
                    for line in poFile[1:]:
                        lineNo += 1
                        ssIncr=SS_CO()
                        ssIncr.fromFile=fileName
                        ssIncr.fileLineNo=lineNo
                        ssIncr.filename=fileName
                        ssIncr.read_header(header)
                        if ssIncr.read_line(line.rstrip()) < 0:
                            # improperly formatted record
                            self.parseErrors[fileName].append('PARSE ERROR: improperly formatted line: # '+str(lineNo)+ ' in "' + fileName + '"')
                        ss[fileName].append(ssIncr)
                reMatch=re.compile('.*ERROR.*')
                if reMatch.match(header):
                    self.parseErrors[fileName]=[]
                    #found a file error
                    self.parseErrors[fileName].append(header)
            except:
                self.parseErrors[fileName].append('FILE ERROR: Unable to open "' + fileName + '" for reading')
        self.poObjects['mirai']=mirai
        self.poObjects['amazon']=amazon
        self.poObjects['ss']=ss
        self.parse_po_objects()
        
    def parse_po_objects(self):
        phItems={}
        itemIndex=0
        phIndex=0
        for key,value in self.poObjects.iteritems():
            for fName,poList in value.iteritems():
                if key == 'mirai':
                    for mirai in poList:
                        if 'mirai_'+mirai.v_orders_id not in phItems:
                            # start compiling a list of items ordered by this customer
                            phIndex+=1
                            phItems['mirai_'+mirai.v_orders_id]=UPS_PH({'WHSE':self.warehouse,
                                                                        'CO':self.CMPY_NAME,
                                                                        'DIV':self.division,
                                                                        'STAT_CODE':'10',
                                                                        'PKT_PROFILE_ID':'MIRAI001',
                                                                        'PKT_CTRL_NBR':'MC'+self.timeStamp,
                                                                        'CARTON_LABEL_TYPE':'001',
                                                                        'NBR_LABEL':'001',
                                                                        'CONTENT_LABEL_TYPE':'001',
                                                                        'NBR_OF_CONTNT_LABEL':'001',
                                                                        'PACK_SLIP_TYPE':'001',
                                                                        'LANG_ID':'EN',
                                                                        'PH1_FREIGHT_TERMS':'0',
                                                                        'PHI_SPL_INSTR_NBR':'{:03}'.format(phIndex),
                                                                        'PHI_SPL_INSTR_TYPE':'QV',
                                                                        'PHI_SPL_INSTR_CODE':['01','08'],
                                                                        'filename':fName})
                            if phItems['mirai_'+mirai.v_orders_id].parse(mirai) < 0:
                                self.parseErrors['mirai_'+mirai.v_orders_id]=['PARSE ERROR: Unable to create PH item: '+'mirai_'+mirai.v_orders_id+' from file "'+fName+'"']
                                del phItems['mirai_'+mirai.v_orders_id]
                        if 'mirai_'+mirai.v_orders_id in phItems:
                            itemIndex+=1
                            phItems['mirai_'+mirai.v_orders_id].add_mirai_detail(mirai,itemIndex)
                            lineError=phItems['mirai_'+mirai.v_orders_id].check_line()
                            if lineError != '':
                                # some missing information in this line item, generate an error
                                self.parseErrors['mirai_'+mirai.v_orders_id]=[lineError]
                if key == 'amazon':
                    for amazon in poList:
                        if 'amazon_'+amazon.order_id not in phItems:
                            # start compiling a list of items ordered by this customer
                            phIndex+=1
                            phItems['amazon_'+amazon.order_id]=UPS_PH({'WHSE':self.warehouse,
                                                                        'CO':self.CMPY_NAME,
                                                                        'DIV':self.division,
                                                                        'STAT_CODE':'10',
                                                                        'PKT_PROFILE_ID':'MIRAI001',
                                                                        'PKT_CTRL_NBR':'MC'+self.timeStamp,
                                                                        'LANG_ID':'EN',
                                                                        'PH1_FREIGHT_TERMS':'0',
                                                                        'PHI_SPL_INSTR_NBR':'{:03}'.format(phIndex),
                                                                        'PHI_SPL_INSTR_TYPE':'QV',
                                                                        'PHI_SPL_INSTR_CODE':['01','08'],
                                                                        'filename':fName})
                            if phItems['amazon_'+amazon.order_id].parse(amazon) < 0:
                                self.parseErrors['amazon_'+amazon.order_id]=['PARSE ERROR: Unable to create PH item: "'+'amazon_'+amazon.order_id+'"']
                                del phItems['amazon_'+amazon.order_id]
                        if 'amazon_'+amazon.order_id in phItems:
                            itemIndex+=1
                            phItems['amazon_'+amazon.order_id].add_amazon_detail(amazon,itemIndex)
                            lineError=phItems['amazon_'+amazon.order_id].check_line()
                            if lineError != '':
                                # some missing information in this line item, generate an error
                                phIndex+=1
                                self.parseErrors['amazon_'+amazon.order_id]=[lineError]
                if key == 'ss':
                    for ss in poList:
                        if 'ss_'+ss.order_id not in phItems:
                            # start compiling a list of items ordered by this customer
                            phIndex+=2
                            phItems['ss_'+ss.order_id]=UPS_PH({'WHSE':self.warehouse,
                                                               'CO':self.CMPY_NAME,
                                                               'DIV':self.division,
                                                               'STAT_CODE':'10',
                                                               'PKT_PROFILE_ID':'MIRAI001',
                                                               'PKT_CTRL_NBR':'MC'+self.timeStamp,
                                                               'LANG_ID':'EN',
                                                               'PH1_FREIGHT_TERMS':'0',
                                                               'PHI_SPL_INSTR_NBR':'{:03}'.format(phIndex),
                                                               'PHI_SPL_INSTR_TYPE':'QV',
                                                               'PHI_SPL_INSTR_CODE':['01','08'],
                                                               'filename':fName})
                            if phItems['ss_'+ss.order_id].parse(ss) < 0:
                                self.parseErrors['ss_'+ss.order_id]=['PARSE ERROR: Unable to create PH item: "'+'ss_'+ss.order_id+'"']
                                del phItems['ss_'+ss.order_id]
                        if 'ss_'+ss.order_id in phItems:
                            itemIndex+=1
                            phItems['ss_'+ss.order_id].add_ss_detail(ss,itemIndex)
                            lineError=phItems['ss_'+ss.order_id].check_line()
                            if lineError != '':
                                # some missing information in this line item, generate an error
                                self.parseErrors['ss_'+ss.order_id]=[lineError]
        for key,phItem in phItems.iteritems():
            self.PH.append(phItem)
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
    
class UPS_CO_FILE(models.Model):
    """
    UPS Customer Order files
    """
    ups_pkt = models.ForeignKey(UPS_PKT)
    fileName=models.URLField(default='')
    contents=models.TextField(default='')
    
class UPS_PH(models.Model):
    '''
    UPS Pickticket Loop, contained in a UPS_PKT (Shipment Order)
    '''
    SEP='|' # record separator
    fileLineNo=0
    pkt=models.ForeignKey(UPS_PKT)
    filename=''
    REC_TYPE='PH'                   # 2 char
    WHSE=''                         # 3 char
    CO=''                           # 10 char
    DIV=''                          # 10 char
    STAT_CODE='10'                  # 2 char
    PKT_PROFILE_ID=''               # 10 char
    PKT_CTRL_NBR=''                 # 10 char
    PKT_NBR=''                          # opt. 11 char
    PKT_SFX=''                          # opt. 3 char
    ORD_NBR=''                          # opt. 3 char
    ORD_SFX=''                          # opt. 3 char
    ORD_TYPE=''                         #opt. 2 char
    SHIPTO=''                           # opt 10 char
    SHIPTO_NAME=''                  # 35 characters
    SHIPTO_CONTACT=''               # 30 characters
    SHIPTO_ADDR_1=''                    # opt. 75 char
    SHIPTO_ADDR_2=''                    # opt. 75 char
    SHIPTO_ADDR_3=''                    # opt. 75 char
    SHIPTO_CITY=''                      # opt. 40 char
    SHIPTO_STATE=''                     # opt. 3 char
    SHIPTO_ZIP=''                       # opt. 11 char
    SHIPTO_CNTRY=''                     # opt. 4 char
    TEL_NBR=''                          # opt. 15 char
    SOLDTO=''                           # opt. 10 char
    SOLDTO_NAME=''                      # opt. 35 char
    SOLDTO_ADDR_1=''                    # opt. 75 char
    SOLDTO_ADDR_2=''                    # opt. 75 char
    SOLDTO_ADDR_3=''                    # opt. 75 char
    SOLDTO_CITY=''                      # opt. 40 char
    SOLDTO_STATE=''                     # opt. 3 char
    SOLDTO_ZIP=''                       # opt. 11 char
    SOLDTO_CNTRY=''                     # opt. 4 char
    SHIP_VIA='UUS2'                     # opt. 4 char (Surepost=UUS2, UPS grnd=UU10)
    CARTON_LABEL_TYPE=''                # opt. 3 char
    NBR_OF_LABEL=''                     # opt. 3 char
    CONTNT_LABEL_TYPE=''                # opt. 3 char
    NBR_OF_CONTNT_LABEL=''              # opt. 3 char
    NBR_OF_PAKING_SLIPS=''              # opt. 3 char
    PACK_SLIP_TYPE=''                   # opt. 2 char
    LANG_ID=''                          # opt. 3 char
                                        # opt. PH1 section
    # PH1 section
    PH1_REC_TYPE='PH1'               # 2 char
    PH1_ACCT_RCVBL_ACCT_NBR=''          # opt. 10 char
    PH1_ACCT_RCVBL_CODE=''              # opt. 2 char
    PH1_CUST_PO_NBR=''                  # opt. 26 char
    PH1_PRTY_CODE=''                    # opt. 2 char
    PH1_PRTY_SFX=''                     # opt. 2 char
    PH1_ORD_DATE=''                     # opt. 14 char MM/DD/YY
    PH1_START_SHIP_DATE=''              # opt. 14 char MM/DD/YY
    PH1_STOP_SHIP_DATE=''               # opt. 14 char MM/DD/YY
    PH1_SCHED_DLVRY_DATE=''             # opt. 14 char MM/DD/YY
    PH1_EARLIEST_DLVRY_TIME=''          # opt. 4 char 1200??
    PH1_SCHED_DLVRY_DATE_END=''         # opt. 14 char MM/DD/YY
    PH1_RTE_GUIDE_NBR=''                # opt. 10 char
    PH1_CUST_RTE=''                     # opt. 1 char (Y,N)
    PH1_RTE_ATTR=''                     # opt. 30 char
    PH1_RTE_ID=''                       # opt. 10 char
    PH1_RTE_STOP_SEQ=''                 # opt. 5 char
    PH1_RTE_TO=''                       # opt. 10 char
    PH1_RTE_TYPE_1=''                   # opt. 2 char
    PH1_RTE_TYPE_2=''                   # opt. 2 char
    PH1_RTE_ZIP=''                      # opt. 11 char
    PH1_RTE_SWC_NBR=''                  # opt. 10 char
    PH1_CONSOL_NBR=''                   # opt. 10 char
    PH1_TOTAL_DLRS_UNDISC=''            # opt. 11 char
    PH1_TOTAL_DLRS_DISC=''              # opt. 11 char
    PH1_CURR_CODE=''                    # opt. 10 char
    PH1_PROD_VALUE=''                   # opt. 11 char
    PH1_FREIGHT_TERMS=''                # opt. 1 char 0 = Prepaid (Default),1 = Collect Billing,1 0:1,2 = Consignee Billing.3 = Third Party Billing
    PH1_MARK_FOR=''                     # opt. 25 char
    PH1_INCO_TERMS=''                   # opt. 3 char
    PH1_BILL_ACCT_NBR=''                # opt. 10 char
    PH1_COD_FUNDS=''                    # OPT. 1 CHAR
    PH1_INTL_GOODS_DESC=''              # opt. 35 char
    # PHI
    PHI_REC_TYPE='PHI'                  # 3 char
    PHI_SPL_INSTR_NBR=''                # 3 char
    PHI_SPL_INSTR_TYPE=''               # 2 char
    PHI_SPL_INSTR_CODE=[]               # 2 char list from: (01=shipment,02=delivery,04=exception,08=delivery failure)
    PHI_SPL_INSTR_DESC=''               # 135 char
    PHI_PKT_PROFILE_ID=''               # 10 char
#     # For Debugging 
#     REC_TYPE='PH'                   # 2 char
#     WHSE='WHSE'                         # 3 char
#     CO='CO'                           # 10 char
#     DIV='DIV'                          # 10 char
#     STAT_CODE='10'                  # 2 char
#     PKT_PROFILE_ID='PKT_PROFILE_ID'               # 10 char
#     PKT_CTRL_NBR='PKT_CTRL_NBR'                 # 10 char
#     PKT_NBR='PKT_NBR'                          # opt. 11 char
#     PKT_SFX='PKT_SFX'                          # opt. 3 char
#     ORD_NBR='ORD_NBR'                          # opt. 3 char
#     ORD_SFX='ORD_SFX'                          # opt. 3 char
#     ORD_TYPE='ORD_TYPE'                         #opt. 2 char
#     SHIPTO='SHIPTO'                           # opt 10 char
#     SHIPTO_NAME='SHIPTO_NAME'                  # 35 characters
#     SHIPTO_CONTACT=''               # 30 characters
#     SHIPTO_ADDR_1='SHIPTO_ADDR_1'                    # opt. 75 char
#     SHIPTO_ADDR_2='SHIPTO_ADDR_2'                    # opt. 75 char
#     SHIPTO_ADDR_3='SHIPTO_ADDR_3'                    # opt. 75 char
#     SHIPTO_CITY='SHIPTO_CITY'                      # opt. 40 char
#     SHIPTO_STATE='SHIPTO_STATE'                     # opt. 3 char
#     SHIPTO_ZIP='SHIPTO_ZIP'                       # opt. 11 char
#     SHIPTO_CNTRY='SHIPTO_CNTRY'                     # opt. 4 char
#     TEL_NBR='TEL_NBR'                          # opt. 15 char
#     SOLDTO='SOLDTO'                           # opt. 10 char
#     SOLDTO_NAME='SOLDTO_NAME'                      # opt. 35 char
#     SOLDTO_ADDR_1='SOLDTO_ADDR_1'                    # opt. 75 char
#     SOLDTO_ADDR_2='SOLDTO_ADDR_2'                    # opt. 75 char
#     SOLDTO_ADDR_3='SOLDTO_ADDR_3'                    # opt. 75 char
#     SOLDTO_CITY='SOLDTO_CITY'                      # opt. 40 char
#     SOLDTO_STATE='SOLDTO_STATE'                     # opt. 3 char
#     SOLDTO_ZIP='SOLDTO_ZIP'                       # opt. 11 char
#     SOLDTO_CNTRY='SOLDTO_CNTRY'                     # opt. 4 char
#     SHIP_VIA='SHIP_VIA'                     # opt. 4 char (Surepost=UUS2, UPS grnd=UU10)
#     CARTON_LABEL_TYPE='CARTON_LABEL_TYPE'                # opt. 3 char
#     NBR_OF_LABEL='NBR_OF_LABEL'                     # opt. 3 char
#     CONTNT_LABEL_TYPE='CONTNT_LABEL_TYPE'                # opt. 3 char
#     NBR_OF_CONTNT_LABEL='NBR_OF_CONTNT_LABEL'              # opt. 3 char
#     NBR_OF_PAKING_SLIPS='NPS'              # opt. 3 char
#     PACK_SLIP_TYPE='PACK_SLIP_TYPE'                   # opt. 2 char
#     LANG_ID='LANG_ID'                          # opt. 3 char
#                                         # opt. PH1 section
#     # PH1 section
#     PH1_REC_TYPE='PH1'               # 2 char
#     PH1_ACCT_RCVBL_ACCT_NBR='ACTREC_NBR'          # opt. 10 char
#     PH1_ACCT_RCVBL_CODE=''              # opt. 2 char
#     PH1_CUST_PO_NBR=''                  # opt. 26 char
#     PH1_PRTY_CODE=''                    # opt. 2 char
#     PH1_PRTY_SFX=''                     # opt. 2 char
#     PH1_ORD_DATE=''                     # opt. 14 char MM/DD/YY
#     PH1_START_SHIP_DATE=''              # opt. 14 char MM/DD/YY
#     PH1_STOP_SHIP_DATE=''               # opt. 14 char MM/DD/YY
#     PH1_SCHED_DLVRY_DATE=''             # opt. 14 char MM/DD/YY
#     PH1_EARLIEST_DLVRY_TIME=''          # opt. 4 char 1200??
#     PH1_SCHED_DLVRY_DATE_END=''         # opt. 14 char MM/DD/YY
#     PH1_RTE_GUIDE_NBR=''                # opt. 10 char
#     PH1_CUST_RTE=''                     # opt. 1 char (Y,N)
#     PH1_RTE_ATTR=''                     # opt. 30 char
#     PH1_RTE_ID=''                       # opt. 10 char
#     PH1_RTE_STOP_SEQ=''                 # opt. 5 char
#     PH1_RTE_TO=''                       # opt. 10 char
#     PH1_RTE_TYPE_1=''                   # opt. 2 char
#     PH1_RTE_TYPE_2=''                   # opt. 2 char
#     PH1_RTE_ZIP=''                      # opt. 11 char
#     PH1_RTE_SWC_NBR=''                  # opt. 10 char
#     PH1_CONSOL_NBR=''                   # opt. 10 char
#     PH1_TOTAL_DLRS_UNDISC=''            # opt. 11 char
#     PH1_TOTAL_DLRS_DISC=''              # opt. 11 char
#     PH1_CURR_CODE=''                    # opt. 10 char
#     PH1_PROD_VALUE=''                   # opt. 11 char
#     PH1_FREIGHT_TERMS=''                # opt. 1 char 0 = Prepaid (Default),1 = Collect Billing,1 0:1,2 = Consignee Billing.3 = Third Party Billing
#     PH1_MARK_FOR=''                     # opt. 25 char
#     PH1_INCO_TERMS=''                   # opt. 3 char
#     PH1_BILL_ACCT_NBR=''                # opt. 10 char
#     PH1_COD_FUNDS=''                    # OPT. 1 CHAR
#     PH1_INTL_GOODS_DESC=''              # opt. 35 char
#                                         # opt. PH2 section
#                                         # opt. PH3 section
#     PHI_REC_TYPE='PHI'                  # 3 char
#     PHI_SPL_INSTR_NBR=''                # 3 char
#     PHI_SPL_INSTR_TYPE=''               # 2 char
#     PHI_SPL_INSTR_CODE=''               # 2 char (01=shipment,02=delivery,04=exception,08=delivery failure)
#     PHI_SPL_INSTR_DESC=''               # 135 char
#     PHI_PKT_PROFILE_ID=''               # 10 char
    PD=[]                           # holds detail loop items

    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(UPS_PH,self).__init__()
        self.PD=[] # need to create this here rather than use a default value in instance var init section
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'SEP':
                    self.SEP=value
                if key == 'filename':
                    self.filename=value
                if key == 'fileLineNo':
                    self.fileLineNo=value
                # PH
                if key == 'REC_TYPE':
                    self.REC_TYPE=value[:3]
                if key == 'WHSE':
                    self.WHSE=value[:3]
                if key == 'CO':
                    self.CO=value[:10]
                if key == 'DIV':
                    self.DIV=value[:10]
                if key == 'STAT_CODE':
                    self.STAT_CODE=value[:2]
                if key == 'PKT_PROFILE_ID':
                    self.PKT_PROFILE_ID=value[:10]
                if key == 'PKT_CTRL_NBR':
                    self.PKT_CTRL_NBR=value[:10]
                if key == 'PKT_NBR':
                    self.PKT_NBR=value[:11]
                if key == 'PKT_SFX':
                    self.PKT_SFX=value[:3]
                if key == 'ORD_NBR':
                    self.ORD_NBR=value[:8]
                if key == 'ORD_SFX':
                    self.ORD_SFX=value[:3]
                if key == 'ORD_TYPE':
                    self.ORD_TYPE=value[:2]
                if key == 'SHIPTO':
                    self.SHIPTO=value[:10]
                if key == 'SHIPTO_NAME':
                    self.SHIPTO_NAME=value[:35]
                if key == 'SHIPTO_CONTACT':
                    self.SHIPTO_CONTACT=value[:30]
                if key == 'SHIPTO_ADDR_1':
                    self.SHIPTO_ADDR_1=value[:75]
                if key == 'SHIPTO_ADDR_2':
                    self.SHIPTO_ADDR_2=value[:75]
                if key == 'SHIPTO_ADDR_3':
                    self.SHIPTO_ADDR_3=value[:75]
                if key == 'SHIPTO_CITY':
                    self.SHIPTO_CITY=value[:40]
                if key == 'SHIPTO_STATE':
                    self.SHIPTO_STATE=value[:3]
                if key == 'SHIPTO_ZIP':
                    self.SHIPTO_ZIP=value[:11]
                if key == 'SHIPTO_CNTRY':
                    self.SHIPTO_CNTRY=value[:4]
                if key == 'TEL_NBR':
                    self.TEL_NBR=value[:15]
                if key == 'SOLDTO':
                    self.SOLDTO=value[:10]
                if key == 'SOLDTO_NAME':
                    self.SOLDTO_NAME=value[:35]
                if key == 'SOLDTO_ADDR_1':
                    self.SOLDTO_ADDR_1=value[:75]
                if key == 'SOLDTO_ADDR_2':
                    self.SOLDTO_ADDR_2=value[:75]
                if key == 'SOLDTO_ADDR_3':
                    self.SOLDTO_ADDR_3=value[:75]
                if key == 'SOLDTO_CITY':
                    self.SOLDTO_CITY=value[:40]
                if key == 'SOLDTO_STATE':
                    self.SOLDTO_STATE=value[:3]
                if key == 'SOLDTO_ZIP':
                    self.SOLDTO_ZIP=value[:11]
                if key == 'SOLDTO_CNTRY':
                    self.SOLDTO_CNTRY=value[:4]
                if key == 'SHIP_VIA':
                    self.SHIP_VIA=value[:4]
                if key == 'CARTON_LBL_TYPE':
                    self.CARTON_LABEL_TYPE=value[:3]
                if key == 'NBR_OF_LABEL':
                    self.NBR_OF_LABEL=value[:3]
                if key == 'CONTNT_LABEL_TYPE':
                    self.CONTNT_LABEL_TYPE=value[:3]
                if key == 'NBR_CONTNT_LABEL':
                    self.NBR_OF_CONTNT_LABEL=value[:3]
                if key == 'NBR_OF_PKNG_SLIPS':
                    self.NBR_OF_PAKING_SLIPS=value[:3]
                if key == 'PACK_SLIP_TYPE':
                    self.PACK_SLIP_TYPE=value[:2]
                if key == 'LANG_ID':
                    self.LANG_ID=value[:3]
                # PH1
                if key == 'PH1_REC_TYPE':
                    self.PH1_REC_TYPE=value[:3]
                if key == 'PH1_ACCT_RCVBL_ACCT_NBR':
                    self.PH1_ACCT_RCVBL_ACCT_NBR=value[:10]
                if key == 'PH1_ACCT_RCVBL_CODE':
                    self.PH1_ACCT_RCVBL_CODE=value[:2]
                if key == 'PH1_CUST_PO_NBR':
                    self.PH1_CUST_PO_NBR=value[:26]
                if key == 'PH1_PRTY_CODE':
                    self.PH1_PRTY_CODE=value[:2]
                if key == 'PH1_PRTY_SFX':
                    self.PH1_PRTY_SFX=value[:2]
                if key == 'PH1_ORD_DATE':
                    self.PH1_ORD_DATE=value[:14]
                if key == 'PH1_START_SHIP_DATE':
                    self.PH1_START_SHIP_DATE=value[:14]
                if key == 'PH1_STOP_SHIP_DATE':
                    self.PH1_STOP_SHIP_DATE=value[:14]
                if key == 'PH1_SCHED_DLVRY_DATE':
                    self.PH1_SCHED_DLVRY_DATE=value[:14]
                if key == 'PH1_EARLIEST_DLVRY_TIME':
                    self.PH1_EARLIEST_DLVRY_TIME=value[:4]
                if key == 'PH1_SCHED_DLVRY_DATE_END':
                    self.PH1_SCHED_DLVRY_DATE_END=value[:14]
                if key == 'PH1_RTE_GUIDE_NBR':
                    self.PH1_RTE_GUIDE_NBR=value[:10]
                if key == 'PH1_CUST_RTE':
                    self.PH1_CUST_RTE=value[:1]
                if key == 'PH1_RTE_ATTR':
                    self.PH1_RTE_ATTR=value[:30]
                if key == 'PH1_RTE_ID':
                    self.PH1_RTE_ID=value[:10]
                if key == 'PH1_RTE_STOP_SEQ':
                    self.PH1_RTE_STOP_SEQ=value[:5]
                if key == 'PH1_RTE_TO':
                    self.PH1_RTE_TO=value[:10]
                if key == 'PH1_RTE_TYPE_1':
                    self.PH1_RTE_TYPE_1=value[:2]
                if key == 'PH1_RTE_TYPE_2':
                    self.PH1_RTE_TYPE_2=value[:2]
                if key == 'PH1_RTE_ZIP':
                    self.PH1_RTE_ZIP=value[:11]
                if key == 'PH1_RTE_SWC_NBR':
                    self.PH1_RTE_SWC_NBR=value[:10]
                if key == 'PH1_CONSOL_NBR':
                    self.PH1_CONSOL_NBR=value[:10]
                if key == 'PH1_TOTAL_DLRS_UNDISC':
                    self.PH1_TOTAL_DLRS_UNDISC=value[:11]
                if key == 'PH1_TOTAL_DLRS_DISC':
                    self.PH1_TOTAL_DLRS_DISC=value[:11]
                if key == 'PH1_CURR_CODE':
                    self.PH1_CURR_CODE=value[:10]
                if key == 'PH1_PROD_VALUE':
                    self.PH1_PROD_VALUE=value[:11]
                if key == 'PH1_FREIGHT_TERMS':
                    self.PH1_FREIGHT_TERMS=value[:1]
                if key == 'PH1_MARK_FOR':
                    self.PH1_MARK_FOR=value[:25]
                if key == 'PH1_INCO_TERMS':
                    self.PH1_INCO_TERMS=value[:3]
                if key == 'PH1_BILL_ACCT_NBR':
                    self.PH1_BILL_ACCT_NBR=value[:10]
                if key == 'PH1_COD_FUNDS':
                    self.PH1_COD_FUNDS=value[:1]
                if key == 'PH1_INTL_GOODS_DESC':
                    self.PH1_INTL_GOODS_DESC=value[:35]
                #PHI
                if key == 'PHI_REC_TYPE':
                    self.PHI_REC_TYPE=value[:3]
                if key == 'PHI_SPL_INSTR_NBR':
                    self.PHI_SPL_INSTR_NBR=value[:3]
                if key == 'PHI_SPL_INSTR_TYPE':
                    self.PHI_SPL_INSTR_TYPE=value[:2]
                if key == 'PHI_SPL_INSTR_CODE':
                    self.PHI_SPL_INSTR_CODE=value[:2]
                if key == 'PHI_SPL_INSTR_DESC':
                    self.PHI_SPL_INSTR_DESC=value[:135]
                if key == 'PHI_PKT_PROFILE_ID':
                    self.PHI_PKT_PROFILE_ID=value[:10]
                #PD
                if key == 'PD':
                    self.PD=value # List of UPS_PD objects
                
        else:
            raise TypeError("Invalid data type passed to UPS_PH __init__.  Should be a dictionary\n")
    
    def __str__(self):
        return 'UPS_PH instance ['+self.PKT_CTRL_NBR+']'
    
    def parse(self,phItem):
        self.fromFile=phItem.fromFile
        self.fileLineNo=phItem.fileLineNo
        if phItem.type == 'Mirai':
            try:
                self.PH1_ORD_DATE=phItem.v_date_purchased[:10]
                self.PH1_START_SHIP_DATE=phItem.v_date_purchased[:10]
                self.PH1_START_SHIP_DATE=phItem.v_date_purchased[:10]
                self.PH1_CUST_PO_NBR=phItem.v_orders_id
                self.TEL_NBR=phItem.v_customers_telephone
                self.SHIPTO_CONTACT=phItem.v_customers_email_address
                self.SHIPTO=phItem.v_customers_name
                self.SHIPTO_NAME=phItem.v_customers_name
                self.SHIPTO_ADDR_1=phItem.v_customers_street_address
                self.SHIPTO_ADDR_2=phItem.v_customers_suburb
                self.SHIPTO_CITY=phItem.v_customers_city
                self.SHIPTO_ZIP=phItem.v_customers_postcode
                self.SHIPTO_CNTRY=phItem.v_customers_country
                self.ORD_TYPE='ZE'
                self.SHIP_VIA=self.parse_ship_via('none')
            except:
                return(-1)
        if phItem.type == 'Amazon':
            try:
                self.PH1_ORD_DATE=phItem.purchase_date[:10]
                self.PH1_START_SHIP_DATE=phItem.purchase_date[:10]
                self.PH1_START_SHIP_DATE=phItem.purchase_date[:10]
                self.PH1_CUST_PO_NBR=phItem.order_id
                self.TEL_NBR=phItem.buyer_phone_number
                self.SHIPTO_CONTACT=phItem.buyer_email
                self.SHIPTO_NAME=phItem.recipient_name
                self.SHIPTO_ADDR_1=phItem.ship_address_1
                self.SHIPTO_ADDR_2=phItem.ship_address_2
                self.SHIPTO_CITY=phItem.ship_city
                self.SHIPTO_STATE=phItem.ship_state
                self.SHIPTO_ZIP=phItem.ship_postal_code
                self.SHIPTO_CNTRY=phItem.ship_country
                self.ORD_TYPE='AM'
                self.SHIP_VIA=self.parse_ship_via(phItem.ship_service_level)
                self.PHI_SPL_INSTR_DESC=phItem.buyer_email
            except:
                return(-1)
        if phItem.type == 'ShipStation':
            try:
                self.PH1_ORD_DATE=phItem.purchase_date[:10]
                self.PH1_START_SHIP_DATE=phItem.purchase_date[:10]
                self.PH1_START_SHIP_DATE=phItem.purchase_date[:10]
                self.PH1_CUST_PO_NBR=phItem.order_id
                self.SHIPTO_NAME=phItem.recipient_name
                self.SHIPTO_ADDR_1=phItem.ship_address_1
                self.SHIPTO_ADDR_2=phItem.ship_address_2
                self.SHIPTO_ADDR_3=phItem.ship_address_3
                self.SHIPTO_CITY=phItem.ship_city
                self.SHIPTO_STATE=phItem.ship_state
                self.SHIPTO_ZIP=phItem.ship_postal_code
                self.SHIPTO_CNTRY=phItem.ship_country
                self.PACK_SLIP_TYPE=phItem.pack_slip_type
                self.CARRIER=phItem.carrier
                self.ORD_TYPE=phItem.order_type[:2]
                self.SHIP_VIA=self.parse_ship_via(phItem.ship_service_level)
                self.PHI_SPL_INSTR_DESC=phItem.buyer_email
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
    
    def add_mirai_detail(self,phItem,index):
        pd=UPS_PD({'CUST_SKU':phItem.v_products_model,
                   'SIZE_DESC':phItem.v_products_name[:15],
                   'ORIG_ORD_QTY':'1',
                   'PKT_SEQ_NBR':'{:09}'.format(index),
                   'STAT_CODE':'00',
                   'fileLineNo':phItem.fileLineNo,
                   'filename':phItem.filename})
        self.PD.append(pd)
    
    def add_amazon_detail(self,phItem,index):
        pd=UPS_PD({'CUST_SKU':phItem.sku,
                   'SIZE_DESC':phItem.product_name[:15],
                   'ORIG_ORD_QTY':phItem.quantity_purchased,
                   'ORIG_PKT_QTY':phItem.quantity_purchased,
                   'PKT_SEQ_NBR':'{:09}'.format(index),
                   'STAT_CODE':'00',
                   'fileLineNo':phItem.fileLineNo,
                   'filename':phItem.filename})
        self.PD.append(pd)
    
    def add_ss_detail(self,phItem,index):
        pd=UPS_PD({'CUST_SKU':phItem.sku,
                   'SIZE_DESC':phItem.product_name[:15],
                   'ORIG_ORD_QTY':phItem.quantity_purchased,
                   'ORIG_PKT_QTY':phItem.quantity_purchased,
                   'PKT_SEQ_NBR':'{:09}'.format(index),
                   'STAT_CODE':'00',
                   'fileLineNo':phItem.fileLineNo,
                   'filename':phItem.filename})
        self.PD.append(pd)
    
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

class UPS_PD(models.Model):
    '''
    UPS Detail Loop, contained in a UPS_PH (Pickticket loop)
    '''
    SEP='|' # record separator
    fileLineNo=0
    ph=models.ForeignKey(UPS_PH)
    filename=''
    
    # PD section
    # key for PD hash tables is PKT_SEQ_NBR
    REC_TYPE='PD'                   # 2 char
    PKT_SEQ_NBR=''                  # 9 char
    STAT_CODE=''                    # 2 char
    PKT_PROFILE_ID=''                   # opt. 2 char
    SEASON=''                           # opt. 2 char
    SEASON_YR=''                        # opt. 2 char
    STYLE=''                            # opt. 8 char
    STYLE_SFX=''                        # opt. 8 char
    COLOR=''                            # opt. 4 char
    COLOR_SFX=''                        # opt. 2 char
    SEC_DIM=''                          # opt. 3 char
    QUAL=''                             # opt. 1 char
    SIZE_RANGE_CODE=''                  # opt. 4 char
    SIZE_REL_POSN_IN_TABLE=''           # opt. 2 char
    SIZE_DESC=''                        # opt. 15 char
    ORIG_ORD_QTY=''                 # 9 char
    ORIG_PKT_QTY=''                 # 9 char
    CANCEL_QTY=''                       # opt. 9 char
    CUBE_MULT_QTY=''                    # opt. 9 char
    BACK_ORD_QTY=''                     # opt. 9 char
    CUST_SKU=''                         # opt. 20 char
#     #For Debugging
#     REC_TYPE='PD'                   # 2 char
#     PKT_SEQ_NBR='PKT_SEQ_NBR'                  # 9 char
#     STAT_CODE='STAT_CODE'                    # 2 char
#     PKT_PROFILE_ID='PKT_PROFILE_ID'                   # opt. 2 char
#     SEASON='SS'                           # opt. 2 char
#     SEASON_YR='SY'                        # opt. 2 char
#     STYLE='STYLE'                            # opt. 8 char
#     STYLE_SFX='STLSFX'                        # opt. 8 char
#     COLOR='COLR'                            # opt. 4 char
#     COLOR_SFX='CS'                        # opt. 2 char
#     SEC_DIM=''                          # opt. 3 char
#     QUAL=''                             # opt. 1 char
#     SIZE_RANGE_CODE=''                  # opt. 4 char
#     SIZE_REL_POSN_IN_TABLE=''           # opt. 2 char
#     SIZE_DESC=''                        # opt. 15 char
#     ORIG_ORD_QTY=''                     # 9 char
#     ORIG_PKT_QTY=''                     # 9 char
#     CANCEL_QTY=''                       # opt. 9 char
#     CUBE_MULT_QTY=''                    # opt. 9 char
#     BACK_ORD_QTY=''                     # opt. 9 char
#     CUST_SKU=''                         # opt. 20 char
                                        # opt. PD1 section
                                        # opt. PD2 section
                                        # opt. PD3 section
                                        # opt. PDI section

    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(UPS_PD,self).__init__()
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'SEP':
                    self.SEP=value
                if key == 'fileLineNo':
                    self.fileLineNo=value
                if key == 'filename':
                    self.filename=value
                #PD
                if key == 'REC_TYPE':
                    self.REC_TYPE=value
                if key == 'PKT_SEQ_NBR':
                    self.PKT_SEQ_NBR=value
                if key == 'STAT_CODE':
                    self.STAT_CODE=value
                if key == 'PKT_PROFILE_ID':
                    self.PKT_PROFILE_ID=value
                if key == 'SEASON':
                    self.SEASON=value
                if key == 'SEASON_YR':
                    self.SEASON_YR=value
                if key == 'STYLE':
                    self.STYLE=value
                if key == 'STYLE':
                    self.STYLE_SFX=value
                if key == 'COLOR':
                    self.COLOR=value
                if key == 'COLOR_SFX':
                    self.COLOR_SFX=value
                if key == 'SEC_DIM':
                    self.SEC_DIM=value
                if key == 'QUAL':
                    self.QUAL=value
                if key == 'SIZE_RANGE_CODE':
                    self.SIZE_RANGE_CODE=value
                if key == 'SIZE_REL_POSN_IN_TABLE':
                    self.SIZE_REL_POSN_IN_TABLE=value
                if key == 'SIZE_DESC':
                    self.SIZE_DESC=value
                if key == 'ORIG_ORD_QTY':
                    self.ORIG_ORD_QTY=value
                if key == 'ORIG_PKT_QTY':
                    self.ORIG_PKT_QTY=value
                if key == 'CANCEL_QTY':
                    self.CANCEL_QTY=value
                if key == 'CUBE_MULT_QTY':
                    self.CUBE_MULT_QTY=value
                if key == 'BACK_ORD_QTY':
                    self.BACK_ORD_QTY=value
                if key == 'CUST_SKU':
                    self.CUST_SKU=value
        else:
            raise TypeError("Invalid data type passed to UPS_PD __init__.  Should be a dictionary\n")
    
    def __str__(self):
        return "UPS_PD instance"
    
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
    
class SS_CO(models.Model):
    '''
    Ship Station consolidated customer orders
    Strive to maintain compatibility with Amazon_CO
    '''
    headers=[] # holds headers in order read from file
    pkt=models.ForeignKey(UPS_PKT, null=True)
    fromFile=models.URLField(default='')
    fileLineNo=0
    filename=models.URLField(default='')
    type=models.CharField(max_length=20, default='ShipStation')
    sku=models.CharField(max_length=50, default='')
    product_name=models.CharField(max_length=100, default='')
    order_id=models.CharField(max_length=50, default='')
    order_type=models.CharField(max_length=50, default='')
    quantity_purchased=models.IntegerField(default=0)
    purchase_date=models.DateField()
    ship_service_level=models.CharField(max_length=50, default='')
    recipient_name=models.CharField(max_length=100, default='')
    buyer_email=models.EmailField(max_length=254, default='')
    # TODO: RG 09/09/14 add in address parser module
    ship_address_1=models.CharField(max_length=200, default='')
    ship_address_2=models.CharField(max_length=200, default='')
    ship_address_3=models.CharField(max_length=200, default='')
    ship_city=models.CharField(max_length=100, default='')
    ship_state=models.CharField(max_length=20, default='')
    ship_postal_code=models.CharField(max_length=20, default='')
    ship_country=models.CharField(max_length=50, default='')
    # Additional fields not used by Amazon
    carrier=models.CharField(max_length=20, default='')
    pack_slip_type=models.CharField(max_length=20, default='')
    intl_terms_of_sale=models.CharField(max_length=100, default='')
    
    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(SS_CO,self).__init__()
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'headers':
                    self.headers=value
                if key == 'fileLineNo':
                    self.fileLineNo=value
                if key == 'filename':
                    self.filename=value
                if key == 'sku':
                    self.sku=value
                if key == 'product-name':
                    self.product_name=value
                if key == 'order-id':
                    self.order_id=value
                if key == 'order-type':
                    self.order_type=value
                if key == 'quantity-purchased':
                    self.quantity_purchased=value
                if key == 'purchase-date':
                    self.purchase_date=value
                if key == 'ship-service-level':
                    self.ship_service_level=value
                if key == 'recipient-name':
                    self.recipient_name=value
                if key == 'buyer-email':
                    self.buyer_email=value
                if key == 'ship-address-1':
                    self.ship_address_1=value
                if key == 'ship-address-2':
                    self.ship_address_2=value
                if key == 'ship-address-3':
                    self.ship_address_3=value
                if key == 'ship-city':
                    self.ship_city=value
                if key == 'ship-state':
                    self.ship_state=value
                if key == 'ship-postal-code':
                    self.ship_postal_code=value
                if key == 'ship-country':
                    self.ship_country=value
                if key == 'carrier':
                    self.carrier=value
                if key == 'pack-slip-type':
                    self.pack_slip_type=value
                if key == 'intl-terms-of-sale':
                    self.intl_terms_of_sale=value
        else:
            raise TypeError("Invalid data type passed to SS_CO __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "SS_CO instance"
    
    def read_line(self,line):
        res=re.split(r'\t', line.rstrip())
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
                self.product_name=res[self.headers.index(item)]
            if item == 'order-id':
                self.order_id=res[self.headers.index(item)]
            if item == 'order-type':
                self.order_type=res[self.headers.index(item)]
            if item == 'quantity-purchased':
                self.quantity_purchased=res[self.headers.index(item)]
            if item == 'purchase-date':
                self.purchase_date=res[self.headers.index(item)]
            if item == 'ship-service-level':
                self.ship_service_level=res[self.headers.index(item)]
            if item == 'recipient-name':
                self.recipient_name=res[self.headers.index(item)]
            if item == 'buyer-email':
                self.buyer_email=res[self.headers.index(item)]
            if item == 'ship-address-1':
                self.ship_address_1=res[self.headers.index(item)]
            if item == 'ship-address-2':
                self.ship_address_2=res[self.headers.index(item)]
            if item == 'ship-address-3':
                self.ship_address_3=res[self.headers.index(item)]
            if item == 'ship-city':
                self.ship_city=res[self.headers.index(item)]
            if item == 'ship-state':
                self.ship_state=res[self.headers.index(item)]
            if item == 'ship-postal-code':
                self.ship_postal_code=res[self.headers.index(item)]
            if item == 'ship-country':
                self.ship_country=res[self.headers.index(item)]
            if item == 'carrier':
                self.carrier=res[self.headers.index(item)]
            if item == 'pack-slip-type':
                self.pack_slip_type=res[self.headers.index(item)]
            if item == 'intl-terms-of-sale':
                self.intl_terms_of_sale=res[self.headers.index(item)]
        return(0)
    
    def read_header(self,line):
        self.headers=re.split(r'\t', line.rstrip())
    
class Amazon_CO(models.Model):
    '''
    Amazon customer order
    '''
    headers=[] # holds headers in order read from file
    pkt=models.ForeignKey(UPS_PKT, null=True)
    fromFile=models.URLField(default='')
    fileLineNo=0
    filename=models.URLField(default='')
    type=models.CharField(max_length=20, default='Amazon')
    buyer_name=models.CharField(max_length=100, default='')
    buyer_email=models.EmailField(max_length=254, default='')
    sku=models.CharField(max_length=50, default='')
    product_name=models.CharField(max_length=100, default='')
    purchase_date=models.DateField()
    payments_date=models.DateField()
    order_id=models.CharField(max_length=50, default='')
    order_item_id=models.CharField(max_length=50, default='')
    external_order_id=models.CharField(max_length=50, default='')
    quantity_purchased=models.IntegerField(default=0)
    currency=models.CharField(max_length=50, default='')
    item_price=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    item_promotion_discount=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    item_promotion_id=models.CharField(max_length=100, default='')
    ship_promotion_discount=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ship_promotion_id=models.CharField(max_length=100, default='')
    item_tax=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_price=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_tax=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ship_service_level=models.CharField(max_length=50, default='')
    recipient_name=models.CharField(max_length=100, default='')
    # TODO: RG 09/09/14 add in address parser module
    ship_address_1=models.CharField(max_length=200, default='')
    ship_address_2=models.CharField(max_length=200, default='')
    ship_address_3=models.CharField(max_length=200, default='')
    ship_city=models.CharField(max_length=200, default='')
    ship_state=models.CharField(max_length=20, default='')
    ship_postal_code=models.CharField(max_length=20, default='')
    ship_country=models.CharField(max_length=20, default='')
    ship_phone_number=models.CharField(max_length=50, default='')
    delivery_start_date=models.DateField()
    delivery_end_date=models.DateField()
    delivery_time_zone=models.CharField(max_length=50, default='America/New_York')
    delivery_Instructions=models.CharField(max_length=500, default='')
    sales_channel=models.CharField(max_length=50, default='')
    order_channel=models.CharField(max_length=50, default='')
    order_channel_instance=models.CharField(max_length=50, default='')
    tax_location_code=models.CharField(max_length=200, default='')
    tax_location_city=models.CharField(max_length=200, default='')
    tax_location_county=models.CharField(max_length=50, default='')
    tax_location_state=models.CharField(max_length=20, default='')
    per_unit_item_taxable_district=models.CharField(max_length=200, default='')
    per_unit_item_taxable_city=models.CharField(max_length=200, default='')
    per_unit_item_taxable_county=models.CharField(max_length=200, default='')
    per_unit_item_taxable_state=models.CharField(max_length=20, default='')
    per_unit_item_non_taxable_district=models.CharField(max_length=200, default='')
    per_unit_item_non_taxable_city=models.CharField(max_length=200, default='')
    per_unit_item_non_taxable_county=models.CharField(max_length=200, default='')
    per_unit_item_non_taxable_state=models.CharField(max_length=20, default='')
    per_unit_item_zero_rated_district=models.CharField(max_length=200, default='')
    per_unit_item_zero_rated_city=models.CharField(max_length=200, default='')
    per_unit_item_zero_rated_county=models.CharField(max_length=200, default='')
    per_unit_item_zero_rated_state=models.CharField(max_length=20, default='')
    per_unit_item_tax_collected_district=models.CharField(max_length=200, default='')
    per_unit_item_tax_collected_city=models.CharField(max_length=200, default='')
    per_unit_item_tax_collected_county=models.CharField(max_length=200, default='')
    per_unit_item_tax_collected_state=models.CharField(max_length=20, default='')
    per_unit_shipping_taxable_district=models.CharField(max_length=200, default='')
    per_unit_shipping_taxable_city=models.CharField(max_length=200, default='')
    per_unit_shipping_taxable_county=models.CharField(max_length=200, default='')
    per_unit_shipping_taxable_state=models.CharField(max_length=20, default='')
    per_unit_shipping_non_taxable_district=models.CharField(max_length=200, default='')
    per_unit_shipping_non_taxable_city=models.CharField(max_length=200, default='')
    per_unit_shipping_non_taxable_county=models.CharField(max_length=200, default='')
    per_unit_shipping_non_taxable_state=models.CharField(max_length=20, default='')
    per_unit_shipping_zero_rated_district=models.CharField(max_length=200, default='')
    per_unit_shipping_zero_rated_city=models.CharField(max_length=200, default='')
    per_unit_shipping_zero_rated_county=models.CharField(max_length=200, default='')
    per_unit_shipping_zero_rated_state=models.CharField(max_length=20, default='')
    per_unit_shipping_tax_collected_district=models.CharField(max_length=200, default='')
    per_unit_shipping_tax_collected_state=models.CharField(max_length=20, default='')
    per_unit_shipping_tax_collected_county=models.CharField(max_length=200, default='')
    per_unit_shipping_tax_collected_state=models.CharField(max_length=200, default='')

    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(Amazon_CO,self).__init__()
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'headers':
                    self.headers=value
                if key == 'fileLineNo':
                    self.fileLineNo=value
                if key == 'filename':
                    self.filename=value
                if key == 'buyer-name':
                    self.buyer_name=value
                if key == 'buyer-phone-number':
                    self.buyer_phone_number=value
                if key == 'buyer-email':
                    self.buyer_email=value
                if key == 'sku':
                    self.sku=value
                if key == 'product-name':
                    self.product_name=value
                if key == 'purchase-date':
                    self.purchase_date=value
                if key == 'payments-date':
                    self.payments_date=value
                if key == 'order-id':
                    self.order_id=value
                if key == 'order-item-id':
                    self.order_item_id=value
                if key == 'external-order-id':
                    self.external_order_id=value
                if key == 'quantity-purchased':
                    self.quantity_purchased=value
                if key == 'currency':
                    self.currency=value
                if key == 'item-price':
                    self.item_price=value
                if key == 'item-promotion-discount':
                    self.item_promotion_discount=value
                if key == 'item-promotion-id':
                    self.item_promotion_id=value
                if key == 'ship-promotion-discount':
                    self.ship_promotion_discount=value
                if key == 'ship-promotion-id':
                    self.ship_promotion_id=value
                if key == 'item-tax':
                    self.item_tax=value
                if key == 'shipping-price':
                    self.shipping_price=value
                if key == 'shipping-tax':
                    self.shipping_tax=value
                if key == 'ship-service-level':
                    self.ship_service_level=value
                if key == 'recipient-name':
                    self.recipient_name=value
                if key == 'ship-address-1':
                    self.ship_address_1=value
                if key == 'ship-address-2':
                    self.ship_address_2=value
                if key == 'ship-address-3':
                    self.ship_address_3=value
                if key == 'ship-city':
                    self.ship_city=value
                if key == 'ship-state':
                    self.ship_state=value
                if key == 'ship-postal-code':
                    self.ship_postal_code=value
                if key == 'ship-country':
                    self.ship_country=value
                if key == 'ship-phone-number':
                    self.ship_phone_number=value
                if key == 'delivery-start-date':
                    self.delivery_start_date=value
                if key == 'delivery-end-date':
                    self.delivery_end_date=value
                if key == 'delivery-time-zone':
                    self.delivery_time_zone=value
                if key == 'delivery-instructions':
                    self.delivery_Instructions=value
                if key == 'sales-channel':
                    self.sales_channel=value
                if key == 'order-channel':
                    self.order_channel=value
                if key == 'order-channel-instance':
                    self.order_channel_instance=value
                if key == 'tax-location-code':
                    self.tax_location_code=value
                if key == 'tax-location-city':
                    self.tax_location_city=value
                if key == 'tax-location-county':
                    self.tax_location_county=value
                if key == 'tax-location-state':
                    self.tax_location_state=value
                if key == 'per-unit-item-taxable-district':
                    self.per_unit_item_taxable_district=value
                if key == 'per-unit-item-taxable-city':
                    self.per_unit_item_taxable_city=value
                if key == 'per-unit-item-taxable-county':
                    self.per_unit_item_taxable_county=value
                if key == 'per-unit-item-taxable-state':
                    self.per_unit_item_taxable_state=value
                if key == 'per-unit-item-non_taxable-district':
                    self.per_unit_item_non_taxable_district=value
                if key == 'per-unit-item-non_taxable-city':
                    self.per_unit_item_non_taxable_city=value
                if key == 'per-unit-item-non_taxable-county':
                    self.per_unit_item_non_taxable_county=value
                if key == 'per-unit-item-non_taxable-state':
                    self.per_unit_non_item_taxable_state=value
                if key == 'per-unit-item-zero-rated-district':
                    self.per_unit_item_zero_rated_district=value
                if key == 'per-unit-item-zero-rated-city':
                    self.per_unit_item_zero_rated_city=value
                if key == 'per-unit-item-zero-rated-county':
                    self.per_unit_item_zero_rated_county=value
                if key == 'per-unit-item-zero-rated-state':
                    self.per_unit_item_zero_rated_state=value
                if key == 'per-unit-item-tax-collected-district':
                    self.per_unit_item_item_tax_collected_district=value
                if key == 'per-unit-item-tax-collected-city':
                    self.per_unit_item_tax_collected_city=value
                if key == 'per-unit-item-tax-collected-county':
                    self.per_unit_item_tax_collected_county=value
                if key == 'per-unit-item-tax-collected-state':
                    self.per_unit_item_tax_collected_state=value
                if key == 'per-unit-shipping-taxable-district':
                    self.per_unit_shipping_taxable_district=value
                if key == 'per-unit-shipping-taxable-city':
                    self.per_unit_shipping_taxable_city=value
                if key == 'per-unit-shipping-taxable-county':
                    self.per_unit_shipping_taxable_county=value
                if key == 'per-unit-shipping-taxable-state':
                    self.per_unit_shipping_taxable_state=value
                if key == 'per-unit-shipping-non-taxable-district':
                    self.per_unit_shipping_non_taxable_district=value
                if key == 'per-unit-shipping-non-taxable-city':
                    self.per_unit_shipping_non_taxable_city=value
                if key == 'per-unit-shipping-non-taxable-county':
                    self.per_unit_shipping_non_taxable_county=value
                if key == 'per-unit-shipping-non-taxable-state':
                    self.per_unit_shipping_non_taxable_state=value
                if key == 'per-unit-shipping-zero-rated-district':
                    self.per_unit_shipping_zero_rated_district=value
                if key == 'per-unit-shipping-zero-rated-city':
                    self.per_unit_shipping_zero_rated_city=value
                if key == 'per-unit-shipping-zero-rated-county':
                    self.per_unit_shipping_zero_rated_county=value
                if key == 'per-unit-shipping-zero-rated-state':
                    self.per_unit_shipping_zero_rated_state=value
                if key == 'per-unit-shipping-tax-collected-district':
                    self.per_unit_shipping_tax_collected_district=value
                if key == 'per-unit-shipping-tax-collected-city':
                    self.per_unit_shipping_tax_collected_city=value
                if key == 'per-unit-shipping-tax-collected-county':
                    self.per_unit_shipping_tax_collected_county=value
                if key == 'per-unit-shipping-tax-collected-state':
                    self.per_unit_shipping_tax_collected_state=value
        else:
            raise TypeError("Invalid data type passed to Amazon_CO __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "Amazon_CO instance"
    
    def read_line(self,line):
        res=re.split(r'\t', line.rstrip())
        if line[-2:-1]=='\t':
            res.append('')
        if len(res) != len(self.headers):
            return(-1) # improperly formatted line
        for item in self.headers:
            if item == 'buyer-name':
                self.buyer_name=res[self.headers.index(item)]
            if item == 'buyer-phone-number':
                self.buyer_phone_number=res[self.headers.index(item)]
            if item == 'buyer-email':
                self.buyer_email=res[self.headers.index(item)]
            if item == 'sku':
                self.sku=res[self.headers.index(item)]
            if item == 'product-name':
                self.product_name=res[self.headers.index(item)]
            if item == 'purchase-date':
                self.purchase_date=res[self.headers.index(item)]
            if item == 'payments-date':
                self.payments_date=res[self.headers.index(item)]
            if item == 'order-id':
                self.order_id=res[self.headers.index(item)]
            if item == 'order-item-id':
                self.order_item_id=res[self.headers.index(item)]
            if item == 'external-order-id':
                self.external_order_id=res[self.headers.index(item)]
            if item == 'quantity-purchased':
                self.quantity_purchased=res[self.headers.index(item)]
            if item == 'currency':
                self.currency=res[self.headers.index(item)]
            if item == 'item-price':
                self.item_price=res[self.headers.index(item)]
            if item == 'item-promotion-discount':
                self.item_promotion_discount=res[self.headers.index(item)]
            if item == 'item-promotion-id':
                self.item_promotion_id=res[self.headers.index(item)]
            if item == 'ship-promotion-discount':
                self.ship_promotion_discount=res[self.headers.index(item)]
            if item == 'ship-promotion-id':
                self.ship_promotion_id=res[self.headers.index(item)]
            if item == 'item-tax':
                self.item_tax=res[self.headers.index(item)]
            if item == 'shipping-price':
                self.shipping_price=res[self.headers.index(item)]
            if item == 'shipping-tax':
                self.shipping_tax=res[self.headers.index(item)]
            if item == 'ship-service-level':
                self.ship_service_level=res[self.headers.index(item)]
            if item == 'recipient-name':
                self.recipient_name=res[self.headers.index(item)]
            if item == 'ship-address-1':
                self.ship_address_1=res[self.headers.index(item)]
            if item == 'ship-address-2':
                self.ship_address_2=res[self.headers.index(item)]
            if item == 'ship-address-3':
                self.ship_address_3=res[self.headers.index(item)]
            if item == 'ship-city':
                self.ship_city=res[self.headers.index(item)]
            if item == 'ship-state':
                self.ship_state=res[self.headers.index(item)]
            if item == 'ship-postal-code':
                self.ship_postal_code=res[self.headers.index(item)]
            if item == 'ship-country':
                self.ship_country=res[self.headers.index(item)]
            if item == 'ship-phone-number':
                self.ship_phone_number=res[self.headers.index(item)]
            if item == 'delivery-start-date':
                self.delivery_start_date=res[self.headers.index(item)]
            if item == 'delivery-end-date':
                self.delivery_end_date=res[self.headers.index(item)]
            if item == 'delivery-time-zone':
                self.delivery_time_zone=res[self.headers.index(item)]
            if item == 'delivery-instructions':
                self.delivery_Instructions=res[self.headers.index(item)]
            if item == 'sales-channel':
                self.sales_channel=res[self.headers.index(item)]
            if item == 'order-channel':
                self.order_channel=res[self.headers.index(item)]
            if item == 'order-channel-instance':
                self.order_channel_instance=res[self.headers.index(item)]
            if item == 'tax-location-code':
                self.tax_location_code=res[self.headers.index(item)]
            if item == 'tax-location-city':
                self.tax_location_city=res[self.headers.index(item)]
            if item == 'tax-location-county':
                self.tax_location_county=res[self.headers.index(item)]
            if item == 'tax-location-state':
                self.tax_location_state=res[self.headers.index(item)]
            if item == 'per-unit-item-taxable-district':
                self.per_unit_item_taxable_district=res[self.headers.index(item)]
            if item == 'per-unit-item-taxable-city':
                self.per_unit_item_taxable_city=res[self.headers.index(item)]
            if item == 'per-unit-item-taxable-county':
                self.per_unit_item_taxable_county=res[self.headers.index(item)]
            if item == 'per-unit-item-taxable-state':
                self.per_unit_item_taxable_state=res[self.headers.index(item)]
            if item == 'per-unit-item-non_taxable-district':
                self.per_unit_item_non_taxable_district=res[self.headers.index(item)]
            if item == 'per-unit-item-non_taxable-city':
                self.per_unit_item_non_taxable_city=res[self.headers.index(item)]
            if item == 'per-unit-item-non_taxable-county':
                self.per_unit_item_non_taxable_county=res[self.headers.index(item)]
            if item == 'per-unit-item-non_taxable-state':
                self.per_unit_non_item_taxable_state=res[self.headers.index(item)]
            if item == 'per-unit-item-zero-rated-district':
                self.per_unit_item_zero_rated_district=res[self.headers.index(item)]
            if item == 'per-unit-item-zero-rated-city':
                self.per_unit_item_zero_rated_city=res[self.headers.index(item)]
            if item == 'per-unit-item-zero-rated-county':
                self.per_unit_item_zero_rated_county=res[self.headers.index(item)]
            if item == 'per-unit-item-zero-rated-state':
                self.per_unit_item_zero_rated_state=res[self.headers.index(item)]
            if item == 'per-unit-item-tax-collected-district':
                self.per_unit_item_item_tax_collected_district=res[self.headers.index(item)]
            if item == 'per-unit-item-tax-collected-city':
                self.per_unit_item_tax_collected_city=res[self.headers.index(item)]
            if item == 'per-unit-item-tax-collected-county':
                self.per_unit_item_tax_collected_county=res[self.headers.index(item)]
            if item == 'per-unit-item-tax-collected-state':
                self.per_unit_item_tax_collected_state=res[self.headers.index(item)]
            if item == 'per-unit-shipping-taxable-district':
                self.per_unit_shipping_taxable_district=res[self.headers.index(item)]
            if item == 'per-unit-shipping-taxable-city':
                self.per_unit_shipping_taxable_city=res[self.headers.index(item)]
            if item == 'per-unit-shipping-taxable-county':
                self.per_unit_shipping_taxable_county=res[self.headers.index(item)]
            if item == 'per-unit-shipping-taxable-state':
                self.per_unit_shipping_taxable_state=res[self.headers.index(item)]
            if item == 'per-unit-shipping-non-taxable-district':
                self.per_unit_shipping_non_taxable_district=res[self.headers.index(item)]
            if item == 'per-unit-shipping-non-taxable-city':
                self.per_unit_shipping_non_taxable_city=res[self.headers.index(item)]
            if item == 'per-unit-shipping-non-taxable-county':
                self.per_unit_shipping_non_taxable_county=res[self.headers.index(item)]
            if item == 'per-unit-shipping-non-taxable-state':
                self.per_unit_shipping_non_taxable_state=res[self.headers.index(item)]
            if item == 'per-unit-shipping-zero-rated-district':
                self.per_unit_shipping_zero_rated_district=res[self.headers.index(item)]
            if item == 'per-unit-shipping-zero-rated-city':
                self.per_unit_shipping_zero_rated_city=res[self.headers.index(item)]
            if item == 'per-unit-shipping-zero-rated-county':
                self.per_unit_shipping_zero_rated_county=res[self.headers.index(item)]
            if item == 'per-unit-shipping-zero-rated-state':
                self.per_unit_shipping_zero_rated_state=res[self.headers.index(item)]
            if item == 'per-unit-shipping-tax-collected-district':
                self.per_unit_shipping_tax_collected_district=res[self.headers.index(item)]
            if item == 'per-unit-shipping-tax-collected-city':
                self.per_unit_shipping_tax_collected_city=res[self.headers.index(item)]
            if item == 'per-unit-shipping-tax-collected-county':
                self.per_unit_shipping_tax_collected_county=res[self.headers.index(item)]
            if item == 'per-unit-shipping-tax-collected-state':
                self.per_unit_shipping_tax_collected_state=res[self.headers.index(item)]
        self.parse_date()
        return(0)
    
    def read_header(self,line):
        self.headers=re.split(r'\t', line.rstrip())
    
    def parse_date(self):
        #format: 2014-09-08T13:08:30-07:00
        try:
            pieces=re.split(r'T',self.purchase_date)
            ymd=re.split(r'-',pieces[0])
            timeGmt=re.split(r'[+-]',pieces[1])
            #drop off final number separated by a +/-.  Is it some GMT adder?
            # doesn't seem to correlate with actual timesone of purchaser
            self.purchase_date=ymd[1]+'/'+ymd[2]+'/'+ymd[0]+' '+timeGmt[0]
        except:
            self.purchase_date='00/00/00 00:00:00'

class Zen_CO(models.Model):
    '''
    Mirai customer order
    '''
    headers=[] # holds headers in order read from file
    pkt=models.ForeignKey(UPS_PKT, null=True)
    fromFile=models.URLField(default='')
    fileLineNo=0
    filename=models.URLField(default='')
    type=models.CharField(max_length=20, default='Mirai')
    v_date_purchased=models.DateField()
    v_orders_status_name=models.CharField(max_length=50, default='')
    v_orders_id=models.CharField(max_length=50, default='')
    v_customers_id=models.CharField(max_length=50, default='')
    v_customers_name=models.CharField(max_length=100, default='')
    v_customers_company=models.CharField(max_length=100, default='')
    # TODO: RG 09/09/14 add in address parser module
    v_customers_street_address=models.CharField(max_length=200, default='')
    v_customers_suburb=models.CharField(max_length=200, default='')
    v_customers_city=models.CharField(max_length=100, default='')
    v_customers_postcode=models.CharField(max_length=20, default='')
    v_customers_country=models.CharField(max_length=200, default='')
    v_customers_telephone=models.CharField(max_length=50, default='')
    v_customers_email_address=models.EmailField(max_length=254)
    v_products_model=models.CharField(max_length=100, default='')
    v_products_name=models.CharField(max_length=100, default='')
    v_products_options=models.CharField(max_length=100, default='')
    v_products_options_values=models.CharField(max_length=200, default='')

    def __init__(self, params={}):
        '''
        Constructor
        '''
        super(Zen_CO,self).__init__()
        if isinstance(params,dict):
            for key,value in params.iteritems():
                if key == 'headers':
                    self.headers=value
                if key == 'fileLineNo':
                    self.fileLineNo=value
                if key == 'filename':
                    self.filename=value
                if key == 'v_date_purchased':
                    self.v_date_purchased=value
                if key == 'v_order_status_name':
                    self.v_order_status_name=value
                if key == 'v_orders_id':
                    self.v_orders_id=value
                if key == 'v_customers_id':
                    self.v_customers_id=value
                if key == 'v_customers_name':
                    self.v_customers_name=value
                if key == 'v_customers_company':
                    self.v_customers_company=value
                if key == 'v_customers_street_address':
                    self.v_customers_street_address=value
                if key == 'v_customers_suburb':
                    self.v_customers_suburb=value
                if key == 'v_customers_city':
                    self.v_customers_city=value
                if key == 'v_customers_postcode':
                    self.v_customers_postcode=value
                if key == 'v_customers_country':
                    self.v_customers_country=value
                if key == 'v_customers_telephone':
                    self.v_customers_telephone=value
                if key == 'v_customers_email_address':
                    self.v_customers_email_address=value
                if key == 'v_products_model':
                    self.v_products_model=value
                if key == 'v_products_name':
                    self.v_products_name=value
                if key == 'v_products_options':
                    self.v_products_options=value
                if key == 'v_products_options_values':
                    self.v_products_options_values=value
        else:
            raise TypeError("Invalid data type passed to Zen_CO __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "Zen_CO instance"
    
    def read_line(self,line):
        res=re.split(r'\t', line.rstrip())
        if line[-2:-1]=='\t':
            res.append('')
        if len(res) != len(self.headers):
            return(-1) # improperly formatted line
        for item in self.headers:
            if item == 'v_date_purchased':
                self.v_date_purchased=res[self.headers.index(item)]
            if item == 'v_orders_status_name':
                self.v_order_status_name=res[self.headers.index(item)]
            if item == 'v_orders_id':
                self.v_orders_id=res[self.headers.index(item)]
            if item == 'v_customers_id':
                self.v_customers_id=res[self.headers.index(item)]
            if item == 'v_customers_name':
                self.v_customers_name=res[self.headers.index(item)]
            if item == 'v_customers_street_address':
                self.v_customers_street_address=res[self.headers.index(item)]
            if item == 'v_customers_suburb':
                self.v_customers_suburb=res[self.headers.index(item)]
            if item == 'v_customers_city':
                self.v_customers_city=res[self.headers.index(item)]
            if item == 'v_customers_postcode':
                self.v_customers_postcode=res[self.headers.index(item)]
            if item == 'v_customers_country':
                self.v_customers_country=res[self.headers.index(item)]
            if item == 'v_customers_telephone':
                self.v_customers_telephone=res[self.headers.index(item)]
            if item == 'v_customers_email_address':
                self.v_customers_email_address=res[self.headers.index(item)]
            if item == 'v_products_model':
                self.v_products_model=res[self.headers.index(item)]
            if item == 'v_products_name':
                self.v_products_name=res[self.headers.index(item)]
            if item == 'v_products_options':
                self.v_products_options=res[self.headers.index(item)]
            if item == 'v_products_options_values':
                self.v_products_options_values=res[self.headers.index(item)]
        self.parse_date()
        return(0)
        
    def read_header(self,line):
        self.headers=re.split(r'\t', line.rstrip())
        
    def parse_date(self):
        #format: 2014-08-14 14:20:46
        try:
            pieces=re.split(r' ',self.v_date_purchased)
            ymd=re.split(r'-',pieces[0])
            #drop off final number separated by a +/-.  Is it some GMT adder?
            # doesn't seem to correlate with actual timesone of purchaser
            self.v_date_purchased=ymd[1]+'/'+ymd[2]+'/'+ymd[0]+' '+pieces[1]
        except:
            self.v_date_purchased='00/00/00 00:00:00'
    
class UPS_SOR(models.Model):
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
        super(UPS_SOR,self).__init__()
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
            raise TypeError("Invalid data type passed to UPS_SOR __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "UPS_SOR instance"
    
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
                    # build up a tab separated line that UPS_SO line items know how to parse 
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
                    so=UPS_SO({'headers':self.headers,'fileLineNo':rowIndex+1})
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

class UPS_SO(models.Model):
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
        super(UPS_SO,self).__init__()
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
            raise TypeError("Invalid data type passed to UPS_SO __init__.  Should be a dictionary\n")
    
    def __unicode__(self):
        return "UPS_SO instance"
    
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