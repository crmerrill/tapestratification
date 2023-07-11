import os
import datetime as dt
import numpy as np
import numpy_financial as npf
import pandas as pd
import CFEngine.cmutils.sysutils as sysutils
import varsconfig as config
from IPython.display import HTML, display

def import_raw_data(tape_file_path: str, header_map: (str, dict) = None, **kwargs) -> pd.DataFrame:
    """
    Import raw tape file of multiple format types into a pandas dataframe, with option to remap header names.
    :param str tape_file_path: path to tape file.  File type can be csv, tsv, txt, xlsx, xls, or sql_query=<query>.
            If sql_query, then tape_file_path is the query string and db connection string is required.
    :param str header_map: path to header map file
    :param optional kwargs: optional arguments
        :keyword str delimiter: delimiter for csv, tsv, txt tape files
        :keyword str sheet_name: sheet name for xlsx, xls tape files
        :keyword list parse_dates: list of columns to parse as dates.  Default is False
        :keyword function date_parser: function to use for parsing dates.  Default is None
        :keyword dict converters: dict of functions for converting values in certain columns.  Default is None
        :keyword dict dtype: dict of column names and types for columns. Default is None
        :keyword list index_col: list of columns to use as index. Default is first column.
        :keyword str db_connection_string: connection string for sql query
        :keyword str header_delimiter: delimiter for header map file for tsv, txt files
        :keyword str header_sheet_name: sheet name for header map file for xlsx, xls files


    :return: pandas dataframe
    :exception FileNotFoundError: if tape_file_path does not exist
    :exception ImportError: if tape_file_path is not a supported file type
    :exception ImportWarning: if header_map is not a supported file type
    Note: Exception handling does not occur in this function.  It must be handled in the calling function or by the user.
    """
    if sysutils.check_file_exists(tape_file_path) is False:
        raise FileNotFoundError(f'File {tape_file_path} does not exist')
    elif tape_file_path.strip().lower().endswith('.csv'):
        delim = kwargs.get('delimiter', ',')
        tape_data = pd.read_csv(tape_file_path.strip(), delimiter=delim, parse_dates=kwargs.get('parse_dates', False),
                                date_parser=kwargs.get('date_parser', None), converters=kwargs.get('converters', None),
                                dtype=kwargs.get('dtype', None), index_col=kwargs.get('index_col', 0))
    elif tape_file_path.strip().lower().endswith('.tsv') or tape_file_path.lower.endswith('.txt'):
        delim = kwargs.get('delimiter', '\t')
        tape_data = pd.read_csv(tape_file_path.strip(), delimiter=delim, parse_dates=kwargs.get('parse_dates', False),
                                date_parser=kwargs.get('date_parser', None), converters=kwargs.get('converters', None),
                                dtype=kwargs.get('dtype', None), index_col=kwargs.get('index_col', 0))
    elif tape_file_path.endswith('.xlsx') or tape_file_path.endswith('.xls'):
        tape_data = pd.read_excel(tape_file_path, sheet_name=kwargs.get('sheet_name', 0),
                                  parse_dates=kwargs.get('parse_dates', False),
                                  date_parser=kwargs.get('date_parser', None), converters=kwargs.get('converters', None),
                                  dtype=kwargs.get('dtype', None), index_col=kwargs.get('index_col', 0))
    #SQL Query is still in development
    elif tape_file_path.strip().lower().beginwith('sql_query='):
        sql_query = tape_file_path.strip().lower().replace('sql_query=', '')
        tape_data = pd.read_sql(sql_query, kwargs.get('db_connection'))
    else:
        raise ImportError(
            f'File {tape_file_path} is not a valid file type.  Must use .csv, .tsv, .txt, .xls, .xlsx, or sql_query=<query>')
    if header_map is None:
        return tape_data
    elif isinstance(header_map, dict):
        tape_data = tape_data.rename(columns=header_map)
    elif header_map.lower().endswith('.csv'):
        header_map = pd.read_csv(header_map, header=0, index_col=0).to_dict()['mapped_field']
        tape_data = tape_data.rename(columns=header_map)
    elif header_map.lower().endswith('.tsv') or header_map.lower().endswith('.txt'):
        header_map = pd.read_csv(header_map, header=0, index_col=0,
                                 delimiter=kwargs.get('header_delimiter', ',')).to_dict()['mapped_field']
        tape_data = tape_data.rename(columns=header_map)
    elif header_map.lower().endswith('.xlsx'):
        header_map = pd.read_excel(header_map, header=0, index_col=0,
                                   sheet_name=kwargs.get('header_sheet_name',0)).to_dict()['mapped_field']
        tape_data = tape_data.rename(columns=header_map)
    else:
        raise ImportWarning('Unsupported header file input.  Header must be dictionary or flat file format')
    return tape_data


