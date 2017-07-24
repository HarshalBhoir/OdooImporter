
#
# ATT 2017-05-03 v10.0.52 - New odoo Functions
# ATT 2017-04-26 v10.0.1
#
# TOOLS FOR ODOO 10+
#
# CUSTOM FUNCTIONS FOR XML IMPORT
#
 #Logging Required Imports
import conf.logging_config as lc
import logging

import conf.odoo_importer_from_xml_cxsd_config as config
#import odoo_importer_from_xml_cxsd as importer

import sys
import random
import time
import csv
from datetime import datetime, timezone, timedelta #Py3

def getMainId():
    logger = logging.getLogger(__name__)
    return config.main_id

#Odoo
def getOdooUserId():
    logger = logging.getLogger(__name__)
    return config.odooConfigDict["odoo_uid"]

def getOdooUserName():
    logger = logging.getLogger(__name__)
    return config.odooConfigDict["odoo_username"]

def getCurrentDateTimeForSQL():
    logger = logging.getLogger(__name__)
    return time.strftime('%Y-%m-%d %H:%M:%S')

def getSQLDateTimeFromJoinedStringInternational(joined_datetime_string):

    if len(joined_datetime_string) == 12:


        dt = datetime.strptime(joined_datetime_string, "%Y%m%d%H%M")
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    elif len(joined_datetime_string) == 14:

        dt = datetime.strptime(joined_datetime_string, "%Y%m%d%H%M%S")
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    else:
        return ""


def getSQLDateTimeFromJoinedStringBrazilian(joined_datetime_string):
    logger = logging.getLogger(__name__)
    ##logger.warn(nodePath)
    ##logger.warn(getValueOf)
    ##logger.warn(joined_datetime_string)
    ##exit(1)

    if len(joined_datetime_string) == 12:
        dt = datetime.strptime(joined_datetime_string, "%d%m%Y%H%M")
        
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    elif len(joined_datetime_string) == 14:
        #08062017135811
        dt = datetime.strptime(joined_datetime_string, "%d%m%Y%H%M%S")
        ##logger.warn(joined_datetime_string)
        
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    else:

        return ""

def sec2time(sec, n_msec=3):
    ''' Convert seconds to 'D days, HH:MM:SS.FFF' '''
    if hasattr(sec,'__len__'):
        return [sec2time(s) for s in sec]
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if n_msec > 0:
        pattern = '%%02d:%%02d:%%0%d.%df' % (n_msec+3, n_msec)
    else:
        pattern = r'%02d:%02d:%02d'
    if d == 0:
        return pattern % (h, m, s)
    return ('%d days, ' + pattern) % (d, h, m, s)

def check_sunday(_datetime):
    '''Check if _datetime is sunday and return True if is not return False'''
    if _datetime.weekday() == 6:
        return True
    else:
        return False


def check_holiday_csv(_datetime):
    with open('/etc/OdooImporter/feriados.csv', newline='') as csvfile:
        csvferiados = csv.reader(csvfile, delimiter=';', quotechar='|')
        for feriado in csvferiados:
            if datetime(feriado[0]) == _datetime:
                return True
            else:
                pass
        return False
            

#Returns delta time between two dates.
def getDeltaTimeBrazilianDateTimeStringsHolidays(old_date_time_joined_string, new_date_time_joined_string):
    logger = logging.getLogger(__name__)

    dateTimeStringOld = getSQLDateTimeFromJoinedStringBrazilian(old_date_time_joined_string)
    dateTimeStringNew = getSQLDateTimeFromJoinedStringBrazilian(new_date_time_joined_string)
    
    dateTimeOld = datetime.strptime(dateTimeStringOld, '%Y-%m-%d %H:%M:%S')
    dateTimeNew = datetime.strptime(dateTimeStringNew, '%Y-%m-%d %H:%M:%S')
  
    logger.info('Início do SLA: %s' % dateTimeOld)
    logger.info('Fim do SLA: %s' % dateTimeNew)
    logger.info('Delta 24horas: %s' % (dateTimeNew-dateTimeOld))

    delta_horas = timedelta(hours=0)
    delta_dia = timedelta(hours=12)
    d = timedelta(days=1)
    check_day = dateTimeOld
    delta_full_days = dateTimeNew.day - dateTimeOld.day - 1
    first_day_start = datetime(dateTimeOld.year, dateTimeOld.month, dateTimeOld.day, 7, 30)
    first_day_end = datetime(dateTimeOld.year, dateTimeOld.month, dateTimeOld.day, 19, 30)
    last_day_start = datetime(dateTimeNew.year, dateTimeNew.month, dateTimeNew.day, 7, 30)
    last_day_end = datetime(dateTimeNew.year, dateTimeNew.month, dateTimeNew.day, 19, 30)


    if delta_full_days >= 0:
        run = delta_full_days
        while run > 0:
            check_day = check_day + d
            if check_sunday(check_day):
                pass
            else:
                if check_holiday(check_day):
                    pass
                else:
                    delta_horas = delta_horas + delta_dia
            run = run - 1
        if first_day_start > dateTimeOld:
            delta_start = timedelta(hours=12)
        else:
            if dateTimeOld > first_day_end:
                delta_start = timedelta(hours=0)
            else:
                delta_start = first_day_end - dateTimeOld
                pass

        if last_day_start > dateTimeNew:
            delta_end = timedelta(hours=0)
        else:
            if dateTimeNew > last_day_end:
                delta_end = timedelta(hours=12)
            else:
                delta_end = dateTimeNew - last_day_start
                pass
                        
        delta_total = delta_start + delta_horas + delta_end
        logger.info('SLA total: %s' % delta_total)

    else:
        if first_day_start > dateTimeOld:
            dateTimeOld = first_day_start

        if last_day_end < dateTimeNew:
            dateTimeNew = last_day_end

        delta_total = dateTimeNew - dateTimeOld
        logger.info('SLA total: %s' % delta_total)

    d =  divmod(delta_total.total_seconds(), 86400) #days
    h = divmod(d[1],3600)  # hours
    m = divmod(h[1],60)  # minutes
    s = m[1]  # seconds

    return '%d dias, %d horas, %d minutos e %d segundos' % (d[0],h[0],m[0],s)

