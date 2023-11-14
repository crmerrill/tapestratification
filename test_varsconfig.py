import unittest
import os
import datetime
import numpy as np
import pathlib
import contextlib
import csv
import varsconfig
#import CFEngine.cmutils.sysutils as sysutils


class TestConvertBools(unittest.TestCase):
    def test_none_to_bool(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(None), None)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_bools(None), type(None))

    def test_str_to_bool(self):
        test_vars = {'NONE': None, 'none': None, 'None': None, ' None': None, 'NONE ': None,
                     'NA': None, 'na': None, 'Na': None, ' Na': None, 'NA ': None,
                     'NAN': None, 'nan': None, 'Nan': None, ' Nan': None, 'NAN ': None,
                     'N/A': None, 'n/a': None, 'N/a': None, ' N/a': None, 'N/A ': None,
                     'NULL': None, 'null': None, 'Null': None, ' Null': None, 'NULL ': None,
                     '': None, ' ': None,
                     'TRUE': True, 'true': True, 'True': True, ' True': True, 'TRUE ': True,
                     'YES': True, 'yes': True, 'Yes': True, ' Yes': True, 'YES ': True,
                     'Y': True, 'y': True, ' y': True, 'Y ': True,
                     'T': True, 't': True, ' t': True, 'T ': True,
                     '1': True,
                     'FALSE': False, 'false': False, 'False': False, ' False': False, 'FALSE ': False,
                     'NO': False, 'no': False, 'No': False, ' No': False, 'NO ': False,
                     'N': False, 'n': False, ' n': False, 'N ': False,
                     'F': False, 'f': False, ' f': False, 'F ': False,
                     '0': False}
        for k, v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_bools(k), (bool, type(None)))

    def test_int_to_bool(self):
        for var in range(0, 10):
            if var == 1:
                self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(var), True)
            else:
                self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(var), False)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_bools(var), bool)

    def test_float_to_bool(self):
        for var in np.arange(0.0, 10.0, 0.1):
            if var == 1.0:
                self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(var), True)
            else:
                self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(var), False)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_bools(var), bool)

    def test_others_to_bool(self):
        test_vars = [datetime.datetime.now(),
                     datetime.date.today(),
                     ['a', 'b', 'c'],
                     ('a', 'b', 'c'),
                     {'a': 1, 'b': 2, 'c': 3}
                     ]
        for var in test_vars:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_bools(var), None)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_bools(var), type(None))


class TestConvertInts(unittest.TestCase):
    def test_none_to_int(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(None), None)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(None), type(None))

    def test_bool_to_int(self):
        test_vars = {True: 1, False: 0}
        for k, v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer))

    def test_float_to_int(self):
        for var in np.arange(0.0, 10.0, 0.01):
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(var), int(round(var, 0)))
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(var), (int, np.integer))

    def test_strnone_to_int(self):
        test_vars = {'NONE': None, 'none': None, 'None': None, ' None': None, 'NONE ': None,
                     'NA': None, 'na': None, 'Na': None, ' Na': None, 'NA ': None,
                     'NAN': None, 'nan': None, 'Nan': None, ' Nan': None, 'NAN ': None,
                     'N/A': None, 'n/a': None, 'N/a': None, ' N/a': None, 'N/A ': None,
                     'NULL': None, 'null': None, 'Null': None, ' Null': None, 'NULL ': None,
                     '': None, ' ': None}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer, type(None)))

    def test_strbool_to_int(self):
        test_vars = {'TRUE': 1, 'true': 1, 'True': 1, ' True': 1, 'TRUE ': 1,
                     'YES': 1, 'yes': 1, 'Yes': 1, ' Yes': 1, 'YES ': 1,
                     'Y': 1, 'y': 1, ' y': 1, 'Y ': 1,
                     'T': 1, 't': 1, ' t': 1, 'T ': 1,
                     'FALSE': 0, 'false': 0, 'False': 0, ' False': 0, 'FALSE ': 0,
                     'NO': 0, 'no': 0, 'No': 0, ' No': 0, 'NO ': 0,
                     'N': 0, 'n': 0, ' n': 0, 'N ': 0,
                     'F': 0, 'f': 0, ' f': 0, 'F ': 0}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer, type(None)))

    def test_strpct_to_int(self):
       test_vars = {'%12': None, '%12%12 ': None, '12%': 12, '12.4%': 12,
                    '12.65%': 13, '12.50%': 12, '12.00%': 12,
                    ' 12.00%': 12, '12.00% ': 12, '12.00 %': 12}
       for k,v in test_vars.items():
           self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
           self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer, type(None)))

    def test_strcurr_to_int(self):
        test_vars = {'$10,000.00': 10000, '$10,000.50': 10000, '$10,000.65': 10001,
                     '$10,000.50 ': 10000, ' $10,000.50': 10000, '$10,000.55 $': 10001,
                     '£10,000.50 ': 10000, ' £10,000.50': 10000, '£10,000.55 £': 10001,
                     '€10,000.50 ': 10000, ' €10,000.50': 10000, '€10,000.55 €': 10001}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer, type(None)))

    def test_strbps_to_int(self):
        test_vars = {'10bps': 10, '50bps': 50, '100bps': 100,
                     'bps10': None, ' bps10': None, '  10bps': 10, '10 bps': 10}
        #TODO: FINISH THIS TEST WITH MORE VALUES
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer, type(None)))

    def test_strnum_to_int(self):
        test_vars = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                     '0.00': 0, '1.15': 1, '2.65': 3, '3.50': 4, '4.00': 4, '5.50': 6}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), (int, np.integer, type(None)))

    def test_strother_to_int(self):
        test_vars = {'this is a string': None,
                     'ThIS is AnoTHer StriNG ': None,
                     '    Blah blah blah': None}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(k), type(None))

    def test_others_to_ints(self):
        test_vars = [datetime.datetime.now(),
                     datetime.date.today(),
                     ['a', 'b', 'c'],
                     ('a', 'b', 'c'),
                     {'a': 1, 'b': 2, 'c': 3}
                     ]
        for var in test_vars:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_ints(var),None)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_ints(var), type(None))


