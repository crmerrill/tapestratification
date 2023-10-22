# This file contians utilites for general system based functions.
# These functions are not specific to any one project and are intended to be used in any project.

import os
import sys
import datetime as dt


###### File Validation Functions and Helper Functions ######

def check_input_types(input_variable, variable_type):
    """
    Helper function to check that the input variable is of the correct type.
    :param input_variable: variable to be checked
    :param variable_type: type of variable to be checked
    :return: assertion error if variable is not of correct type
    """
    if type(variable_type) in (tuple, list):
        assert type(input_variable) in variable_type
    else:
        assert type(input_variable) is variable_type


def check_data_file_type_suffix(file_name: str, file_type: str = None) -> bool:
    """
    Helper function to check that a data file suffix matches stated type or is in list of standard data file types.
    :param file_name: file name to be checked in formation *.extension
    :param file_type: file extension of type to be checked
    :return: True (valid file extension) or False (invalid file extension)
    """
    file_name = file_name.strip()
    file_name_split = file_name.split('.')
    msg = None
    try:
        msg = 'No file type specified when checking file type suffix'
        if file_name_split[-1] == file_type and file_type in ('csv', 'tsv', 'txt', 'xls', 'xlsx', 'sql'):
            return True
        elif file_type is None and file_name_split[-1] in ('csv', 'tsv', 'txt', 'xls', 'xlsx', 'sql'):
            return True
        else:
            msg = 'Invalid file name or file type specified when checking file type suffix'
            raise ValueError
    except (IndexError, ValueError):
        print(msg)
        return False


def check_file_exist(file_name:str, prefix_path:str = None) -> bool:
    """
    Helper function to check if a file and filepath exists and return a boolean
    :param file_name: name of file to check
    :param prefix_path: string of path to file
    :return: True (file exists) or False (file does not exist)
    """
    if prefix_path is None:
        full_path = file_name
    elif prefix_path[-1] in ('/', '\\'):
        full_path = ''.join([prefix_path, file_name])
    else:
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            full_path = ''.join([prefix_path, '\\', file_name])
        else:
            full_path = ''.join([prefix_path, '/', file_name])
    if os.path.exists(full_path):
        return True
    else:
        return False


def validate_data_file_name(file_name, prefix_path=None, file_type=None):
    """
    Function to check that a data file name is valid and exists in the specified path.
    :param file_name: full name of the file to be checked including file extension; can include full path
    :param prefix_path: path name to the file (if not specified in file name)
    :param file_type: type of file to be checked (csv, tsv, txt, xls, xlsx, sql)
    :return: True (file exists) or False (file does not exist)
    """
    try:
        msg = "file_name is not valid str"
        check_input_types(file_name, str)
        msg = "prefix_path is not valid str"
        check_input_types(prefix_path, (str, type(None)))
        msg = "file_type is not valid str"
        check_input_types(file_type, (str, type(None)))
        msg = 'none'
        if check_data_file_type_suffix(file_name, file_type) is True:
            return check_file_exist(file_name, prefix_path)
        else:
            msg = 'Invalid inputs'
            raise ValueError
    except AssertionError:
        print(msg)
        return False
    except ValueError:
        print(msg)
        return False
