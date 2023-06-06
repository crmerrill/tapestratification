import os
import datetime as dt
import numpy as np
import pandas as pd
import CFEngine.cmutils.sysutils as sysutils
import varsconfig as config
from IPython.display import HTML, display


def import_raw_tape(tape_file_path: str, **kwargs) -> pd.DataFrame:
    if sysutils.check_file_exists(tape_file_path) is False:
        raise FileNotFoundError(f'File {tape_file_path} does not exist')
    elif tape_file_path.strip().lower().endswith('.csv'):
        delim = kwargs.get('delimiter') if kwargs.get('delimiter') is not None else ','
        tape_data = pd.read_csv(tape_file_path.strip(), delimiter=delim, parse_dates=kwargs.get('parse_dates'),
                                date_parser=kwargs.get('date_parser'), converters=kwargs.get('converters'),
                                dtype=kwargs.get('dtype'), index_col=kwargs.get('index_col'))
    elif tape_file_path.strip().lower().endswith('.tsv') or tape_file_path.lower.endswith('.txt'):
        delim = kwargs.get('delimiter') if kwargs.get('delimiter') is not None else '\t'
        tape_data = pd.read_csv(tape_file_path.strip(), delimiter=delim, parse_dates=kwargs.get('parse_dates'),
                                date_parser=kwargs.get('date_parser'), converters=kwargs.get('converters'),
                                dtype=kwargs.get('dtype'), index_col=kwargs.get('index_col'))
    elif tape_file_path.endswith('.xlsx') or tape_file_path.endswith('.xls'):
        tape_data = pd.read_excel(tape_file_path, sheet_name=kwargs.get('sheet_name'),
                                  parse_dates=kwargs.get('parse_dates'),
                                  date_parser=kwargs.get('date_parser'), converters=kwargs.get('converters'),
                                  dtype=kwargs.get('dtype'), index_col=kwargs.get('index_col'))
    elif tape_file_path.strip().lower().beginwith('sql_query='):
        sql_query = tape_file_path.strip().lower().replace('sql_query=', '')
        tape_data = pd.read_sql(sql_query, kwargs.get('db_connection'))
    else:
        raise ImportError(
            f'File {tape_file_path} is not a valid file type.  Must use .csv, .tsv, .txt, .xls, .xlsx, or sql_query=...')
    if kwargs.get('header_map') is None:
        return tape_data
    elif type(kwargs.get('header_map')) == dict:
        tape_data = tape_data.rename(columns=kwargs.get('header_map'))
    elif kwargs.get('header_map').lower().endswith('.csv'):
        header_map = pd.read_csv(kwargs.get('header_map'), header=0, index_col=0).to_dict()['mapped_field']
        tape_data = tape_data.rename(columns=header_map)
    elif kwargs.get('header_map').lower().endswith('.tsv') or kwargs.get('header_map').lower().endswith('.txt'):
        header_map = pd.read_csv(kwargs.get('header_map'), header=0, index_col=0,
                                 delimiter=kwargs.get('delimiter')).to_dict()['mapped_field']
        tape_data = tape_data.rename(columns=header_map)
    elif kwargs.get('header_map').lower().endswith('.xlsx'):
        header_map = pd.read_excel(kwargs.get('header_map'), header=0, index_col=0,
                                   sheet_name=kwargs.get('sheet_name')).to_dict()['mapped_field']
        tape_data = tape_data.rename(columns=header_map)
    else:
        raise ImportWarning('Unsupported header file input.  Header must be dictionary or flat file format')
    return tape_data


def _get_unique_values_dict(data_tape: pd.DataFrame) -> dict:
    unique_values = {}
    for field in data_tape.columns:
        if data_tape[field].dtype in ('object', 'string', str, object):
            unique_values[field] = [value for values in data_tape[field].unique().tolist() if str(value) != 'nan']
        else:
            unique_values[field] = ''
    return unique_values


def tape_unique_values(data_tape: pd.DataFrame) -> pd.DataFrame:
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
        'missing_pct': data_tape.isna().sum() / self.tape_data.shape[0],
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
    if check_required_fields(data_tape, config_data) is True:
        for variable in config_data:
            if variable in self.tape_data.columns:
                self.tape_data[variable] = self.tape_data[variable].apply(self._converter_dict[variable])
            else:
                pass
        return self.tape_data
    else:
        print('Can not porcess tape without required fields.  Please check tape fields and retry')
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