class TestConvertFloats(unittest.TestCase):
    def test_none_to_float(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_floats(None), None)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(None), type(None))

    def test_empty_to_float(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_floats(''), None)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(''), type(None))

    def test_strnone_to_float(self):
        test_vars = {'NONE': None, 'none': None, 'None': None, ' None': None, 'NONE ': None,
                     'NA': None, 'na': None, 'Na': None, ' Na': None, 'NA ': None,
                     'NAN': None, 'nan': None, 'Nan': None, ' Nan': None, 'NAN ': None,
                     'N/A': None, 'n/a': None, 'N/a': None, ' N/a': None, 'N/A ': None,
                     'NULL': None, 'null': None, 'Null': None, ' Null': None, 'NULL ': None,
                     '': None, ' ': None}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_floats(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(k), (float, np.floating, type(None)))

    def test_strbool_to_float(self):
        test_vars = {'TRUE': 1, 'true': 1, 'True': 1, ' True': 1, 'TRUE ': 1,
                     'YES': 1, 'yes': 1, 'Yes': 1, ' Yes': 1, 'YES ': 1,
                     'Y': 1, 'y': 1, ' y': 1, 'Y ': 1,
                     'T': 1, 't': 1, ' t': 1, 'T ': 1,
                     'FALSE': 0, 'false': 0, 'False': 0, ' False': 0, 'FALSE ': 0,
                     'NO': 0, 'no': 0, 'No': 0, ' No': 0, 'NO ': 0,
                     'N': 0, 'n': 0, ' n': 0, 'N ': 0,
                     'F': 0, 'f': 0, ' f': 0, 'F ': 0}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_floats(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(k), (float, np.floating, type(None)))

    def test_strcurr_to_float(self):
        for val in np.arange(1.0, 5.0, .01):
            val_dollar = '${:,.2f}'.format(val)
            val_pound = '£{:,.2f}'.format(val)
            val_euro = '€{:,.2f}'.format(val)
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_dollar), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_dollar),
                                  (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_pound), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_pound),
                                  (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_euro), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_euro),
                                  (float, np.floating, type(None)))
        for val in np.arange(490000.0, 500000.0, .25):
            val_dollar = '${:,.2f}'.format(val)
            val_pound = '£{:,.2f}'.format(val)
            val_euro = '€{:,.2f}'.format(val)
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_dollar), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_dollar),
                                  (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_pound), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_pound),
                                  (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_euro), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_euro),
                                  (float, np.floating, type(None)))

    def test_strpct_to_float(self):
        for val in np.arange(1.0, 100.0, 0.125):
            val_pct_1 = '{:,.3f} %'.format(val)
            val_pct_2 = '{:,.3f}%'.format(val)
            val_pct_3 = '% {:,.3f}'.format(val)
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_pct_1), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_pct_1),
                                    (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_pct_2), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_pct_2),
                                    (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_pct_3), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_pct_3),
                                    (float, np.floating, type(None)))

    def test_strbps_to_float(self):
        for val in np.arange(1.0, 100.0, 1.0):
            val_bps_1 = '{:,.3f} bps'.format(val)
            val_bps_2 = '{:,.3f}bps'.format(val)
            val_bps_3 = 'bps {:,.3f}'.format(val)
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_bps_1), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_bps_1),
                                    (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_bps_2), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_bps_2),
                                    (float, np.floating, type(None)))
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_bps_3), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_bps_3),
                                    (float, np.floating, type(None)))

    def test_strnum_to_float(self):
        for val in np.arange(1.0, 100.0, 0.125):
            val_str = str(val)
            self.assertAlmostEqual(varsconfig.AssetVariableConfig.convert_floats(val_str), val)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(val_str),(float, np.floating, type(None)))

    def test_strother_to_float(self):
        test_vars = {'this is a string': None,
                     'ThIS is AnoTHer StriNG ': None,
                     '    Blah blah blah': None}
        for k, v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_floats(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(k), type(None))

    def test_others_to_float(self):
        test_vars = [datetime.datetime.now(),
                     datetime.date.today(),
                     ['a', 'b', 'c'],
                     ('a', 'b', 'c'),
                     {'a': 1, 'b': 2, 'c': 3}
                     ]
        for var in test_vars:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_floats(var), None)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_floats(var), type(None))


