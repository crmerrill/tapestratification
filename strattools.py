import math
import pandas as pd
import numpy as np

def weighted_average_factory(**kwargs):
    weights = kwargs.get('weights').copy()
    zero_values = kwargs.get('zeros')
    rounding = kwargs.get('rounding')
    output_type = kwargs.get('output_type')
    def weighted_average(values):
        try:
            if zero_values is None:
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

