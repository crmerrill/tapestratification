# This file contains a list of standard date management functions that are needed for various calculations

import datetime

import numpy as np
import pandas as pd
from numba import jit

#TODO: consider embeding this stuff in classes
# --BEGIN: Some extended datetime checking utilities similar to datetime.py private functions

# Utility functions, adapted from Python's native datetime.py, which
# also assumes the current Gregorian calendar indefinitely extended in
# both directions.  In general, Python datetime.py references to match
# the definition of the "proleptic Gregorian" calendar in Dershowitz
# and Reingold's "Calendrical Calculations", where it's the base calendar
# for all computations.  See the book for algorithms for converting between
# proleptic Gregorian ordinals and many other calendar systems.  For additional information
# refer to the code in the datetime.py module.

# -1 is a placeholder for indexing purposes.
_DAYS_IN_MONTH_LIST = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_DAYS_BEFORE_MONTH_LIST = [-1]  # -1 is a placeholder for indexing purposes.
_dbm = 0
for _dim in _DAYS_IN_MONTH_LIST[1:]:
    _DAYS_BEFORE_MONTH_LIST.append(_dbm)
    _dbm += _dim
del _dbm, _dim


def isleap(year):
    """
    Function to determined if a year is a leap year
    
    Parameters:
    -----------
    year -> INTEGER

    Returns:
    --------
    BOOLEAN: True if leap year, False otherwise
             (boolean will also work as 1 or 0)

    Notes:
    ------
    The function is written using numpy so vector calculations are supported
        (this means numpy needs to be imported as np before this can be used)

    """
    # written in numpy to support vectorized array calculations
    return np.logical_and(year % 4 == 0, np.logical_or(year % 100 != 0, year % 400 == 0))


def daysinyear(year):
    """
    Function to return total number of days in a given year, accounting for leap year.

    Parameters:
    -----------
    year -> INTEGER

    Returns:
    --------
    INTEGER: 366 if the year is a leap year, otherwise 365

    Notes:
    ------
    The function does NOT support arrays.  For array based inputs see daysinyear_array()

    """
    if isleap(year):
        return 366
    else:
        return 365


def daysinyear_array(array):
    """
    Function to return total number of days in a given year, accounting for leap year.

    Parameters:
    -----------
    year -> INTEGER ARRAY

    Returns:
    --------
    INTEGER ARRAY: 366 if the year is a leap year, otherwise 365

    Notes:
    ------
    The function is written using numpy so vector calculations are supported
        (this obviously means numpy needs to be imported as np before this can be used)

    """
    return np.where(isleap(array), 366, 365)


def daysbeforeyear(year):
    """
    Parameters:
    -----------
    year -> INTEGER

    Returns:
    --------
    INTEGER: number of days before January 1st of a given year

    """
    y = year - 1
    return y * 365 + y // 4 - y // 100 + y // 400


def daysinmonth(year, month):
    """
    Parameters:
    -----------
    year -> INTEGER
    month -> INTEGER

    Returns:
    --------
    INTEGER: number of days in that month and year, accounting for leap year

    Notes:
    --------
    Requires the isleap function to be defined.  Also reuqires numpy (requirement of isleap function) to be loaded.
    Does NOT support array inputs: for array calculations see daysinmonth_array.

    """
    assert 1 <= month <= 12, month
    if month == 2 and isleap(year):
        return 29
    return _DAYS_IN_MONTH_LIST[month]


def daysinmonth_array(array):
    """
    Function to return the number of days in a given month for an array of dates.

    Parameters:
    -----------
    array -> NUMPY ARRAY of DATEIME64[M] or greater resolution (i.e. Day, Hour, Second, )

    Returns:
    --------
    INTEGER ARRAY: number of days in a given  month accounting for leap year

    Notes:
    ------
    METHOD:
        (1) Array is converted to a numpy array of datetime64[M], which removes all of the dates
        (2) 1 month (timedelta64[M]) is added to the converted array to get the next month
        (3) The array in 2 is converted back to datetime64[d] which provides the first of the month (which is the first day of the month following the day from the input array)
        (4) 1 day (timedelta64[D]) is subtracted from the days in (3) to get the last day of the month from the original input array
        (5) The array in 4 is converted to a pandas DatetimeIndex so the day can be easily extracted
        (6) Days are returned as a numpy array of integers

    """
    newarray = (np.array(array, dtype='datetime64[M]') + np.timedelta64(1,'M')).astype('datetime64[D]') - np.timedelta64(1,'D')
    newarray = np.array(pd.DatetimeIndex(newarray).day).astype('intc')
    return newarray


