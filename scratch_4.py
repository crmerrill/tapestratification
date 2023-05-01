
import csv
import datetime

import numpy as np
import pandas as pd

import assets.loans.loanvars as loanvars


def readTapeToDF(tapepath, inputtype='CSV', cutoffdate=None, delimiter=None, sheetname=None):
    #look at whether we are getting tape_data from flatfile or SQL.
    if inputtype == 'SQL':
        return print('SLQ not yet supported.  Write the code or use a flat file format')
        #TODO: Write SQL Code: (1) Check for No Lock in SQL string (2) Test if database exists and connection possible before query (3) run query and put into dataframe (4) enforce strict types
    else:
        #set up delimiter types for flat files:
        delimdict = {'CSV':',',
                     'csv':',',
                     'TSV':'\t',
                     'tsv':'\t',
                     'TXT':delimiter,
                     'txt':delimiter
        }
        delimiter = delimdict[inputtype]

        # get the header information so we know what fields are on the tape_data
        with open(tapepath) as file:
            header = next(csv.reader(file, delimiter = delimiter))
        #TODO: need to adust header names to trim extra space
        #now we will set-up dictinaries of types and converters for pandas to use when reading files to dataframes
        #basic type and converter dictionaries
        typedict = {}
        convertdict = getConverterDict()
        datelist = list(set(loanvars.dates).intersection(header))
        for var in set(header).difference(datelist).difference(convertdict):
            typedict[var] = loanvars.getTypeDict(var)

        #Use pandas to process flat file type being input
        if inputtype in ('CSV','csv'):
            return pd.read_csv(tapepath, parse_dates=datelist, date_parser=parseLoanDates, converters=convertdict, dtype=typedict)
        elif inputtype in ('TSV','tsv','TXT','txt'):
            return pd.read_csv(tapepath, delimiter=delimiter, parse_dates=datelist, date_parser=parseLoanDates, converters=convertdict, dtype=typedict)
        elif inputtype in ('XLS','xls'):
            return pd.read_excel(tapepath, sheet_name=sheetname, parse_dates=datelist, date_parser=parseLoanDates, converters=convertdict, dtype=typedict)
        else:
            raise Exception('Unsupported input type.  Use flat file format, MSExcel format, or SQL query')

def parseLoanDates(var, dt_format = '%Y%m%d'):
    if var == None or pd.isnull(var) or var =='':
        return None
    elif type(var) != str:
        var = str(var)
    else:
        pass
    return pd.datetime.strptime(var, dt_format).date()

def getConverterDict(groups = ('ints','floats','arrays')):
    arraydict = {
                'amortsched': readDatesToArray,
                'pmtsched': readDatesToArray,
                'schedpmtdates': readDatesToArray
                }
    convertdict = {}
    for grp in groups:
        for var in getattr(loanvars, grp):
            if grp == 'arrays' and var in arraydict.keys():
                convertdict[var] = arraydict[var]
            else:
                convertdict[var] = eval(str('convertLoan' + str(grp).capitalize()))
    return convertdict

def convertLoanInts(var):
    if type(var) == str or type(var) == object:
        if var == '':
            newvar = None
        else:
            newvar = np.int64(np.round(np.float64(var.replace(',','')),0))
    elif type(var) == float:
        newvar = np.int64(np.round(var,0))
    elif type(var) == NoneType:
        newvar = None
    else:
        newvar = np.int64(var)
    return newvar

def convertLoanFloats(var):
    if type(var) == str or type(var) == object:
        if var == '':
            newvar = None
        else:
            newvar = np.float64(var.replace(',',''))
    elif type(var) == NoneType:
        newvar = None
    else:
        newvar = np.float64(var)
    return newvar

def convertLoanArrays(string):
    raise NotImplementedError('Array converter not properly specified for reading input')

def readDatesToArray(date_string):
    date_string = date_string.replace(';',',')
    return np.array([parseLoanDates(element.strip()) for element in date_string.split(',')], dtype=datetime.date)

def readRampToArray(ramp_string):
    ramp_array = np.empty(0)
    ramp_string = ramp_string.replace(';',',')
    for element in ramp_string.split(','):
        if 'ramp' in element and 'for' in element:
            subramp = element.replace('ramp',',').replace('for', ',').split(',')
            for i in range(len(subramp)):
                subramp[i] = float(subramp[i])
            ramp_array = np.append(ramp_array,np.arange(subramp[0],subramp[1] + ((subramp[1]-subramp[0])/subramp[2]),(subramp[1]-subramp[0])/subramp[2]))
            del subramp
            del element
        elif 'ramp' in element and 'for' not in element:
            subramp = element.replace('ramp',',').split(',')
            for i in range(len(subramp)):
                subramp[i] = float(subramp[i])
            ramp_array = np.append(ramp_array, np.arange(subramp[0], subramp[1] + ((subramp[1] - subramp[0]))))
            del subramp
            del element
        elif 'for' in element:
            subramp = element.split('for')
            ramp_array = np.append(ramp_array,np.ones(int(subramp[1])) * float(subramp[0]))
            del subramp
            del element
        else:
            ramp_array = np.append(ramp_array,float(element))
            del element
    return ramp_array
