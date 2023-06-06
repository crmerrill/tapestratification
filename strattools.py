
import math
import pandas as pd
import numpy as np
import varsconfig
from CFEngine.cmutils.mathutils import round_to_nearest



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


def bucketize_data(dataframe: pd.DataFrame, variable: str, max_buckets: int = 10, **kwargs) -> list:

    min_value = dataframe[variable].min()
    max_value = dataframe[variable].max()

    def lowest_bucket(value: float = min_value, precision: int = kwargs.get('round_precision', 2)):
        if value < 1:
            factor = 10000
            precision = precision + 1
        else:
            factor = 1
        value = value * factor
        return round_to_nearest(value, base=5 * 10 ** (int(math.log10(value)) - (precision - 1)), method='down') / factor

    def highest_bucket(value: float = max_value, precision: int = kwargs.get('round_precision', 2)):
        if value < 1:
            factor = 10000
            precision = precision + 1
        else:
            factor = 1
        value = value * factor
        return round_to_nearest(value, base=5 * 10 ** (int(math.log10(value)) - (precision - 1)), method='up') / factor

    if max_value < 1:
        round_base = .0025
        bucket_mult = 100
    elif max_value > 1 and min_value < 1 and min_value != 0:
        round_base = .0025
        bucket_mult = 100
    else:
        round_base = .25
        bucket_mult = 1

    buckets_dict = {
        'fico': ('bucket', (540, 580, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800)),
        'ltv': ('bucket', [val / bucket_mult for val in (30.0, 40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0)]),
        'dti': ('bucket', [val / bucket_mult for val in (10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0)]),
        'term': ('bucket', (3, 6, 12, 24, 36, 48, 60, 84, 120, 180, 240, 360, 420)),
        'rate': ('step', round_to_nearest(((highest_bucket() - lowest_bucket()) / max_buckets),
                                          base=round_base, method='down') if 'rate' in variable else None),
        'margin': ('step', round_to_nearest(((highest_bucket() - lowest_bucket()) / max_buckets),
                                            base=round_base, method='down') if 'margin' in variable else None),
    }

    if dataframe[variable].dtype in \
            (str, pd.StringDtype, 'str', 'string', object, 'object', pd.CategoricalDtype, 'category'):
        return dataframe[variable_name].unique().tolist()
    else:
        preset_bucket = False
        top_bucket = highest_bucket()
        bottom_bucket = lowest_bucket()
        for k in buckets_dict.keys():
            if k in variable:
                preset_bucket = k
            else:
                pass
        if preset_bucket is not False:
            if buckets_dict[preset_bucket][0] == 'bucket':
                return list(buckets_dict[preset_bucket][1])
            elif buckets_dict[preset_bucket][0] == 'step':
                step_size = buckets_dict[preset_bucket][1]
                return [bottom_bucket + step_size * i for i in range(max_buckets + 1)]
        else:
            step_size = (top_bucket - bottom_bucket) / max_buckets
            return [bottom_bucket + step_size * i for i in range(max_buckets + 1)]