def daysbeforemonth(year, month):
    """year, month -> number of days in year preceding first day of month."""
    assert 1 <= month <= 12, 'month must be in 1..12'
    return _DAYS_BEFORE_MONTH_LIST[month] + (month > 2 and isleap(year))


def daysbeforedate_array(array):
    array = np.array(array, dtype='datetime64[D]')
    return (array - array.astype('datetime64[Y]').astype('datetime64[D]')).astype('intc')

# --END extended datetime.py date checking utilities


# --BEGIN: Day Count Calculators

def days360diff(start_date, end_date, method='NASD'):
    """
    Parameters:
    -----------
    start_date -> DATETIME
    end_date -> DATETIME
    method -> STRING: 'NASD' (Default) OR 'ISDA'

    Returns:
    --------
    INTEGER: Number of days between start date and end date based on a 360-day calendar using 1 of 2 conventions below.

    Notes:
    --------
    Start_date and end_date must be standalone dates in some date-time format (python native, numpy, or pandas)
    Does NOT support array calculations.  For array calculations see days360diff_array.

    ----NASD (DEFAULT)----
    The number of accrued days is calculated on the basis of a year of 360 days with 12 30-day months, subject to the following rules:
        1.  If the end_date falls on last day of February and the start_date falls on the last day of February, then
            the end_date will be changed to the 30th.

        2.  If the start_date falls on the 31st of a month or the last day of February, then
            the start_date will be changed to the 30th.

        3.  If the start_date falls on the 30th AFTER APPLYING RULE (2), AND end_date falls on the 31st of the month, then
            end_date will be changed to the 30th.

    ----ISDA (US Version from 2006 definitions)----
    The number of accrued days is calculated on the basis of a year of 360 days with 12 30-day months, subject to the following rules:

        1.  If the start_date falls on the 31st of the month, then
            the date will be changed to the 30th.

        2.  If the start_date falls on the 30th of the month after applying (1) above, and the end_date falls on the 31st of the month, then
            the last date will be changed to the 30th.

        NOTE: Under the ISDA method you can end up with day counts for "monthly" periods that are 33 days long.  If you look at the ISDA worksheet, this is expected behavior

        FOR MORE INFORMATION SEE: https://www.isda.org/2008/12/22/30-360-day-count-conventions/

    """
    if not (isinstance(start_date, datetime.date) or isinstance(end_date, datetime.date)):
        raise TypeError('Start and End Dates must be datetime.date objects')
    # some quick error handling if dates are reversed
    _x = 1
    if start_date > end_date:
        print('Start Date is after End Date')
        _x = -1
        start_date = end_date
        end_date = start_date
    # Break apart components of the dates for processing
    sd = start_date.day
    sm = start_date.month
    sy = start_date.year
    ed = end_date.day
    em = end_date.month
    ey = end_date.year
    datediff = 0
    # Adjust the start date and end date based on selected method
    if method == 'ISDA':
        if sd == 31:
            sd = 30
        if ed == 31 and (sd == 30 or sd == 31):
            ed = 30
        datediff = ed - sd
    if method == 'NASD':
        if ed == daysinmonth(ey,em) and sd == daysinmonth(sy,sm):
            ed = 30
            sd = 30
        elif sd == daysinmonth(sy,sm):
            sd = 30
        else:
            pass
        datediff = ed - sd
    return ((ey - sy) * 360 + (em - sm) * 30 + datediff)*_x


