import datetime
import numpy as np
import CFEngine.cmutils.sysutils as sysutils
import csv
from functools import cached_property


class AssetVariableConfig(object):

    required_config_fields = {'FieldName': (str, None),
                              'DataDesc': (str, ('categorical', 'numeric', 'date')), 
                              'DataCategory': (str, ('strs', 'floats', 'ints', 'dates', 'bools', 'arrays')), 
                              'DataType': (str, ('str', 'enum', 'datetime.date', 'int', 'np.int64', 'float', 'np.float64', 'bool')),
                              'Description': (str, None), 
                              'PossibleValues': (str, None),
                              'DefaultValue': (str, None), 
                              'StratFlag': (str, ('y', 'y(e)', 'n')), 
                              'StratType': (str, ('none', 'bucketfixed', 'bucketauto', 'uniquevalue', 'vintagem', 'vintageq', 'vintagea')),
                              'StratSummSet': (str, ('summary', 'summary_extended', 'servicing', 'performance', 'utilization')),
                              'GenericLoan': (bool, (True, False)), 
                              'ConsumerLoan': (bool, (True, False)),
                              'ConsumerMortgage': (bool, (True, False)),
                              'ConsumerAuto': (bool, (True, False)),
                              'ConsumerStudent': (bool, (True, False)),
                              'ConsumerCard': (bool, (True, False)),
                              'ConsumerUnsecured': (bool, (True, False)),
                              'CommercialLoan': (bool, (True, False)),
                              'CommercialMortgage': (bool, (True, False)),
                              'CommercialAmortizing': (bool, (True, False)),
                              'CommercialBullet': (bool, (True, False)),
                              'CommercialRevolver': (bool, (True, False)),
                              'CommercialABL': (bool, (True, False)),
                              'Required': (bool, (True, False))}
    
    
    required_config_field_number = 35


    @staticmethod
    def _check_escape(_input):
        if type(_input) == str:
            _input = _input.lower()
        else:
            pass
        if _input in ('q', 'quit', 'esc', 'escape'):
            return True
        else:
            return False

    @staticmethod
    def _convert_dates(var, dt_format='%Y-%m-%d'):
        if var is None or pd.isnull(var) or var == '':
            return np.nan
        elif type(var) != str:
            var = str(var)
        else:
            pass
        return datetime.datetime.strptime(var, dt_format).date()

    @staticmethod
    def _convert_ints(var, int_type=np.int64):
        if type(var) in (str, object):
            if var == '':
                newvar = np.nan
            else:
                if var.endswith('%'):
                    newvar = int_type(np.round(np.float64(var.replace(',', '').replace('%', '')) * 100, 0))
                elif var.startswith('$'):
                    newvar = int_type(np.round(np.float64(var.replace(',', '').replace('$', '')) * 100, 0))
                else:
                    newvar = int_type(var.replace(',', ''))
        elif type(var) in (float, np.float64):
            newvar = int_type(np.round(var, 0))
        elif type(var) == NoneType:
            newvar = np.nan
        else:
            newvar = np.int_type(var)
        return newvar

    @staticmethod
    def _convert_floats(var, float_type=np.float64):
        if type(var) in (str, object):
            if var == '':
                newvar = np.nan
            else:
                newvar = float_type(var.replace(',', ''))
        elif type(var) == NoneType:
            newvar = np.nan
        else:
            newvar = np.float_type(var)
        return newvar

    @staticmethod
    def _convert_bools(var):
        if type(var) in (str, object):
            if var.lower() in ('true', 'yes', 'y', 't', '1'):
                return True
            elif var.lower() in ('false', 'no', 'n', 'f', '0'):
                return False
            else:
                return False
        elif type(var) is bool:
            return var
        elif type(var) is int:
            if var == 1:
                return True
            elif var == 0:
                return False
            else:
                return False
        elif type(var) is float:
            if var == 1.0:
                return True
            elif var == 0.0:
                return False
            else:
                return False
        else:
            return False

    @staticmethod
    def _read_dates_to_array(date_string, **kwargs):
        dt_format = '%Y-%m-%d' if kwargs.get('dt_format') is None else kwargs.get('dt_format')
        dt_delim = ';' if kwargs.get('dt_delim') is None else kwargs.get('dt_delim')
        dt_type = datetime.date if kwargs.get('dt_type') is None else kwargs.get('dt_type')
        dt_parser = lambda x: (AssetVariableConfig._convert_dates(x, dt_format)
                               if kwargs.get('dt_parser') is None else kwargs.get('dt_parser')(x, dt_format))
        return np.array([dt_parser(element.strip()) for element in date_string.split(dt_delim)], dtype=dt_type)

    @staticmethod
    def _read_ramp_to_array(ramp_string):
        ramp_array = np.empty(0)
        ramp_string = ramp_string.replace(';', ',')
        for element in ramp_string.split(','):
            if 'ramp' in element and 'for' in element:
                subramp = element.replace('ramp', ',').replace('for', ',').split(',')
                for i in range(len(subramp)):
                    subramp[i] = float(subramp[i])
                ramp_array = np.append(ramp_array,
                                       np.arange(subramp[0], subramp[1] + ((subramp[1] - subramp[0]) / subramp[2]),
                                                 (subramp[1] - subramp[0]) / subramp[2]))
                del subramp
                del element
            elif 'ramp' in element and 'for' not in element:
                subramp = element.replace('ramp', ',').split(',')
                for i in range(len(subramp)):
                    subramp[i] = float(subramp[i])
                ramp_array = np.append(ramp_array, np.arange(subramp[0], subramp[1] + ((subramp[1] - subramp[0]))))
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


    # TODO: REWRITE: ramp_to_array should handle dates and regular array expressions.  \
    #               Dates need to be integrated into the array converter vs. being separate converter.
    array_converters = {'pmt_sched_amort': _read_ramp_to_array,
                        'pmt_sched': _read_ramp_to_array,
                        'pmt_sched_dates': _read_dates_to_array,
                        'pmt_draw_sched': _read_ramp_to_array,
                        'pmt_draw_sched_dates': _read_dates_to_array}


    def __init__(self, config_file=None):
        #Configueration Meta Data
        self.config_file = config_file
        self.config_date = datetime.datetime.today()
        #Configueration Data
        self.strs = []
        self.dates = []
        self.bools = []
        self.ints = []
        self.floats = []
        self.arrays = []
        self._type_dict = {}
        self._converter_dict = {}
        self.base_fields = []
        self.consumer_fields = []
        self.consumer_mortgage_fields = []
        self.consumer_auto_fields = []
        self.consumer_student_fields = []
        self.consumer_unsecured_fields = []
        self.consumer_creditcard_fields = []
        self.commercial_fields = []
        self.commercial_mortgage_fields = []
        self.stratification_fields = {}
        self.field_required = {}
        #Data Loading Procedure Calls
        if config_file is None or self._validate_config_file() is False:
            return None
        else:
            self._load_config()
            return None
    

    def _validate_config_file(self):
        try:
            if sysutils.check_file_exist(self.config_file) is False or str(self.config_file).endswith('.csv') is False:
                msg = 'Config file does not exist or is invalid format (must be .csv)'
                raise FileExistsError('Config file does not exist or is invalid format (must be .csv)')
            else:
                with open(self.config_file, 'r', newline='') as csvfile:
                    header = next(csv.reader(csvfile, delimiter = ','))
                    if header == list(AssetVariables.required_config_fields.keys()):
                        i = 0
                        for row in iter(csv.DictReader(csvfile, header, delimiter = ',')):
                            i = i+1
                            for required_field in AssetVariables.required_config_fields.keys():
                                assert type(row[required_field]) == AssetVariables.required_config_fields[required_field][0]
                                if AssetVariables.required_config_fields[required_field][1] is not None:
                                    assert row[required_field] in AssetVariables.required_config_fields[required_field][1]
                                    return True
                                else:
                                    return True
                    else:
                        msg='Config file does not contain correct header row.'
                        raise ImportError('Config file does not contain correct header row.')
        except (FileExistsError, ImportError):
            print(msg)
            return False
        except AssertionError:
            if type(row[required_field]) != AssetVariables.required_config_fields[required_field][0]:
                print(f'Value in {required_field} on config file row {i} is not correct data type.')
                return False
            elif row[required_field] not in AssetVariables.required_config_fields[required_field][1]:
                print(f'Value in {required_field} on config file row {i} does not contain an accepted value.')
                return False
            else:
                print(f'An unknown error has occured in config file row {i}.')
                return False


    def _load_config(self):
        with open(self.config_file, 'r', newline='') as csvfile:
            header = next(csv.reader(csvfile, delimiter = ','))
            for row in iter(csv.DictReader(csvfile, header, delimiter = ',')):
                field_name = row['FieldName'].strip().lower()
                self.field_required[field_name] = bool(row['Required'])
                if row['DataType'].strip().lower() in AssetVariablesConfig.required_config_fields['DataType'][1]:
                    self._type_dict[field_name] = eval(row['DataType'].strip().lower())
                else:
                    self._type_dict[field_name] = None
                if field_name in AssetVariableConfig.array_converters.keys():
                    self._converter_dict[field_name] = AssetVariableConfig.array_converters[field_name]
                elif row['DataType'].strip().lower() in AssetVariableConfig.required_config_fields['DataType'][1]:
                    self._converter_dict[field_name] = eval(str('_convert_' + str(row['DataCategory']).strip().lower()))
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