class Stratification:

    req_fields_consumer = ('bal_orig', 'bal_curr', 'rate_margin', 'term_orig', 'term_rem', 'fico_orig', 'fico_curr',
                           'uw_ltv_orig', 'bal_orig_cum', 'prop_appraisal', 'uw_dti_orig', 'fc_status', 'bk_status',
                           'state', 'mod_type')

    req_fields_consumer_servicing = ('svc_rate_pt', 'svc_fee_gross', 'svc_fee_net', 'svc_fee_gtee', 'svc_fee_late',
                                     'svc_fee_pmt', 'svc_adv_balrec', 'svc_adv_balnorec', 'svc_adv_tp_balrec',
                                     'esc_currbal', 'esc_advbal')

    req_fields_consumer_auto = ()

    req_fields_consumer_student = ()

    req_fields_consumer_card = ()


    def __init__(self, tape, variable, **kwargs):
        self.tape = tape
        self.tape_consumer_mortgage = tape[tape['productdesc']=='consumer_mortgage'].set_index('loanid', inplace=True)
        self.tape_consumer_heloc = tape[tape['productdesc']=='consumer_heloc'].set_index('loanid', inplace=True)
        self.tape_consumer_servicing = tape[tape['productdesc']=='consumer_servicing'].set_index('loanid', inplace=True)
        self.tape_consumer_auto = tape[tape['productdesc']=='consumer_auto'].set_index('loanid', inplace=True)
        self.tape_consumer_student = tape[tape['productdesc']=='consumer_student'].set_index('loanid', inplace=True)
        self.tape_consumer_card = tape[tape['productdesc']=='consumer_card'].set_index('loanid', inplace=True)
        self.tape_consumer_unsecured = tape[tape['productdesc']=='consumer_unsecured'].set_index('loanid', inplace=True)
        self.variable = variable
        self.buckets = kwargs.get('buckets', bucketize_data(tape, variable))
        self.strat_consumer_mortgage = None
        self.strat_consumer_heloc = None
        self.strat_consumer_servicing = None
        self.strat_consumer_auto = None
        self.strat_consumer_student = None
        self.strat_consumer_card = None
        self.strat_consumer_unsecured = None
        self.stratify()


    def strat_summary(self, stratification_variable: str, stratification_buckets: list = None) -> pd.DataFrame:
        if stratification_variable in self.tape.columns and stratification_buckets is None:
            stratification_buckets = bucketize_data(self.tape, stratification_variable)
        elif stratification_variable in self.tape.columns and stratification_buckets is not None:
            stratificaiton_buckets = [stratification_buckets] if type(stratification_buckets) is not list else stratification_buckets
        elif stratification_variable not in self.tape.columns:
            raise ValueError(f'Stratification variable {stratification_variable} not found in dataframe.')
        else:
            raise ValueError(f'Unknown error with stratification variable {stratification_variable}.')

        top_1_state = \
        dataframe[['prop_state', 'count']].groupby(['prop_state']).count().sort_values(by='count', ascending=False)[
        :1].index[0]
        top_2_state = \
        dataframe[['prop_state', 'count']].groupby(['prop_state']).count().sort_values(by='count', ascending=False)[
        1:2].index[0]

        origbal_wa_zero = weighted_average_factory(weights=dataframe['origbal'], zeros=0)
        origbal_wa_zero_int = weighted_average_factory(weights=dataframe['origbal'], zeros=0, rounding=True,
                                                       output_type='int')
        currbal_wa_zero = weighted_average_factory(weights=dataframe['currbal'], zeros=0)
        currbal_wa_zero_int = weighted_average_factory(weights=dataframe['currbal'], zeros=0, rounding=True,
                                                       output_type='int')
        origbal_wa_na = weighted_average_factory(weights=dataframe['origbal'])
        origbal_wa_na_int = weighted_average_factory(weights=dataframe['origbal'], rounding=True, output_type='int')
        currbal_wa_na = weighted_average_factory(weights=dataframe['currbal'])
        currbal_wa_na_int = weighted_average_factory(weights=dataframe['currbal'], rounding=True, output_type='int')


        summary_strat = dataframe.groupby(stratification_variable).agg(
            count=('bal_orig', 'count'),
            count_pct=('bal_orig', lambda x: round(x.count() / self.tape['bal_orig'].count() * 100, 3)),
            origbal=('bal_orig', 'sum'),
            origbal_pct=('bal_orig', lambda x: round(x.sum() / self.tape['bal_orig'].sum() * 100, 3)),
            currbal=('bal_curr', 'sum'),
            currbal_pct=('bal_curr', lambda x: round(x.sum() / self.tape['bal_curr'].sum() * 100, 3)),
            factor=('bal_curr', lambda x: round(x.sum() / self.tape.loc[x.index, 'bal_orig'].sum() * 100, 3)),
            wa_origrate=('rate_margin', origbal_wa_zero),
            wa_origterm=('term_orig', origbal_wa_zero_int),
            wa_origfico=('fico_orig', origbal_wa_zero_int),
            wa_currfico=('fico_curr', currbal_wa_zero_int),
            wa_origltv=('uw_ltv_orig', origbal_wa_zero),
            wa_origcltv=('bal_orig_cum', lambda x: x.sum() / self.tape.loc[x.index, 'prop_appraisal'].sum()),
            wa_currltv=('bal_curr', lambda x: x.sum() / self.tape.loc[x.index, 'prop_appraisal'].sum()),
            wa_origdti=('uw_dti_orig', origbal_wa_zero),
            fc_pct=('fc_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            bk_pct=('bk_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            CA_pct=('state', lambda x: round(x.str.contains('CA').sum() / x.count() * 100, 3)),
            FL_pct=('state', lambda x: round(x.str.contains('FL').sum() / x.count() * 100, 3)),
            TX_pct=('state', lambda x: round(x.str.contains('TX').sum() / x.count() * 100, 3)),
            Top1_pct=(
            'state', lambda x: round(x.str.contains(x.value_counts().index[0]).sum() / x.count() * 100, 3))
            # Top2_pct = ('state', lambda x: round(x.str.contains(x.value_counts().index[1]).sum()/x.count()*100,3))
            # 60day_dpd_pct = ('dq_string', lambda x: round(x.str.contains('60').sum()/x.count()*100,3))
        )
        return summary_strat

    def strat_performance(self):
        pass

    def strat_servicing(self, ):
        servicing_strat = dataframe.groupby(stratification_variable).agg(
            count_pct=('bal_orig', lambda x: round(x.count() / self.tape['bal_orig'].count() * 100, 3)),
            origbal_pct=('bal_orig', lambda x: round(x.sum() / self.tape['bal_orig'].sum() * 100, 3)),
            currbal=('bal_curr', 'sum'),
            currbal_pct=('bal_curr', lambda x: round(x.sum() / self.tape['bal_curr'].sum() * 100, 3)),
            factor=('bal_curr', lambda x: round(x.sum() / self.tape.loc[x.index, 'bal_orig'].sum() * 100, 3)),
            wa_rate=('rate_margin', currbal_wa_zero),
            wa_ptrate=('svc_rate_pt', currbal_wa_zero),
            wa_origterm=('term_age', origbal_wa_zero_int),
            wa_svcfee_gross=('svc_fee_gross', currbal_wa_zero),
            wa_svcfee_net=('svc_fee_net', currbal_wa_zero),
            wa_fee_gtee=('svc_fee_gtee', currbal_wa_zero),
            wa_fee_late=('svc_fee_late', currbal_wa_zero),
            wa_fee_pmt=('svc_fee_pmt', currbal_wa_zero),
            wa_adv_rec=('svc_adv_balrec', currbal_wa_zero),
            wa_adv_norec=('svc_adv_balnorec', currbal_wa_zero),
            wa_adv_tprec=('svc_adv_tp_balrec', currbal_wa_zero),
            wa_escrow=('esc_currbal', currbal_wa_zero),
            wa_escrow_adv=('esc_advbal', currbal_wa_zero),
            mod_pct=('mod_type', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            fc_pct=('fc_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            bk_pct=('bk_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100))
        return servicing_strat

    def strat_line_utilization(self):
        pass

    def stratify(self):
        pass

class Stratification_Package:
    def __init__(self, data_tape: pd.DataFrame, config: varsconfig.AssetVariableConfig):
        self.tape = data_tape
        self.stratification_variables = [x for x in config.stratification_variables if x in self.tape.columns]




    def summary_package(self, **kwargs):
        pass