class TestConvertStrs(unittest.TestCase):
    def test_none_to_str(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(None), None)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(None), type(None))

    def test_bool_to_str(self):
        test_vars = {True: 'True', False: 'False'}
        for k,v in test_vars.items():
            self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(k), v)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(k), str)

    def test_convert_strs__int_to_str(self):
        for var in range(1, 10):
            self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), str(var))
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_convert_strs__float_to_str(self):
        for var in np.arange(1.0, 10.0, 0.1):
            self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), str(var))
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_convert_strs__str_to_str(self):
        for var in ['a', 'b', 'c', 'd']:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), var)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_convert_strs__date_to_str(self):
        var = datetime.date(1982,4,13)
        self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), '1982-04-13')
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_convert_strs__datetime_to_str(self):
        var = datetime.datetime(1982,4,13)
        self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), '1982-04-13 00:00:00')
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_list_to_str(self):
        var = [1, 2, 3]
        self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), "[1, 2, 3]")
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_dict_to_str(self):
        var = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), "{'a': 1, 'b': 2, 'c': 3}")
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

    def test_tuple_to_str(self):
        var = ('a', 'b', 'c')
        self.assertEqual(varsconfig.AssetVariableConfig.convert_strs(var), "('a', 'b', 'c')")
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_strs(var), str)