def _get_unique_values_dict(data_tape: pd.DataFrame, **kwargs) -> dict:
    """
    Get unique values for each column in data tape
    :param data_tape:
    :param kwargs:
        :keyword int max_unique_value_display: maximum number of unique values to display.  Default is 25
        :keyword int unique_value_id_threshold: n-unique threshold above which unique values will not be shown.  Default is 500
        :keyword list unique_value_types: list of data types to include in unique value analysis.  Default is None (which includes all data types)
    :return: dict where k=tape field (column) name, v=list of unique values
    """
    unique_values = {}
    max_unique_value_display = kwargs.get('max_unique_value_display', 25)
    unique_value_id_threshold = kwargs.get('uinque_value_absolute_threshold',500)
    unique_value_types = kwargs.get('unique_value_types', None)
    for field in data_tape.columns:
        if (unique_value_types is None or data_tape[field].dtype in unique_value_types) and \
                (data_tape[field].nunique() <= unique_value_id_threshold):
            if len(data_tape[field].unique()) > max_unique_value_display:
                values_list = []
                for value in data_tape[field].unique()[~pd.isnull(data_tape[field].unique())]:
                    values_list.append((value, data_tape[field].value_counts()[value]))
                values_list = sorted(values_list, key=lambda values:values[1], reverse=True)
                unique_values[field] = [values_list[i][0]for i in range(min(len(values_list),max_unique_value_display))]
                del values_list
            else:
                unique_values[field] = data_tape[field].unique()[~pd.isnull(data_tape[field].unique())]
        else:
            unique_values[field] = ''
    return unique_values


def tape_unique_values(data_tape: pd.DataFrame) -> pd.DataFrame:
    """
    Provides a summary of unique values for each column in data tape
    :param pd.DataFrame data_tape: data tape to analyze
    :return: pd.DataFrame with each field as a row and columns with descriptive statistics
    """
    pd.set_option('display.max_colwidth', None)
    return pd.DataFrame({
        'type': data_tape.dtypes,
        'count': data_tape.count(),
        'missing': data_tape.isna().sum(),
        'missing_pct': data_tape.isna().sum() / data_tape.shape[0],
        'unique_num': data_tape.nunique(),
        'unique_values': _get_unique_values_dict(data_tape)
    })


def tape_summary(data_tape: pd.DataFrame) -> pd.DataFrame:
    """
    Provides a detailed summary of descriptive statistics for each column in data tape
    :param pd.DataFrame data_tape:  data tape to analyze
    :return: pd.DataFrame with each field as a row and columns with descriptive statistics
    """
    pd.set_option('display.max_colwidth', None)
    return pd.DataFrame({
        'type': data_tape.dtypes,
        'count': data_tape.count(),
        'mean': data_tape.mean(numeric_only=True),
        'median': data_tape.median(numeric_only=True),
        'min': data_tape.min(numeric_only=True),
        'quart1': data_tape.quantile(0.25, numeric_only=True, interpolation='midpoint'),
        'quart2': data_tape.quantile(0.50, numeric_only=True, interpolation='midpoint'),
        'quart3': data_tape.quantile(0.75, numeric_only=True, interpolation='midpoint'),
        'max': data_tape.max(numeric_only=True),
        'missing': data_tape.isna().sum(),
        'missing_pct': data_tape.isna().sum() / data_tape.shape[0],
        'unique_num': data_tape.nunique(),
        'unique_values': _get_unique_values_dict(data_tape)
    })


