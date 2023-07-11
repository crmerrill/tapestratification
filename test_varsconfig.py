import unittest
import datetime
import numpy as np
import pathlib
import contextlib
import varsconfig as assetvars

class TestAssetvarsConfig(unittest.TestCase):
    def setUp(self):
        self.config_path_good = pathlib.Path(pathlib.Path(__file__).parent, 'good_config.csv')
        self.config_path_bad_nofile = pathlib.Path(pathlib.Path(__file__).parent, 'no_config_file.csv')
        self.config_path_bad_filetype = pathlib.Path(pathlib.Path(__file__).parent, 'bad_filetype_config.txt')
        self.config_path_bad_header = pathlib.Path(pathlib.Path(__file__).parent, 'bad_header_config.csv')
        self.config_path_bad_datatypes = pathlib.Path(pathlib.Path(__file__).parent, 'bad_datatypes_config.csv')
        self.config_path_bad_datavalues = pathlib.Path(pathlib.Path(__file__).parent, 'bad_datavalues_config.csv')


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
            ['boolean_variable', 'categorical', 'bools', 'bool', 'this is a boolean variable', 'True';'False', 'True', \
             'y', 'uniquevalue', 'True', 'False', 'False', 'False', 'False', 'False', 'False', 'False', \
            'False', 'False', 'False', 'False', 'False', 'True'],
            ['float_variable', 'continuous', 'floats', 'np.float64', 'this is a float variable', '', 3.14,\
            'y', 'bucketauto', 'True', 'False', 'False', 'False', 'False', 'False', 'False', 'False', \
            'False', 'False', 'False', 'False', 'False', 'True'],
            ['int_variable', 'discrete', 'ints', 'np.int64', 'this is an int variable', '', 42, \
            'y', 'bucketauto', 'True', 'False', 'False', 'False', 'False', 'False', 'False', 'False', \
            'False', 'False', 'False', 'False', 'False', 'True'],
            ['string_variable', 'categorical', 'strings', 'str', 'this is a string variable', '', '', \
            'string thing', 'y', 'uniquevalue', 'True', 'False', 'False', 'False', 'False', 'False', \
            'False', 'False', 'False', 'False', 'False', 'False', 'False', 'True'],
            ['date_variable', 'continuous', 'dates', 'dt.date', 'this is a date variable', '', '1982-04-13', \
            'y', 'bucketauto', 'True', 'False', 'False', 'False', 'False', 'False', 'False', 'False', \
            'False', 'False', 'False', 'False', 'False', 'True'],
        ] 

        self.test_ramps = ['3 for 10; 5 for 2; 2; 1 ramp 15 for 5; 16, 17', 
                           '2 for 20', 
                           '20 ramp 1 for 10; 5 for 10']
        