class TestConvertDates(unittest.TestCase):
    def setUp(self) -> None:
        self.test_date = datetime.date(1982,4,13)
        self.test_datetime = datetime.datetime(1982,4,13,12,8,45)
        self.test_int_date_py = 19820413
        self.test_int_date_xl = 30054
        self.test_float_date_py = 19820413.00
        self.test_float_date_xl = 30054.00
        self.test_str_date = '1982-04-13'
        self.test_str_date2 = '19820413'
        self.test_str_datetime = '1982-04-13 12:08:45'

        self.date_formats = [
                            '%Y-%m-%d',           # 2023-07-21
                            '%m/%d/%Y',           # 07/21/2023
                            '%d/%m/%Y',           # 21/07/2023
                            '%Y.%m.%d',           # 2023.07.21
                            '%Y %b %d',           # 2023 Jul 21
                            '%A, %B %d, %Y',      # Friday, July 21, 2023
                            '%d %B %Y',           # 21 July 2023
                            '%m-%d-%Y',           # 07-21-2023
                            '%d-%m-%Y',           # 21-07-2023
                            '%B %d, %Y',          # July 21, 2023
                            '%b %d, %Y',          # Jul 21, 2023
                            '%Y%m%d',             # 20230721
                            ]
        self.datetime_formats = [
                            '%Y-%m-%d %H:%M:%S',        # 2023-07-21 12:34:56
                            '%m/%d/%Y %I:%M:%S %p',     # 07/21/2023 12:34:56 PM
                            '%d/%m/%Y %H:%M:%S',        # 21/07/2023 12:34:56
                            '%Y.%m.%d %H:%M:%S',        # 2023.07.21 12:34:56
                            '%Y %b %d, %I:%M:%S %p',    # 2023 Jul 21, 12:34:56 PM
                            '%A, %B %d, %Y, %H:%M:%S',  # Friday, July 21, 2023, 12:34:56
                            '%d %B %Y %H:%M:%S',        # 21 July 2023 12:34:56
                            '%m-%d-%Y %H:%M:%S',        # 07-21-2023 12:34:56
                            '%d-%m-%Y %H:%M:%S',        # 21-07-2023 12:34:56
                            '%B %d, %Y %H:%M:%S',       # July 21, 2023 12:34:56
                            '%b %d, %Y %H:%M:%S',       # Jul 21, 2023 12:34:56
                            '%Y%m%d%H%M%S',             # 20230721123456
                            ]
        self.none_types = ['NONE', 'none', 'None', ' None', 'NONE ',
                           'NA', 'na', 'Na', ' Na', 'NA ',
                           'NAN', 'nan', 'Nan', ' Nan', 'NAN ',
                           'N/A', 'n/a', 'N/a', ' N/a', 'N/A ',
                           'NULL', 'null', 'Null', ' Null', 'NULL ',
                           '', ' ', None]

    def test_none_to_date(self):
        for var in self.none_types:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(var), None)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(var), type(None))

    def test_strdate_to_date(self):
        for fmt in self.date_formats:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_date.strftime(fmt), fmt), self.test_date)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_date.strftime(fmt), fmt), datetime.date)

    def test_strdatetime_to_date(self):
        for fmt in self.datetime_formats:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_datetime.strftime(fmt), fmt), self.test_date)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_datetime.strftime(fmt), fmt), datetime.date)

    def test_date_to_date(self):
        for fmt in self.date_formats:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_date, fmt), self.test_date)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_date, fmt), datetime.date)

    def test_datetime_to_date(self):
        for fmt in self.date_formats:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_datetime, fmt), self.test_date)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_datetime, fmt), datetime.date)

    def test_int_to_date_xl(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_int_date_xl), self.test_date)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_int_date_xl), datetime.date)

    def test_int_to_date_py(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_int_date_py), self.test_date)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_int_date_py), datetime.date)

    def test_float_to_date_xl(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_float_date_xl), self.test_date)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_float_date_xl), datetime.date)

    def test_float_to_date_py(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(self.test_float_date_py), self.test_date)
        self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(self.test_float_date_py), datetime.date)

    def test_bool_to_date(self):
        self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(True), None)
        self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(False), None)

    def test_others_to_date(self):
        test_vars = [['a', 'b', 'c'],
                     ('a', 'b', 'c'),
                     {'a': 1, 'b': 2, 'c': 3}]
        for var in test_vars:
            self.assertEqual(varsconfig.AssetVariableConfig.convert_dates(var), None)
            self.assertIsInstance(varsconfig.AssetVariableConfig.convert_dates(var), type(None))


class TestReadDatesToArray(unittest.TestCase):
    def setUp(self):
        pass
        # self.test_good_datearrays = ['1982-04-13',
        #                              '1982-04-13;1982-04-14',
        #                              '1982-04-13;1982-04-14;1982-04-15',
        #                              '1982-04-13;1982-04-14;1982-04-15;1982-04-16',
        #                              '2022-01-15; 2022-02-15; 2022-03-15; 2022-04-15, \
        #                               2022-05-15, 2022-06-15, 2022-07-15, 2022-08-15, \
        #                               2022-09-15, 2022-10-15, 2022-11-15, 2022-12-15']


class TestReadRampToArray(unittest.TestCase):
    def setUp(self):
        # self.test_ramps = ['3 for 10; 5 for 2; 2; 1 ramp 15 for 5; 16, 17',
        #                    '2 for 20',
        #                    '20 ramp 1 for 10; 5 for 10',
        #                    '2,2,2, 3 ramp 10 for 5']
        #
        # self.test_lists =  [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 2, 2, 1, 1, 1, 1, 1, 1, 1],
        # self.test_tuples = (1, 2, 3, 4, 5)
        # self.test_dicts = {'a': 1, 'b': 2, 'c': 3}
        # self.test_floats = (1.0, 2.0, 3.0, 4.0, 5.0)
        # self.test_ints = (1, 2, 3, 4, 5)
        # self.test_str = 'this is an all text string, with commas; and semi-colins'
        pass