def check_required_fields(data_tape: pd.DataFrame, config_data: config.AssetVariableConfig) -> (bool, list):
    """Checks to see if all required fields from a configueration object are contained in the data tape
    :param data_tape: pandas dataframe of data tape
    :param config_data: AssetVariableConfig configuration object
    :return: True if all required fields are contained in data tape, False if not
    """
    missing = False
    missing_fields = []
    for field in config_data.required_fields:
        if field not in data_tape.columns:
            print(f'Required field {field} is not contained in data tape.  Please check data tape fields')
            missing_fields.append(field)
            missing = True
        else:
            pass
    return not missing, missing_fields


def process_to_clean_tape(data_tape, config_data):
    if check_required_fields(data_tape, config_data)[0] is True:
        for variable in config_data:
            if variable in self.tape_data.columns:
                self.tape_data[variable] = self.tape_data[variable].apply(self._converter_dict[variable])
            else:
                pass
        return self.tape_data
    else:
        print('Can not process tape without required fields.  Please check tape fields and retry')
        return False


def standardize_state(state_string):
    state_string = state_string.strip().lower()
    full_name_dict = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA',
                        'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA',
                        'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
                        'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA',
                        'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO', 'montana': 'MT',
                        'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM',
                        'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
                        'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
                        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
                        'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV', 'wisconsin': 'WI',
                        'wyoming': 'WY', 'district of columbia': 'DC', 'american samoa': 'AS', 'guam': 'GU',
                        'northern mariana islands': 'MP', 'puerto rico': 'PR', 'united states minor outlying islands': 'UM',
                        'u.s. virgin islands': 'VI'}
    abbreviation_dict = {'al': 'AL', 'ak': 'AK', 'az': 'AZ', 'ar': 'AR', 'ca': 'CA', 'co': 'CO', 'ct': 'CT', 'de': 'DE',
                            'fl': 'FL', 'ga': 'GA', 'hi': 'HI', 'id': 'ID', 'il': 'IL', 'in': 'IN', 'ia': 'IA', 'ks': 'KS',
                            'ky': 'KY', 'la': 'LA', 'me': 'ME', 'md': 'MD', 'ma': 'MA', 'mi': 'MI', 'mn': 'MN', 'ms': 'MS',
                            'mo': 'MO', 'mt': 'MT', 'ne': 'NE', 'nv': 'NV', 'nh': 'NH', 'nj': 'NJ', 'nm': 'NM', 'ny': 'NY',
                            'nc': 'NC', 'nd': 'ND', 'oh': 'OH', 'ok': 'OK', 'or': 'OR', 'pa': 'PA', 'ri': 'RI', 'sc': 'SC',
                            'sd': 'SD', 'tn': 'TN', 'tx': 'TX', 'ut': 'UT', 'vt': 'VT', 'va': 'VA', 'wa': 'WA', 'wv': 'WV',
                            'wi': 'WI', 'wy': 'WY', 'dc': 'DC', 'as': 'AS', 'gu': 'GU', 'mp': 'MP', 'pr': 'PR', 'um': 'UM',
                            'vi': 'VI'}
    if state_string in full_name_dict.keys():
        return full_name_dict[state_string]
    elif state_string in abbreviation_dict.keys():
        return abbreviation_dict[state_string]
    else:
        return state_string.strip().upper()


def check_pmt_calculation(stated_pmt, original_rate, original_term, original_balance, pmt_threshold_pct=0.005, pool_threshold_pct=.025):
    calc_pmt = -np.round(npf.pmt(original_rate, original_term, original_balance), 2)
    calc_error1 = (np.divide(np.abs(np.multiply(calc_pmt, original_term) - np.multiply(stated_pmt, original_term)), np.multiply(stated_pmt, original_term)))
    calc_error2 = (np.divide(np.abs(np.multiply(calc_pmt, original_term) - np.multiply(stated_pmt, original_term)), original_balance))
    count_error1 = np.sum(calc_error1 >= pmt_threshold_pct)
    count_error2 = np.sum(calc_error2 >= pmt_threshold_pct)
    pct_error1 = count_error1 / (1 if isinstance(original_balance, (float,int)) else len(original_balance))
    pct_error2 = count_error2 / (1 if isinstance(original_balance, (float, int)) else len(original_balance))
    if (calc_error1.any() > pmt_threshold_pct or calc_error2.any() > pmt_threshold_pct) and (
            pct_error1 > pool_threshold_pct or pct_error2 > pool_threshold_pct):
        print(f'Payment difference ((pmt_c - pmt_s) * term) / (pmt_s * term) exceeds allowed threshold in {count_error1} instances or {round(pct_error1 * 100, 2)}% of pool')
        print(f'Balance difference ((pmt_c - pmt_s) * term) / origbal) exceeds allowed threshold in {count_error2} instances or {round(pct_error2 * 100, 2)}% of pool')
        return (False, pct_error1, pct_error2)

    else:
        return (True, pct_error1, pct_error2)