def days360diff_array(start_array, end_array, method='NASD'):
    """
    Array calculation to finds the number of dates between start date and end date where dates are given in array format.
    start_array and end_array must be either numpy datetimes or pandas datetimes and start_array must be strictly less than end_array with regards to all dates
    Parameters:
    -----------
    start_date -> NUMPY DATETIME ARRAY OR PANDAS TIMEDATE INDEX ARRAY
    end_date -> NUMPY DATETIME ARRAY OR PANDAS TIMEDATE INDEX
    method -> STRING: 'NASD' (Default) OR 'ISDA'

    Returns:
    --------
    NUMPY INTEGER ARRAY: Number of days between start date and end date based on a 360-day calendar using 1 of 2 conventions below.

    Notes:
    --------
    Start_date and end_date must be arrays in some date-time format (numpy, or pandas)
    Two methods available based on a 360-day calendar using 1 of 2 conventions:

    ----NASD (DEFAULT)----
    The number of accrued days is calculated on the basis of a year of 360 days with 12 30-day months, subject to the following rules:
        1.  If the end_date falls on last day of February and the start_date falls on the last day of February, then
            the end_date will be changed to the 30th.

        2.  If the start_date falls on the 31st of a month or the last day of February, then
            the start_date will be changed to the 30th.

        3.  If the start_date falls on the 30th AFTER APPLYING RULE (2), AND end_date falls on the 31st of the month, then
            end_date will be changed to the 30th.

    ----ISDA (US Version from 2006 definitions)----
        The number of accrued days is calculated on the basis of a year of 360 days with 12 30-day months, subject to the following rules:

        1.  If the start_date falls on the 31st of the month, then
            the date will be changed to the 30th.

        2.  If the start_date falls on the 30th of the month after applying (1) above, and the end_date falls on the 31st of the month, then
            the last date will be changed to the 30th.

        NOTE: Under the ISDA method you can end up with day counts for "monthly" periods that are 33 days long.  If you look at the ISDA worksheet, this is expected behavior

        FOR MORE INFORMATION SEE: https://www.isda.org/2008/12/22/30-360-day-count-conventions/

    """
    # Some quick error handling for wrong date types or orders
    assert len(start_array) == len(end_array)
    assert np.all(start_array < end_array)
    start_array = pd.DatetimeIndex(start_array)
    end_array = pd.DatetimeIndex(end_array)
    # Break apart components of the dates for processing
    sd = start_array.day
    sm = start_array.month
    sy = start_array.year
    ed = end_array.day
    em = end_array.month
    ey = end_array.year
    # Adjust the start date and end date based on selected method
    if method == 'ISDA':
        datediff = np.where(np.logical_and(np.logical_and(sm != 2, sd == daysinmonth_array(start_array)), ed == 31), 0,
                            np.where(sd == 31, ed - 30, ed - sd))
    elif method == 'NASD':
        datediff = np.where(np.logical_and(sd == daysinmonth_array(start_array), ed == daysinmonth_array(end_array)), 0,
                            np.where(sd == daysinmonth_array(start_array), ed - 30, ed - sd))
    else:
        print('Invalid method given, utilizing NASD calculation')
        days360diff_array(start_array, end_array, method='NASD')
    return np.insert(np.array((ey - sy) * 360 + (em - sm) * 30 + datediff),0,0)

# --END: Day Count Calculators



# --BEGIN: Day Count Fraction Calculators




def dayfrac_30360(start_date, end_date, method='NASD'):
    # If the inputs are not arrays then use the normal days360diff function
    if (not hasattr(start_date, '__len__') and (not isinstance(start_date, str))) and (
            not hasattr(end_date, '__len__') and (not isinstance(end_date, str))):
        num = days360diff(start_date, end_date, method=method)
    # If the inputs are arrays then use the array function
    else:
        num = days360diff_array(start_date, end_date, method=method)
    return num / 360


def dayfrac_fnma(start_date,end_date, method='NASD'):
    if (not hasattr(start_date, '__len__') and (not isinstance(start_date, str))) and (
            not hasattr(end_date, '__len__') and (not isinstance(end_date, str))):
        num = days360diff(start_date, end_date, method=method)
    # If the inputs are arrays then use the array function
    else:
        num = days360diff_array(start_date, end_date, method=method)
    return (num // 30) / 360 + (num % 30) / 365


def dayfrac_act360(start_date, end_date, method=None):
    # If the inputs are not arrays then turn them into pd Timestamps and use native pandas functionality
    if (not hasattr(start_date, '__len__') and (not isinstance(start_date, str))) and (
            not hasattr(end_date, '__len__') and (not isinstance(end_date, str))):
        start_date_ = pd.Timestamp(start_date)
        end_date_ = pd.Timestamp(end_date)
        num = end_date_ - start_date_
    # If the inputs are arrays already then assume they are datetime type and use the appropriate builtin functionality for the type
    else:
        num = np.array(end_date - start_date).astype(float)
    return num / 360


def dayfrac_act365(start_date, end_date, method=None):
    # If the inputs are not arrays then turn them into pd Timestamps and use native pandas functionality
    if (not hasattr(start_date, '__len__') and (not isinstance(start_date, str))) and (
            not hasattr(end_date, '__len__') and (not isinstance(end_date, str))):
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)
        num = end_date - start_date
    # If the inputs are arrays already then assume they are datetime type and use the appropriate builtin functionality for the type
    else:
        num = np.array(end_date - start_date).astype(float)
    return num / 365


