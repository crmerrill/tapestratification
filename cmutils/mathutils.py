import numpy as np
import math

def get_digits(x):
    """
    Function to get the number of digits in a number
    :param x: number to get digits of
    :return: number of digits in x
    """
    if x == 0:
        return 1
    elif type(x) is int:
        return int(np.floor(np.log10(abs(x)))) + 1
    elif type(x) is float:
        int_part = len(str(x).split('.')[0])
        dec_part = len(str(x).split('.')[1])
        return (int_part, dec_part)
    else:
        raise TypeError('x must be int or float, or numeric string')


def round_to_nearest(x, base=5, method='down'):
    """
    Function to round a number to the nearest base digit
    :param x: number to be rounded
    :param base: base digit to round to
    :param method: method of rounding (down, up, or mid)
    :return: rounded number
    """
    if method == 'down':
        return base * math.floor((x / base))
    elif method == 'up':
        return base * math.ceil((x / base))
    elif method == 'mid':
        return base * round((x / base))
    else:
        raise ValueError('method must be one of "down", "up", or "mid"')
    
def harmonic_mean(x: np.array) -> float:
    """
    Function to calculate the harmonic mean of a numpy array
    :param x: numpy array of values
    :return: float of harmonic mean
    """
    return len(x) / np.sum(1/x)

def geometric_mean(x: np.array) -> float:
    """
    Function to calculate the geometric mean of a numpy array
    :param x: numpy array of values
    :return: float of geometric mean
    """
    return np.prod(x) ** (1/len(x))

def pandas_weighted_average_factory(**kwargs) -> function:
    weights = kwargs.get('weights').copy()
    zero_values = kwargs.get('zeros')
    rounding = kwargs.get('rounding')
    output_type = kwargs.get('output_type')
    def weighted_average(values):
        try:
            if zero_values is None or str(zero_values).lower() in ('na', 'nan', 'none', 'null'):
                values_mask = ~np.isnan(values)
                if all(v is False for v in values_mask):
                    raise ValueError('there are no non-missing x variable values')
            else:
                values = values.fillna(zero_values)
                values_mask = ~np.isnan(values)
            weight = weights.loc[values.index]
            if rounding is True and output_type == 'int':
                return int(np.round(np.average(values[values_mask], weights=weight[values_mask]), 0))
            elif rounding is True:
                return np.round(np.average(values[values_mask], weights=weight[values_mask]), 0)
            else:
                return np.average(values[values_mask], weights=weight[values_mask])
        except ZeroDivisionError:
            if values.sum() != 0:
                return np.average(values)
            else:
                return 'NA'
    return weighted_average
