import datetime
import numpy as np
import CFEngine.cmutils.sysutils as sysutils
import csv
from functools import cached_property


class AssetVariables(object):

    required_config_fields = {'FieldName': (str, None),
                              'DataDesc': (str, ('categorical', 'numeric', 'date')), 
                              'DataCategory': (str, ('strs', 'floats', 'ints', 'dates', 'bools', 'arrays')), 
                              'DataType': (str, ('str', 'enum', 'datetime.date', 'np.int64', 'np.float64', 'bool')),
                              'Description': (str, None), 
                              'PossibleValues': (str, None),
                              'DefaultValue': (str, None), 
                              'StratFlag': (str, ('y', 'y(e)', 'n')), 
                              'StratType': (str, ('none', 'bucketfixed', 'bucketauto', 'uniquevalue', 'vintagem', 'vintageq', 'vintagea')), 
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
            if type(row(required_field)) != AssetVariables.required_config_fields[required_field][0]:
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
                if row['DataType'].strip().lower() in AssetVariables.required_config_fields['DataType'][1]:
                    self._type_dict[field_name] = eval(row['DataType'].strip().lower())
                else:
                    self._type_dict[field_name] = None
                getattr(self, row['DataCategory'].strip().lower()).append(field_name)
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


    def var_type(self, variable_name):
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
    def all_fields(self):
        return self.strs + self.dates + self.bools + self.ints + self.floats + self.arrays
