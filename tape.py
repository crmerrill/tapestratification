
import os
import sys
import math
import datetime as dt
import numpy as np
import pandas as pd
sys.path.append('/Users/crmerrill/lib')
import CFEngine.cmutils.sysutils as sysutils
import assetvars_new as assetvars
from IPython.display import HTML, display

class Tape:

    def __init__(self, tape_file, tape_prep='raw', **kwargs):
        try:
            if sysutils.validate_data_file_name(tape_file) is False:
                msg = 'Invalid tape file'
                raise Exception('Invalid tape file')
            else:
                #self._config_data = kwargs.get('config_data') if kwargs.get('config_data') is not None else
                self.tape_file = tape_file
                self.tape_prep = tape_prep
                self.cut_off_date = kwargs.get('cut_off_date') if kwargs.get('cut_off_date') is not None else dt.date.today()
                self.modify_date = dt.date.today()
                self.tape_data = None
                if not os.path.exists(self.tape_file):
                    msg = 'Tape file not found'
                    raise FileNotFoundError('Tape file not found')
                elif tape_prep == 'clean':
                    self.tape_data = self.import_clean_data(tape_file, kwargs)
                else:
                    self.tape_data = self.import_raw_data(tape_file, kwargs)
                self.tape_data = self.tape_data.reset_index()
                self.tape_data = self.tape_data.set_index('loanid')
                self.tape_data = self.tape_data.sort_index()
                self.tape_data = self.tape_data.replace('nan', np.nan)
                self.tape_data = self.tape_data.replace('NA', np.nan)
                self.tape_data = self.tape_data.replace('N/A', np.nan)
                self.tape_data = self.tape_data.replace('N\\A', np.nan)
                self.fields = self.tape_data.columns()
                self.asset_types = self.tape_data['sector'].unique()
        except (Exception, FileNotFoundError):
            print(msg)
            return None


    def __repr__(self):
        return display(self.tape_data)


    def import_raw_data(self, tape_file, **kwargs):
        if tape_file.lower().endswith('.csv'):
            self.tape_data = pd.read_csv(self.tape_file, dtype=kwargs.get('dtype'))
        elif tape_file.lower().endswith('.tsv') or tape_file.lower.endswith('.txt'):
            self.tape_data = pd.read_csv(self.tape_file, delimiter=kwargs.get('delimiter'), dtype=kwargs.get('dtype'))
        elif tape_file.endswith('.xlsx'):
            self.tape_data = pd.read_excel(self.tape_file, sheet_name=kwargs.get('sheet_name'), dtype=kwargs.get('dtype'))
        #TODO: Implement SQL input
        #elif tape_file.beginwith('sql_query='):
        #    self.tape_data = pd.read_sql(tape_file, kwargs.get('sql_connection'), dtype=kwargs.get('dtype'), index_col='loanid', \
        #                             parse_dates=kwargs.get('parse_dates'), columns=kwargs.get('columns')))
        else:
            msg = 'Unsupported input type.  Use flat file format, MSExcel format, or SQL query'
            raise Exception('Unsupported input type.  Use flat file format, MSExcel format, or SQL query')
        if kwargs.get('header_map') is not None:
            if type(kwargs.get('header_map')) == dict:
                self.tape_data = self.tape_data.rename(columns=kwargs.get('header_map'))
            elif kwargs.get('header_map').lower().endswith('.csv'):
                header_map = pd.read_csv(kwargs.get('header_map'), header=0, index_col=0).to_dict()['mapped_field']
                self.tape_data = self.tape_data.rename(columns=header_map)
            elif kwargs.get('header_map').lower().endswith('.tsv') or kwargs.get('header_map').lower().endswith('.txt'):
                header_map = pd.read_csv(kwargs.get('header_map'), header=0, index_col=0, delimiter=kwargs.get('delimiter')).to_dict()['mapped_field']
                self.tape_data = self.tape_data.rename(columns=header_map)
            elif kwargs.get('header_map').lower().endswith('.xlsx'):
                header_map = pd.read_excel(kwargs.get('header_map'), header=0, index_col=0, sheet_name=kwargs.get('sheet_name')).to_dict()['mapped_field']
                self.tape_data = self.tape_data.rename(columns=header_map)
            else:
                msg = 'Unsupported header file input.  Header must be dictionary or flat file format'
                raise Exception('Unsupported header file input.  Header must be dictionary or flat file format')
        else:
            pass    
        return self


    def _get_unique_values(self):
        unique_values = {}
        for field in self.tape_data.columns:
            if self.tape_data[field].dtype in ('object', 'string', str, object):
                unique_values[field] = [value for values in self.tape_data[field].unique().tolist() if str(value) != 'nan']
            else:
                unique_values[field] = ''
        return unique_values

    @property
    def head(self):
        return self.tape_data.head()

    @property
    def unique_values(self):
        return pd.DataFrame({
            'type': self.tape_data.dtypes,
            'count': self.tape_data.count(),
            'missing': self.tape_data.isna().sum(),
            'missing_pct': self.tape_data.isna().sum() / self.tape_data.shape[0],
            'unique_num': self.tape_data.nunique(),
            'unique_values': self._get_unique_values()
        })

    @property
    def summary(self):
        pd.set_option('display.max_colwidth', None)
        return pd.DataFrame({
            'type': self.tape_data.dtypes,
            'count': self.tape_data.count(),
            'mean': self.tape_data.mean(numeric_only=True),
            'median': self.tape_data.median(numeric_only=True),
            'min': self.tape_data.min(numeric_only=True),
            'quart1': self.tape_data.quantile(0.25, numeric_only=True, interpolation='midpoint'),
            'quart2': self.tape_data.quantile(0.50, numeric_only=True, interpolation='midpoint'),
            'quart3': self.tape_data.quantile(0.75, numeric_only=True, interpolation='midpoint'),
            'max': self.tape_data.max(numeric_only=True),
            'missing': self.tape_data.isna().sum(),
            'missing_pct': self.tape_data.isna().sum() / self.tape_data.shape[0],
            'unique_num': self.tape_data.nunique(),
            'unique_values': self._get_unique_values()
        })

    # TODO create the following methods:
    def transform_variable(self, variable, transformation):
        pass

    def fill_missing_values(self, variable, treatment):
        pass

    def encode_variable(self, variable, encoding_dict):
        pass

    def create_variable(self, variable, treatment):
        pass

    def drop_variable(self, variable):
        pass

    #Utilites for processing tape_data to a fully formatted tape_data for cashflow engine use
    def _check_required_fields(self, config_data):
        for field in config_data.required_fields:
            if field not in self.tape_data.columns:
                print(f'Required field {field} is not contained in data tape.  Please check data tape fields')
                return False
            else:
                pass
        return True
        
    @staticmethod
    def _parse_tape_dates(var, dt_format='%Y%m%d'):
        if var == None or pd.isnull(var) or var == '':
            return np.nan
        elif type(var) != str:
            var = str(var)
        else:
            pass
        return dt.datetime.strptime(var, dt_format).date()

    @staticmethod
    def _get_converter_dict(groups=('ints', 'floats', 'arrays', 'bools'), config_file):
        arraydict = {
            'amortsched': _read_dates_to_array,
            'pmtsched': _read_dates_to_array,
            'schedpmtdates': _read_dates_to_array
        }
        convertdict = {}
        for grp in groups:
            for var in getattr(config_file, grp):
                if grp == 'arrays' and var in arraydict.keys():
                    convertdict[var] = arraydict[var]
                else:
                    convertdict[var] = eval(str('_convert_tape_' + str(grp).lower()))
        return convertdict

    @staticmethod
    def _convert_tape_ints(var):
        if type(var) == str or type(var) == object:
            if var == '':
                newvar = np.nan
            else:
                newvar = np.int64(np.round(np.float64(var.replace(',', '')), 0))
        elif type(var) == float:
            newvar = np.int64(np.round(var, 0))
        elif type(var) == NoneType:
            newvar = np.nan
        else:
            newvar = np.int64(var)
        return newvar

    @staticmethod
    def _convert_tape_floats(var):
        if type(var) == str or type(var) == object:
            if var == '':
                newvar = np.nan
            else:
                newvar = np.float64(var.replace(',', ''))
        elif type(var) == NoneType:
            newvar = np.nan
        else:
            newvar = np.float64(var)
        return newvar

    @staticmethod
    def _convert_tape_bools(var):
        if type(var) == str or type(var) == object:
            if var.lower() in ('true', 'yes', 'y', 't', '1'):
                newvar = np.True_
            elif var.lower() in ('false', 'no', 'n', 'f', '0'):
                newvar = np.False_
            else:
                newvar = np.False_
        elif type(var) == bool:
            newvar = np.bool_(var)
        elif type(var) == int:
            if var == 1:
                newvar = np.True_
            elif var == 0:
                newvar = np.True_
            else:
                newvar = np.False_
        elif type(var) == float:
            if var == 1.0:
                newvar = np.True_
            elif var == 0.0:
                newvar = np.False_
            else:
                newvar = np.False_
        else:
            newvar = np.False_
        return newvar

    @staticmethod
    def _read_dates_to_array(date_string):
        date_string = date_string.replace(';', ',')
        return np.array([parseLoanDates(element.strip()) for element in date_string.split(',')], dtype=datetime.date)

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

    def process_tape(self, config_data):
        if self._check_required_fields(config_data) is True:
            for variable in config_data:
                if variable in self.tape_data.columns:
                    self.tape_data[variable] = self.tape_data[variable].apply(self.converter_dict[variable])
                else:
                    pass
            return self.tape_data
        else:
            print('Can not porcess tape without required fields.  Please check tape fields and retry')
            return False 
        

    def import_clean_data(self, tape_file, input_type='csv', delimiter=None, sheet_name=None):
        # look at whether we are getting tape_data from flatfile or SQL.
        if input_type is None:
            input_type = tape_file.split('.')[-1].lower()
        elif input_type.lower() == 'sql':
            return print('SLQ not yet supported.  Write the code or use a flat file format')
            # TODO: Write SQL Code: (1) Check for No Lock in SQL string (2) Test if database exists and connection possible before query (3) run query and put into dataframe (4) enforce strict types
        else:
            # set up delimiter types for flat files:
            delimdict = {'csv': ',',
                         'tsv': '\t',
                         'txt': delimiter
                         }
            delimiter = delimdict[input_type.lower()]

            # get the header information so we know what fields are on the tape_data
            with open(tape_file) as file:
                   header = next(csv.reader(file, delimiter=delimiter))
            # TODO: need to adust header names to trim extra space
            # now we will set-up dictinaries of types and converters for pandas to use when reading files to dataframes
            # basic type and converter dictionaries
            typedict = {}
            convertdict = getConverterDict()
            datelist = list(set(assetvars.dates).intersection(header))
            for var in set(header).difference(datelist).difference(convertdict):
                typedict[var] = assetvars.getTypeDict(var)

            # Use pandas to process flat file type being input
            if input_type in ('CSV', 'csv'):
                self.tape_data = pd.read_csv(tape_file, parse_dates=datelist, date_parser=parseLoanDates, converters=convertdict,
                                             dtype=typedict)
            elif input_type in ('TSV', 'tsv', 'TXT', 'txt'):
                self.tape_data = pd.read_csv(tape_file, delimiter=delimiter, parse_dates=datelist, date_parser=parseLoanDates,
                                             converters=convertdict, dtype=typedict)
            elif input_type in ('XLS', 'xls'):
                self.tape_data = pd.read_excel(tape_file, sheet_name=sheet_name, parse_dates=datelist, date_parser=parseLoanDates,
                                               converters=convertdict, dtype=typedict)
            else:
                raise Exception('Unsupported input type.  Use flat file format, MSExcel format, or SQL query')

            return self