def dayfrac_actact(start_date, end_date, method='ISDA'):
    # Note: only ISDA method is supported at this time
    if method=='ISDA':
        if (not hasattr(start_date, '__len__') and (not isinstance(start_date, str))) and (
                not hasattr(end_date, '__len__') and (not isinstance(end_date, str))):
            start_date = pd.Timestamp(start_date)
            end_date = pd.Timestamp(end_date)
            if start_date.year == end_date.year or (not isleap(start_date.year) and not isleap(end_date.year)):
                frac = (end_date - start_date).days / daysinyear(end_date.year)
            else:
                frac_a = (pd.Timestamp(year=start_date.year, month=12, day=31) - start_date).days / daysinyear(start_date.year)
                frac_b = (end_date - pd.Timestamp(year = end_date.year, month=1, day=1)).days / daysinyear(end_date.year)
                frac_c = end_date.year - start_date.year -1
                frac = frac_a + frac_b + frac_c
        else:
            start_date = pd.DatetimeIndex(start_date)
            end_date = pd.DatetimeIndex(end_date)
            frac_a = 1 - (daysbeforedate_array(start_date) / daysinyear(start_date.year))
            frac_b = daysbeforedate_array(end_date) / daysinyear(end_date.year)
            frac_c = (end_date.year - start_date.year) -1
            frac = frac_a + frac_b + frac_c
    else: pass #TODO: write future code for dayfrac_actact other methods.
    return frac


def dayfrac(start_date,end_date,method):
    __DAYFRAC_FUNC_DICT = { '30/360 NASD': (dayfrac_30360,'NASD'),
                            '30/360 ISDA': (dayfrac_30360, 'ISDA'),
                            '30/360 FNMA': (dayfrac_fnma, 'NASD'),
                            'act/360': (dayfrac_act360, None),
                            'act/365': (dayfrac_act365, None),
                            'act/act': (dayfrac_actact, 'ISDA')
                            }
    return __DAYFRAC_FUNC_DICT[method][0](start_date, end_date, __DAYFRAC_FUNC_DICT[method][1])

# --END: Day Count Fraction Calculators




# --BEGIN: Next Business Day Logic

# in general array based datetime calcs for arrays should be done in numpy and single datetimes in native python.
# Other features such as pandas are here to ensure compatability with pandas indicies.
def nextbusday(date):
    """
    Calculate the next business day start_array and end_array must be either numpy datetimes or pandas datetimes and start_array must be strictly less than end_array with regards to all dates
    Parameters:
    -----------
    date -> DATETIME OR NUMPY DATETIME ARRAY OR PANDAS TIMEDATE INDEX ARRAY

    Returns:
    --------
    DATETIME of similar type (individual or array) with next business day

    Notes:
    --------
    date must be in some date-time format (native, numpy, or pandas)

    Method supports array calculations with no additional work, but requires both pandas and numpy to be loaded

    """

    # NUMPY IMPLEMENTATION
    if type(date) == np.datetime64 or type(date) == np.ndarray:
        return np.busday_offset(date, 0, roll='forward')
    # PANDAS DATE INDEX IMPLEMENTATION.  THERE IS NO DATAFRAME IMPLEMENTATION!
    # this implementation is here for pandas for compatability.  It should be avoided because it is extremely slow
    # for example the elif below will take 10x as long as the above statement for numpy
    elif type(date) == pd.core.indexes.datetimes.DatetimeIndex or type(date) == pd.core.series.Series:
        _type = type(date)
        return _type((np.busday_offset((np.array(date).astype('datetime64[D]')), 0, roll='forward')))
    # ORDINARY DATETIME IMPLEMENTATION
    else:
        if date.weekday() == 5:
            return date + pd.Timedelta(2, unit='d')
        elif date.weekday() == 6:
            return date + pd.Timedelta(1, unit='d')
        else:
            return date

# --END: Next Business Day Logic


# --BEGIN: Time Increment Functions

def dayinc(start_date: datetime.date, inc_amt: int, busday=False) -> datetime.date:
    end_date = start_date + datetime.timedelta(days=inc_amt)
    if busday:
        return nextbusday(end_date)
    else:
        return end_date


def weekinc(start_date: datetime.date, inc_amt: int, busday=False) -> datetime.date:
    end_date = start_date + datetime.timedelta(weeks=inc_amt)
    if busday:
        return nextbusday(end_date)
    else:
        return end_date


