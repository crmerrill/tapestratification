import os
import datetime
import numpy as np
import pandas as pd
import csv


class AssetVariableConfig(object):

    _required_config_fields = {'FieldName': (str, None),
                                'DataDesc': (str, ('uniqueid','categorical', 'numeric', 'date', 'flag')),
                                'DataCategory': (str, ('strs', 'floats', 'ints', 'dates', 'bools', 'arrays')),
                                'DataType': (str, ('str', 'enum', 'datetime.date', 'list', 'tuple', 'bool', 'np.bool_' 
                                                    'int', 'np.integer', 'np.int8', 'np.byte', 'np.int16', 'np.short',
                                                    'np.int32', 'np.intc', 'np.int_', 'np.int64', 'np.long', 'np.longlong',
                                                    'np.ubyte', 'np.uint16', 'np.ushort', 'np.uint32', 'np.uintc',
                                                    'np.uint', 'np.uint64', 'np.ulong', 'np.ulonglong',
                                                    'float', 'np.floating', 'np.float16', 'np.half', 'np.float32', 'np.single',
                                                    'np.float64', 'np.double', 'np.float128', 'np.longdouble',
                                                    'np.ndarray')),
                                'Description': (str, None),
                                'PossibleValues': (str, None),
                                'DefaultValue': (str, None),
                                'StratFlag': (str, ('true', 'false')),
                                'StratType': (str, ('none', 'bucket_fixed', 'bucket_auto', 'unique_value', 'vintage_month', 'vintage_quarter', 'vintage_annual')),
                                'StratSumSet': (str, ('none', 'summary', 'summary_extended', 'servicing', 'performance', 'utilization')),
                                'GenericLoan': (str, ('true', 'false')),
                                'ConsumerLoan': (str, ('', 'none', 'true', 'false')),
                                'ConsumerMortgage': (str, ('', 'none', 'true', 'false')),
                                'ConsumerHELOC': (str, ('', 'none', 'true', 'false')),
                                'ConsumerAuto': (str, ('', 'none', 'true', 'false')),
                                'ConsumerStudent': (str, ('', 'none', 'true', 'false')),
                                'ConsumerCard': (str, ('', 'none', 'true', 'false')),
                                'ConsumerUnsecured': (str, ('', 'none', 'true', 'false')),
                                'CommercialLoan': (str, ('true', 'false')),
                                'CommercialMortgage': (str, ('', 'none', 'true', 'false')),
                                'CommercialAmortizing': (str, ('', 'none', 'true', 'false')),
                                'CommercialBullet': (str, ('', 'none', 'true', 'false')),
                                'CommercialRevolver': (str, ('', 'none', 'true', 'false')),
                                'CommercialABL': (str, ('', 'none', 'true', 'false')),
                                'CommercialCard': (str, ('', 'none', 'true', 'false')),
                                'CommercialAuto': (str, ('', 'none', 'true', 'false')),
                                'CommercialEquipment': (str, ('', 'none', 'true', 'false')),
                                }

    
    _required_config_field_number = 26

    @staticmethod
    def convert_bools(var):
        if type(var) in (list, tuple, set, dict, datetime.date, datetime.datetime):
            return None
        elif var is None or pd.isnull(var):
            return None
        elif isinstance(var, bool):
            return var
        elif isinstance(var, (int, np.integer)):
            if var == 1:
                return True
            elif var == 0:
                return False
            else:
                return False
        elif isinstance(var, (float, np.floating)):
            if var == 1.0:
                return True
            else:
                return False
        elif type (var) in (str, object):
            if str(var).strip().lower() in ('none', 'na', 'nan', 'n/a', 'null', '', ' '):
                return None
            if str(var).strip().lower() in ('true', 'yes', 'y', 't', '1'):
                return True
            elif str(var).strip().lower() in ('false', 'no', 'n', 'f', '0'):
                return False
            else:
                return False
        else:
            return False

    @staticmethod
    def convert_ints(var, int_type=np.int_):
        try:
            if int_type not in (int, np.byte, np.short, np.intc, np.int_, np.longlong,
                            np.ubyte, np.ushort, np.uintc, np.uint, np.ulonglong):
                int_type = np.int_
            if type(var) in (list, tuple, set, dict, datetime.date, datetime.datetime):
                return None
            elif var is None or pd.isnull(var):
                return None
            elif isinstance(var, (float, np.floating)):
                return int_type(np.round(var, 0))
            elif type(var) in (str, object):
                #convert empty strings to none
                if str(var).strip().lower() in ('none', 'na', 'nan', 'n/a', 'null', '', ' '):
                    return None
                #converts string boolean to integers (e.g. True to 1)
                elif str(var).strip().lower() in ('true', 'yes', 'y', 't', '1'):
                    return int_type(1)
                elif str(var).strip().lower() in ('false', 'no', 'n', 'f', '0'):
                    return int_type(0)
                #converts percentages to integers (e.g. 10% to 10)
                elif str(var).strip().endswith('%'):
                    return int_type(np.round(np.float_(str(var).strip().replace(',', '').replace('%', '')), 0))
                #takes money and converts to cents for dollars, pounds and euros (not others)
                elif str(var).strip().endswith(('$', '£', '€')) or str(var).strip().startswith(('$', '£', '€')):
                    return int_type(np.round(np.float_(
                                str(var).strip().replace(',', '')
                                .replace('$', '').replace('£', '').replace('€', '')
                                .strip()),0))
                #converts bps to integers (e.g. 10 bps to 10000)
                elif str(var).strip().endswith('bps'):
                    return int_type(np.round(np.float_(str(var).strip().replace(',', '').replace('bps', '')), 0))
                else:
                    return int_type(np.round(np.float_(str(var).strip().replace(',', '')),0))
            else:
                return int_type(var)
        except ValueError:
            return None

    @staticmethod
    def convert_floats(var, float_type=np.longdouble):
        try:
            if float_type not in (float, np.single, np.half, np.double, np.longdouble,
                                  np.float_, np.float16, np.float32, np.float64):
                float_type = np.longdouble
            if type(var) in (list, tuple, set, dict, datetime.date, datetime.datetime):
                return None
            elif var is None or pd.isnull(var):
                return None
            elif type(var) in (str, object):
                if str(var).strip().lower() in ('none', 'na', 'nan', 'n/a', 'null', '', ' '):
                    return None
                # converts string boolean to floats (e.g. True to 1)
                elif str(var).strip().lower() in ('true', 'yes', 'y', 't', '1'):
                    return float_type(1)
                elif str(var).strip().lower() in ('false', 'no', 'n', 'f', '0'):
                    return float_type(0)
                elif str(var).strip().endswith(('%', 'bps', '$', '£', '€')) or \
                        str(var).strip().startswith(('%', 'bps', '$', '£', '€')):
                    return float_type(str(var).strip().replace(',','')
                                      .replace('%','')
                                      .replace('bps','')
                                      .replace('$','').replace('£','').replace('€','')
                                      .strip())
                else:
                    return float_type(str(var).strip().replace(',', '').strip())
            else:
                return float_type(var)
        except ValueError:
            return None

    @staticmethod
    def convert_strs(var):
        if var is None or str(var).strip().lower() in ('none', 'na', 'nan', 'n/a', 'null', '', ' '):
            return None
        else: 
            return str(var)
    
    @staticmethod
    def convert_dates(var, dt_format='%Y-%m-%d'):
        #NOTE: There is a bizarre type hierarcy at work here.
        #       datetime.datetime is an instance of datetime.date, so the check for datetime.datetime must come first
        #       booleans are also instances of int, so you need to check for bool first before int and float
        try:
            if var is None or pd.isnull(var) or str(var).strip().lower() in ('none', 'na', 'nan', 'n/a', 'null', '', ' '):
                return None
            elif isinstance(var, datetime.datetime):
                return var.date()
            elif isinstance(var, datetime.date):
                return var
            elif isinstance(var, bool):
                return None
            elif isinstance(var, (int, np.integer, float, np.floating)) and int(var) <= 409926:
                return datetime.date(1899,12,31) + datetime.timedelta(int(var) - (1 if int(var)>=60 else 0))
            elif isinstance(var, (int, np.integer, float, np.floating)) and int(var) > 409926:
                return datetime.datetime.strptime(str(int(var)), '%Y%m%d').date()
            else:
                var = str(var)
                return datetime.datetime.strptime(var, dt_format).date()
        except ValueError:
            return None

    @staticmethod
    def read_dates_to_array(date_string, **kwargs):
        dt_format = '%Y-%m-%d' if kwargs.get('dt_format') is None else kwargs.get('dt_format')
        dt_delim = ';' if kwargs.get('dt_delim') is None else kwargs.get('dt_delim')
        dt_type = datetime.date if kwargs.get('dt_type') is None else kwargs.get('dt_type')
        dt_parser = lambda x: (AssetVariableConfig.convert_dates(x, dt_format)
                               if kwargs.get('dt_parser') is None else kwargs.get('dt_parser')(x, dt_format))
        return np.array([dt_parser(element.strip()) for element in date_string.split(dt_delim)], dtype=dt_type)

    @staticmethod
    def read_ramp_to_array(ramp_string):
        try:
            if ramp_string is None or str(ramp_string).strip().lower() in ('none', 'na', 'nan', 'n/a', 'null', '', ' '):
                return None
            elif not isinstance(ramp_string, (str, int, float, np.integer, np.floating, list, tuple)):
                raise ValueError('ramp_string must be a string, integer, float, list or tuple')
            else:
                ramp_array = np.empty(0)
                ramp_string = str(ramp_string)
                for symbol in ('[', ']', '(', ')', '{', '}'):
                    ramp_string = ramp_string.strip(symbol)
                ramp_string = ramp_string.replace(';', ',')
                for element in ramp_string.split(','):
                    if 'ramp' in element and 'for' in element:
                        subramp = element.replace('ramp', ',').replace('for', ',').split(',')
                        for i in range(len(subramp)):
                            subramp[i] = float(subramp[i])
                        ramp_array = np.append(ramp_array,
                                               np.arange(subramp[0], subramp[1] + ((subramp[1] - subramp[0]) / subramp[2]),
                                                         ((subramp[1] - subramp[0]) / (subramp[2] - 1))))
                        del subramp
                        del element
                    elif 'ramp' in element and 'for' not in element:
                        subramp = element.replace('ramp', ',').split(',')
                        for i in range(len(subramp)):
                            subramp[i] = float(subramp[i])
                        ramp_array = np.append(ramp_array, np.arange(subramp[0], subramp[1] + 1))
                        del subramp
                        del element
                    elif 'for' in element:
                        subramp = element.split('for')
                        ramp_array = np.append(ramp_array, np.ones(int(subramp[1])) * float(subramp[0]))
                        del subramp
                        del element
                    else:
                        ramp_array = np.append(ramp_array, float(element))
                        del element
                return ramp_array
        except ValueError:
            return 'ramp_error'

    # TODO: REWRITE: ramp_to_array should handle dates and regular array expressions.  \
    #               Dates need to be integrated into the array converter vs. being separate converter.
    array_converters = {'pmt_sched_amort': read_ramp_to_array,
                        'pmt_sched': read_ramp_to_array,
                        'pmt_sched_dates': read_dates_to_array,
                        'pmt_draw_sched': read_ramp_to_array,
                        'pmt_draw_sched_dates': read_dates_to_array}


    def __init__(self, config_file=None):
        #Configueration Meta Data
        self.config_file = config_file
        self.config_date = datetime.datetime.now()
        #Configueration Data
        self.strs = []
        self.dates = []
        self.bools = []
        self.ints = []
        self.floats = []
        self.arrays = []
        self._type_dict = {}
        self._converter_dict = {}
        self.consumer_mortgage_fields = []
        self.consumer_auto_fields = []
        self.consumer_student_fields = []
        self.consumer_unsecured_fields = []
        self.consumer_creditcard_fields = []
        self.commercial_mortgage_fields = []
        self.stratify_by_fields = []
        self.stratify_summary_fields = {}
        self.tape_schema = None

        #Data Loading Procedure Calls
        if config_file is None or self.validate_config_file() is False:
            return self
        else:
            self.load_config()
            return self


    @staticmethod
    def _check_config_file_exists(config_file):
        if os.path.exists(config_file) is False or str(config_file).endswith('.csv') is False:
            raise FileExistsError('Config file does not exist or is invalid format (must be .csv)')
        else:
            return True


    @staticmethod
    def _check_config_file_header(config_file):
        with open(config_file, 'r', newline='') as csvfile:
            header = next(csv.reader(csvfile, delimiter = ','))
            if header == list(AssetVariableConfig._required_config_fields.keys()):
                return True
            else:
                raise ImportError('Config file does not contain correct header row.')


    @staticmethod
    def _check_config_file_data(config_file):
        try:
            with open(config_file, 'r', newline='') as csvfile:
                header = next(csv.reader(csvfile, delimiter = ','))
                i = 0
                for row in iter(csv.DictReader(csvfile, header, delimiter = ',')):
                    i=i+1
                    for required_field in AssetVariableConfig._required_config_fields.keys():
                        assert type(row[required_field]) == AssetVariableConfig._required_config_fields[required_field][0]
                        if AssetVariableConfig._required_config_fields[required_field][1] is not None:
                            assert row[required_field].lower().strip() in AssetVariableConfig._required_config_fields[required_field][1]
            return True
        except AssertionError:
            if type(row[required_field]) != AssetVariableConfig._required_config_fields[required_field][0]:
                print(f'Value in {required_field} on config file row {i} is not correct data type.')
            elif row[required_field] not in AssetVariableConfig._required_config_fields[required_field][1]:
                print(f'Value of {row[required_field]} in {required_field} on config file row {i} does not contain an accepted value.')
            else:
                print(f'An unknown error has occured in config file row {i}.')
            return False


    def validate_config_file(self):
        if AssetVariableConfig._check_config_file_exists(self.config_file) is True:
            if AssetVariableConfig._check_config_file_header(self.config_file) is True:
                return AssetVariableConfig._check_config_file_data(self.config_file)
            else:
                return False
        else:
            return False


    def load_config(self):
        with open(self.config_file, 'r', newline='') as csvfile:
            header = next(csv.reader(csvfile, delimiter = ','))
            for row in iter(csv.DictReader(csvfile, header, delimiter = ',')):
                field_name = row['FieldName'].strip().lower()
                self.field_required[field_name] = bool(row['Required'])
                eval(str('self.' + str(row['DataCategory']))).append(row['FieldName'])
                if row['DataType'].strip().lower() in AssetVariableConfig._required_config_fields['DataType'][1]:
                    self._type_dict[field_name] = eval(row['DataType'].strip().lower())
                else:
                    self._type_dict[field_name] = None
                if field_name in AssetVariableConfig.array_converters.keys():
                    self._converter_dict[field_name] = AssetVariableConfig.array_converters[field_name]
                elif row['DataType'].strip().lower() in AssetVariableConfig._required_config_fields['DataType'][1]:
                    self._converter_dict[field_name] = eval(str('AssetVariableConfig._convert_' + str(row['DataCategory']).strip().lower()))
                else:
                    self._converter_dict[field_name] = None
                if row['StratFlag'].strip().lower() in ('y', 'y(e)'):
                    self.stratification_fields[field_name] = \
                        (row['StratFlag'].strip().lower(), row['StratType'].strip().lower())
                if bool(row['GenericLoan']) is True:
                    self.base_fields.append(field_name)
                if bool(row['ConsumerLoan']) is True:
                    self.consumer_fields.append(field_name)
                if bool(row['ConsumerMortgage']) is True:
                    self.consumer_mortgage_fields.append(field_name)
                if bool(row['ConsumerAuto']) is True:
                    self.consumer_auto_fields.append(field_name)
                if bool(row['ConsumerStudent']) is True:
                    self.consumer_student_fields.append(field_name)
                if bool(row['ConsumerUnsecured']) is True:
                    self.consumer_unsecured_fields.append(field_name)
                if bool(row['ConsumerCard']) is True:
                    self.consumer_creditcard_fields.append(field_name)
                if bool(row['CommercialLoan']) is True:
                    self.commercial_fields.append(field_name)
                if bool(row['CommercialMortgage']) is True:
                    self.commercial_mortgage_fields.append(field_name)
        return self


    def variable_type(self, variable_name):
        if self._type_dict[variable_name] is not None:
            return self._type_dict[variable_name]
        elif variable_name in self.strs:
            return str
        elif variable_name in self.dates:
            return datetime.date
        elif variable_name in self.bools:
            return np.bool_
        elif variable_name in self.ints:
            return np.int64
        elif variable_name in self.floats:
            return np.float64
        elif variable_name in self.arrays:
            return np.array
        else:
            return None


    @property
    def variables(self):
        return self.strs + self.dates + self.bools + self.ints + self.floats + self.arrays


    @property
    def converter_dict(self, variable_name=None):
        if variable_name is not None:
            return self._converter_dict[variable_name]
        else:
            return self._converter_dict



