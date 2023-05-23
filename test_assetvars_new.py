import unittest
import datetime
import numpy as np
import pathlib
import contextlib
import assetvars_new as assetvars

class TestAssetvarsConfig(unittest.TestCase):
    def setUp(self):
        self.config_path_good = pathlib.Path(__file__).parent / 'good_config.csv'
        self.config_path_bad_nofile = pathlib.Path(__file__).parent / 'no_config_file.csv'
        self.config_path_bad_filetype = pathlib.Path(__file__).parent / 'bad_filetype_config.txt'
        self.config_path_bad_header = pathlib.Path(__file__).parent / 'bad_header_config.csv'
        self.config_path_bad_datatypes = pathlib.Path(__file__).parent / 'bad_datatypes_config.csv'
        self.config_path_bad_datavalues = pathlib.Path(__file__).parent / 'bad_datavalues_config.csv'
        
        self.good_header = ['FieldName', 
                              'DataDesc', 
                              'DataCategory', 
                              'DataType',
                              'Description', 
                              'PossibleValues',
                              'DefaultValue', 
                              'StratFlag', 
                              'StratType', 
                              'GenericLoan', 
                              'ConsumerLoan', 
                              'ConsumerMortgage',
                              'ConsumerAuto',
                              'ConsumerStudent',
                              'ConsumerCard',
                              'ConsumerUnsecured',
                              'CommercialLoan', 
                              'CommercialMortgage', 
                              'CommercialAmortizing', 
                              'CommercialBullet',	
                              'CommercialRevolver', 
                              'CommercialABL', 
                              'Required']
        
        self.test_variables = [
            ['boolean_variable', 'categorical', 'bools', 'bool', 'this is a boolean variable', 'True';'False', \
             'True', 'y', 'uniquevalue', 'True', 'False', 'False', 'False', 'False', 'False', 'False', 'False', \
                'False', 'False', 'False', 'False', 'False', 'True']
            ['float_variable', 'continuous', 'floats', 'np.float64', 'this is a float variable', '', '',\
             'y', 'bucketauto'
             ]
        ] 