def monthinc(start_date, inc_amt, busday=False):
    end_year = (start_date.year + ((start_date.month + inc_amt - 1) // 12))
    end_month = ((start_date.month + inc_amt - 1) % 12 + 1)
    end_day = min(start_date.day, daysinmonth(end_year, end_month))
    end_date = datetime.date(end_year, end_month, end_day)
    del (end_year, end_month, end_day)
    if busday:
        return nextbusday(end_date)
    else:
        return end_date


def eomonth(start_date: datetime.date, inc_amt = 0, busday=False) -> datetime.date:
    _advDate = monthinc(start_date, inc_amt, busday)
    _endDate = datetime.date(_advDate.year, _advDate.month, daysinmonth(_advDate.year, _advDate.month))
    if busday:
        return nextbusday(_endDate)
    else:
        return _endDate


def midmonth(start_date: datetime.date, inc_amt = 0, busday = False) -> datetime.date:
    _advDate = monthinc(start_date, inc_amt, busday)
    _endDate = datetime.date(_advDate.year, _advDate.month, 15)
    if busday:
        return nextbusday(_endDate)
    else:
        return _endDate


def quarterinc(start_date, inc_amt, busday=False):
    return monthinc(start_date, inc_amt * 3, busday)


def semianninc(start_date, inc_amt, busday=False):
    return monthinc(start_date, inc_amt * 6, busday)


def anninc(start_date, inc_amt, busday=False):
    end_year = start_date.year + inc_amt
    end_month = start_date.month
    end_day = min(start_date.day, daysinmonth(end_year, end_month))
    end_date = datetime.date(end_year, end_month, end_day)
    # del (end_year, end_month, end_day)
    if busday:
        return nextbusday(end_date)
    else:
        return end_date

# --END: Time Increment Functions



#--BEGIN: Date Range Creator

# Dictionary of increment functions that can be used.
__INCREMENT_FUNC_DICT = {   'daily': (dayinc, 'datetime64[D]'),
                            'weekly': (weekinc, 'datetime64[W]'),
                            'monthly': (monthinc, 'datetime64[M]'),
                            'monthend': (eomonth, 'datetime64[M]'),
                            'monthmid': (midmonth, 'datetime64[M]'),
                            'quarterly': (quarterinc, 'datetime64[M]'),
                            'semiannual': (semianninc, 'datetime64[M]'),
                            'annual': (anninc, 'datetime64[M]')
                        }



def dateIncrement(start_date,periods, increment_type, weekday_only=False):
    return __INCREMENT_FUNC_DICT[increment_type][0](start_date, periods, weekday_only)


def dateRangeVec(start_date, periods, increment_type, weekday_only=False):
    # TODO: Fix the daily date range generator w/ business days so that it doesn't repeat days.
    _dateRange = np.arange(start_date, __INCREMENT_FUNC_DICT[increment_type][0](start_date, periods, weekday_only), dtype=__INCREMENT_FUNC_DICT[increment_type][1])
    # Logic for dealing with dates where increments are greater than monthly.  Three cases:
    if not (increment_type == 'daily' or increment_type =='weekly'):
    #   (1) Days are not 29, 30, 31 so no need to worry about leap year or how many dates a month has
    #   (2) Using mid month convention, so always use the 15th after the first date
    #   (3) Using month end steps, so always need to grab the last day
    #   (4) using 29, 30, 31 so need to grab the lesser of the actual date or the maximum dates in a month
    # CASE 1
        if start_date.day < 29 and increment_type != 'monthend' and increment_type !='monthmid':
            _dateRange = _dateRange + np.timedelta64(start_date.day - 1, 'D')
    # CASE 2
        elif increment_type == 'monthmid':
            _dateRange = _dateRange + (lambda x: 1 if x > 15 else 0)(start_date.day) * np.timedelta64(1, 'M') + np.timedelta64(14,'D')
    # CASES 3, 4
        else:
            _yearVector = [dt.year for dt in _dateRange.astype(object)]
            _monthVector = [dt.month for dt in _dateRange.astype(object)]
            _dateAdder = np.empty(len(_dateRange), dtype='<m8[D]')
            #CASE 3
            if increment_type == 'monthend':
                for i in range(0, len(_dateRange)):
                    _dateAdder[i] = np.timedelta64(daysinmonth(_yearVector[i], _monthVector[i]) - 1, 'D')
            #CASE 4
            else:
                for i in range(0, len(_dateRange)):
                    _dateAdder[i] = np.timedelta64(min(start_date.day, daysinmonth(_yearVector[i], _monthVector[i])) - 1, 'D')
            _dateRange = _dateRange + _dateAdder
    # Do the business day logics
    if weekday_only == True:
        _dateRange = nextbusday(_dateRange)
    # Give the final answer
    return _dateRange


def dateRangeGen(start_date, end_date, increment_type, weekday_only=False):
    try:
        date_iter = start_date
        while date_iter <= end_date:
            yield date_iter
            date_iter = dateIncrement(date_iter, 1, increment_type, weekday_only)
        return
    except:
        print('dateRangeGenerator inputs not correctly specified')

# END: Date Range Creator

#TODO: consider inserting some del statements to clean up some of the internal variables and methods defined in the module