#Returns delta time between two dates.
def getDeltaTimeBrazilianDateTimeStrings(old_date_time_joined_string, new_date_time_joined_string):
    logger = logging.getLogger(__name__)

    dateTimeStringOld = getSQLDateTimeFromJoinedStringBrazilian(old_date_time_joined_string)
    dateTimeStringNew = getSQLDateTimeFromJoinedStringBrazilian(new_date_time_joined_string)
    
    #logger.info(dateTimeStringOld)
    #logger.info(dateTimeStringNew)
    
    dateTimeOld = datetime.strptime(dateTimeStringOld, '%Y-%m-%d %H:%M:%S')
    dateTimeNew = datetime.strptime(dateTimeStringNew, '%Y-%m-%d %H:%M:%S')
  
    logger.info(dateTimeOld)
    logger.info(dateTimeNew)
  
    logger.info(dateTimeNew-dateTimeOld)

    if dateTimeNew>dateTimeOld:

        elapsedTime = dateTimeNew-dateTimeOld

        d =  divmod(elapsedTime.total_seconds(), 86400) #days
        h = divmod(d[1],3600)  # hours
        m = divmod(h[1],60)  # minutes
        s = m[1]  # seconds

        return '%d dias, %d horas, %d minutos e %d segundos' % (d[0],h[0],m[0],s)

    else:
        return ""


def getXMLFilename():
    logger = logging.getLogger(__name__)
    return config.inputXMLFileName

def getRandomNumber():
    logger = logging.getLogger(__name__)
    return str(random.randint(0, sys.maxsize))

def getFormDateTime():
    logger = logging.getLogger(__name__)
    return convertDateTimeFromEpochDateTime(config.formDateTime)

#Return Formatted Date from timestamp in miliseconds
def convertDateTimeFromEpochDateTime(datetime_from_epoch_ms):
    logger = logging.getLogger(__name__)
    return datetime.fromtimestamp(int(datetime_from_epoch_ms)/1000, timezone.utc)

#Config of Custom Schemas based on prefix of file (5Chars)
def getSchemaFilenameForPrefix(prefix):
    logger = logging.getLogger(__name__)

    if prefix in ["IPO"]:
      #return 'MCO_20170607_150100_D02.cxsd'
      return 'IPO_Main_20170619_153000_D01.cxsd'

    if prefix in ["MCO"]:
      #return 'MCO_20170607_150100_D02.cxsd'
      #return 'MCO_20170612_153050_D03.cxsd'
      return 'MCO_20170724_102000_D04.cxsd'

    if prefix in ["COR9_"]:
      return 'COR09.cxsd'

    if prefix in ["COR16"]:
      return 'COR16.cxsd'

    if prefix in ["COR17", "COR18", "COR19", "COR19"]:
      return 'COR19.cxsd'   

    if prefix in ["COR20", "COR21", "COR22"]:
      return 'COR20.cxsd'

    if prefix in ["COR23"]:
      return 'COR23.cxsd'

    if prefix in ["COR24"]:
      return 'COR24.cxsd'

    if prefix in ["COR25"]:
      return 'COR25.cxsd'

    if prefix in ["COR27"]:
      return 'COR27.cxsd'

    if prefix in ["COR28", "COR29", "COR30"]:
      return 'COR27.cxsd'

    if prefix in ["COR31"]:
      return 'COR31.cxsd'

    return "COR27" #default
