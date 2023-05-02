import datetime
import numpy as np
import CFEngine.utils.sysutils as sysutils
import csv


class AssetVariables(object):

    def __init__(self, config_file):
        #Configueration Meta Data
        if sysutils.validate_data_file_name(config_file) is False:
            raise Exception('Invalid tape file')
        else:
            self.config_file = config_file
            self.config_date = datetime.datetime.today()
            #Configueration Data
            self.strs = None
            self.dates = None
            self.bools = None
            self.ints = None
            self.floats = None
            self.arrays = None
            self.base_fields = None
            self.consumer_fields = None
            self.consumer_mortgage_fields = None
            self.consumer_auto_fields = None
            self.consumer_student_fields = None
            self.consumer_unsecured_fields = None
            self.consumer_creditcard_fields = None
            self.commercial_fields = None
            self.commercial_mortgage_fields = None
            self.stratification_fields = None
            #Data Loading Procedure Calls
            if self._validate_config_file() is False:
                raise Exception('Invalid config file')
            else:
                self._read_config_file()
                self._load_config()

    def _validate_config_file(self):
        if sysutils.check_file_exists(self.config_file) is False or str(self.config_file).endswith('.csv') is False:
            raise Exception('Config file does not exist or is invalid format (must be .csv)')
        else:
            with open(self.config_file, 'r', newline='') as csvfile:
                header = next(csv.reader(csvfile, delimiter = ','))
            #TODO: : check the header to see if fields are vaild... also need to check values in each field

    def _read_config_file(self):
        with open(self.config_file, 'r') as f:
            raw_config = f.read()
        return raw_config

    def _load_config(self):


strs = (
    # basic origination characteristics
    'loanid', 'poolid', 'sector', 'productdesc',
    # interest rate characteristics
    'intrate_type', 'intcompound_type', 'daycount_type', 'rate_index', 'floatrate_resetfreq',
    # amortization and payment characteristics
    'pmtfreq'
)

dates = (
    # basic origination characteristics
    'origdate', 'matdate', 'cutoffdate',
    # interest rate characteristics
    'floatrate_initresetdate', 'floatrate_lastresetdate', 'floatrate_nextresetdate',
    # amortization and payment characteristics
    'firstpaydate',
    # servicing characteristics
    'lastpaydate', 'lastduedate', 'nextpaydate',
    # internal function characteristics
    'paydate_calc', 'rateget_calc'
)

bools = (
    # portfolio characteristics
    'flag_runcf', 'data_integrity', 'type_integrity'
)

ints = (
    # basic origination characteristics
    'origterm', 'loanage', 'remterm',
    # interest rate characteristics
    'floatrate_fixterm', '__floatrate_resetsubfreq', 'floatrate_lookback', 'floatrate_period1',
    # amortization and payment characteristics \
    'amortterm', 'ioterm', 'promoterm',
    # servicing characteristics
    'dqstatus',
    # portfolio characteristics \
    'port_group1', 'port_group2', 'port_group3'
)

floats = (
    # basic origination characteristics
    'origbal', 'currbal', 'pmt',
    # interest rate characteristics
    'curr_rate', 'rate_margin', 'rate_index_initvalue', 'floatrate_cap1', 'floatrate_floor1',
    'floatrate_cap2','floatrate_floor2', 'io_margin', 'promo_margin',
    # amortization and payment characteristics
    'prepaypenalty',
    # servicing characteristics
    'escrowbal', 'accrued_int', 'accrued_fees'
)

arrays = (
    # amortization and payment characteristics
    'amortsched', 'pmtsched', 'schedpmtdates', 'eompmtdates', 'rempmtdates', 'rempmtage'
)



def getTypeDict(varname,fulldict=False):
    def getType(varname_):
        if varname_ in strs:
            return str
        elif varname_ in dates:
            return datetime.date
        elif varname_ in bools:
            return np.bool_
        elif varname_ in ints:
            return np.int64
        elif varname in floats:
            return np.float64
        elif varname in arrays:
            return np.array
        else:
            return None
    if not fulldict:
        return getType(varname)
    else:
        typedict= {}
        for var in strs, dates, bools, ints, floats, arrays:
            typedict[var] = getType(var)
        return typedict


required_base_fields = ['loanid', 'poolid', 'sector', 'productdesc', 'intrate_type',
                        'cutoffdate', 'origdate', 'matdate', 'firstpaydate',
                        'origterm', 'remterm', 'dqstatus', 'orig_channel',
required_consumer_fields = ['origfico', 'currfico', 'origdti', 'originc', 'inctype',
                            'bk_status', 'fc_status',  ]
required_consumer_mortgage_fields = ['cumorigbal', 'proptype', 'propunits', 'occtype', 'purposetype', 'lientype',
                                     'prop_appraisal', ]
required_consumer_auto_fields = []
required_consumer_student_fields = []
required_consumer_unsecured_fields = []
required_consumer_creditcard_fields = []
required_commercial_fields = []
required_commercial_mortgage_fields = []



required_mortgage_fields = ['cutoffdate',
                            'loanid',
                            'sector',
                            'poolid',
                            'loantype', #TODO: think about requirement
                            'productdesc',
                            'origfico',
                            'currfico',
                            'currfico_date',
                            'oltv',
                            'odti',
                            'origterm',
                            'origbal',
                            'currbal',
                            'cumorigbal',
                            'rate_margin',
                            'io_flag',
                            'baloon_flag',
                            'state',
                            'proptype',
                            'propunits',
                            'occtype',
                            'purposetype',
                            'lientype',
                            'dqstatus',
                            'prop_appraisal',
                            'orig_channel',
                            'mers_flag',
                            'bkstatus',
                            'fc_status',
                            'origdate',
                            'firstpaydate',
                            'matdate',
                            'mod_date',
                            'mod_type',
                            'bk_type',
                            'pmt',
                            'pmt_ti',
                            'svc_grossfee',
                            'svc_netfee',
                            'sec_ptrate',
                            'esc_currbal',
                            'esc_advbal',
                            'svc_advbal',
                            'svc_advbal_rec',
                            'svc_tp_advbal_rec',
                            'svc_fee_pending',
                            'mi_company',
                            'lpmi_flag',
                            'mi_coverage',
                            'tx50a6_flag',
                            'scra_flag',
                            'recourse_flag']