def check_term_consistency(original_term, promo_term, io_term, amort_term, loan_age, remaining_term, balloon_flag, pool_threshold_pct=.025):
    age_error = np.sum(original_term, -loan_age, -remaining_term)
    term_sum_error = np.sum(original_term, -promo_term, -io_term, -amort_term) if balloon_flag in (None, False) else 0
    balloon_error = np.sum( original_term, -promo_term, -io_term, -amort_term) if (balloon_flag is True and np.sum(promo_term, io_term, amort_term) < original_term) else 0
    count_age_error = np.sum(age_error != 0)
    count_term_sum_error = np.sum(term_sum_error != 0)
    count_balloon_error = np.sum(balloon_error != 0)
    pct_age_error = count_age_error / (1 if isinstance(original_term, (float, int)) else len(original_term))
    pct_term_sum_error = count_term_sum_error / (1 if isinstance(original_term, (float, int)) else len(original_term))
    pct_balloon_error = count_balloon_error / (1 if isinstance(original_term, (float, int)) else len(original_term))
    if (age_error.any() != 0 or term_sum_error.any() != 0 or balloon_error.any() != 0) and (
            pct_age_error > pool_threshold_pct or pct_term_sum_error > pool_threshold_pct or pct_balloon_error > pool_threshold_pct):
        print(f'Original term minus loan age minus remaining term does not equal zero in {count_age_error} instances or {round(pct_age_error * 100, 2)}% of pool')
        print(f'Original term minus promo term minus IO term minus amort term does not equal zero in {count_term_sum_error} instances or {round(pct_term_sum_error * 100, 2)}% of pool')
        print(f'Original term minus promo term minus IO term minus amort term does not equal zero in {count_balloon_error} instances or {round(pct_balloon_error * 100, 2)}% of pool')
        return (False, pct_age_error, pct_term_sum_error, pct_balloon_error)




def check_orig_term_and_dates(original_term, origination_date, first_payment_date, maturity_date, diff_type, pool_threshold_pct=.025):
    calc_orig_term = datetime.diff(maturity_date, origination_date, diff_type)
    calc_pmt_term = datetime.diff(maturity_date, first_payment_date)
    if calc_orig_term == original_term or calc_pmt_term == original term: 
        return True
    else: 
        return (False, {'stated_term': original_term, 'calc_term_orig': calc_orig_term, 'calc_term_pmt': calc_pmt_term})

def check_rem_term_and_dates(remaining_term, origination_date, first_payment_date, maturity_date, cutoff_date, pool_threshold_pct=.025):
    a = datetime.diff(first_payment_date, origination_date)
    b = datetime.diff(maturity_date, origination_date)
    c = datetime.diff(maturity_date, first_payment_date)
    return(a, b, c)


#NOT COMPLETE

def check_doc_types(documentation_type, income_type, asset_type, employment_type, pool_threshold_pct=.025):
    pass


def standardize_doctypes(documentation_type, income_type, asset_type, employment_type):
    doc_type_dict = {'full': ('verified', 'verified', 'verified'),
                     'alt_doc': ('alt_doc', 'alt_doc', 'verbal'),
                     'siva': ('stated', 'verified', 'verbal'),
                     'sisa': ('stated', 'stated', 'verbal'),
                     'nina': ('none', 'none', 'verbal'),
                     'no_doc': ('none', 'none', 'none')
                     }
    if documentation_type in doc_type_dict.keys():