class TestNewAssetVariableConfig(unittest.TestCase):
    def setUp(self):
        self.config_path_good = pathlib.Path(pathlib.Path(__file__).parent, 'good_config.csv')
        self.config_path_bad_nofile = pathlib.Path(pathlib.Path(__file__).parent, 'no_config_file.csv')
        self.config_path_bad_filetype = pathlib.Path(pathlib.Path(__file__).parent, 'bad_filetype_config.txt')
        self.config_path_bad_header = pathlib.Path(pathlib.Path(__file__).parent, 'bad_header_config.csv')
        self.config_path_bad_datatypes = pathlib.Path(pathlib.Path(__file__).parent, 'bad_datatypes_config.csv')
        self.config_path_bad_datavalues = pathlib.Path(pathlib.Path(__file__).parent, 'bad_datavalues_config.csv')
        self.test_default_config_file = pathlib.Path(pathlib.Path(__file__).parent, 'default_config.csv')

        self.config_path_good.touch()
        self.config_path_bad_filetype.touch()
        self.config_path_bad_header.touch()
        self.config_path_bad_datatypes.touch()
        self.config_path_bad_datavalues.touch()
        # NOTE: DO NOT TOUCH DEFAULT_CONFIG_FILE.  IT IS A PRE EXISTING FILE THAT SHOULD NOT BE MODIFIED.

        self.good_header = ['FieldName',
                            'DataDesc',
                            'DataCategory',
                            'DataType',
                            'Description',
                            'PossibleValues',
                            'DefaultValue',
                            'StratFlag',
                            'StratType',
                            'StratSumSet',
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
        
        self.test_good_variables = [
            ('boolean_variable', 'categorical', 'bools', 'bool', 'this is a boolean variable', 'True;False', 'True',
             'True', 'unique_value', 'summary', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
            ('int_variable', 'numeric', 'ints', 'np.longlong', 'this is an int variable', '', 42,
             'True', 'bucket_auto', 'summary', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
            ('int_variable2', 'numeric', 'ints', 'np.longlong', 'this is also an int variable', '', 7,
             'True', 'bucket_fixed', 'summary_extended', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
            ('float_variable1', 'numeric', 'floats', 'np.longdouble', 'this is a float variable', '', 3.14159,
             'True', 'bucket_auto', 'summary', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
            ('float_variable2', 'numeric', 'floats', 'np.longdouble', 'this is also a float variable', '',  2.71828,
             'True', 'bucket_auto', 'summary_extended', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
            ('string_variable', 'categorical', 'strs', 'str', 'this is a string variable', '', 'string thing',
             'True', 'unique_value', 'performance', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
            ('date_variable', 'date', 'dates', 'datetime.date', 'this is a date variable', '', '1982-4-13',
             'True', 'vintage_month', 'summary', 'True',
             'False', 'False', 'False', 'False', 'False', 'False',
             'False', 'False', 'False', 'False', 'False', 'False',
             'True'),
        ]

        with open(self.config_path_good, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.good_header)
            for var in self.test_good_variables:
                writer.writerow(var)


    def tearDown(self):
        #self.config_path_good.unlink()
        self.config_path_bad_filetype.unlink()
        if os.path.exists(self.config_path_bad_header):
            self.config_path_bad_header.unlink()
        self.config_path_bad_datatypes.unlink()
        self.config_path_bad_datavalues.unlink()
        #NOTE: DO NOT DELETE DEFAULT CONFIG FILE BY UNLINKING

    def test_config_file_exists(self):
        self.assertTrue(os.path.exists(self.config_path_good))
        self.assertTrue(str(self.config_path_good).endswith('.csv'))
        self.assertFalse(os.path.exists(self.config_path_bad_nofile))
        self.assertTrue(str(self.config_path_bad_nofile).endswith('.csv'))
        self.assertTrue(os.path.exists(self.config_path_bad_filetype))
        self.assertFalse(str(self.config_path_bad_filetype).endswith('.csv'))
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_exists(self.config_path_good))
        self.assertRaises(FileExistsError, varsconfig.AssetVariableConfig._check_config_file_exists, self.config_path_bad_nofile)
        self.assertRaises(FileExistsError, varsconfig.AssetVariableConfig._check_config_file_exists, self.config_path_bad_filetype)

    def test_config_file_good_header(self):
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_header(self.config_path_good))

    def test_config_file_bad_header(self):
        for i in range(0, len(self.good_header)):
            self.config_path_bad_header.touch()
            bad_header = self.good_header.copy().pop(i)
            with open(self.config_path_bad_header, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(bad_header)
            self.assertRaises(ImportError, varsconfig.AssetVariableConfig._check_config_file_header, self.config_path_bad_header)
            self.config_path_bad_header.unlink()

    def test_config_file_good_datatypes(self):
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_exists(self.config_path_good))
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_header(self.config_path_good))
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_data(self.config_path_good))

    def test_config_file_bad_datatypes(self):
        pass

    def test_default_config_file(self):
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_exists(self.test_default_config_file))
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_header(self.test_default_config_file))
        self.assertTrue(varsconfig.AssetVariableConfig._check_config_file_data(self.test_default_config_file))



if __name__ == '__main__':
    unittest.main()


