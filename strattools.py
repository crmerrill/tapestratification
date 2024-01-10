
from functools import cached_property
import math
import pandas as pd
import numpy as np
import varsconfig
from cmutils.mathutils import round_to_nearest
from cmutils.mathutils import pandas_weighted_average_factory


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

    # def __new__(cls, *args, **kwargs):
    #     class_instance = super().__new__(cls)
    #     class_instance.required_fields_consumer = kwargs.get('config_object').required_fields_consumer
    #
    #


    def __init__(self, input_tape: pd.DataFrame, asset_class: str, stratify_by_variable: str, **kwargs) -> None:
        self.tape = None
        self.tape_type=asset_class
        self.stratify_by = stratify_by_variable
        self.reload_tape(input_tape)
        self.reload_buckets(stratify_by_variable, **kwargs)
        self.reload_weighted_average_factories(**kwargs)

    def reload_tape(self, input_tape: pd.DataFrame = None):
        if input_tape is None or input_tape.empty or self.tape_type not in input_tape['asset_sector'].unique():
            raise ValueError(f'Input tape is empty or does not contain the asset class {self.tape_type}')
        else:
            self.tape = input_tape[input_tape['asset_sector']==self.tape_type].set_index('asset_id', inplace=True)
        return self


    def reload_buckets(self, stratify_by_variable: str = self.stratify_by, **kwargs):
        self.stratify_by = stratify_by_variable
        self.buckets = kwargs.get(f'buckets_{self.tape_type}',
                                                    kwargs.get('buckets_consumer', 
                                                               kwargs.get('buckets', 
                                                                          bucketize_data(self.tape, self.stratify_by))))

    def reload_weighted_average_factories(self, **kwargs):
        """
        Reloads the weighted average functions for the stratification object.  This is required when the tape is reloaded
        :param kwargs: wa_zeros: this determines how zeros are handled.
                        If an integer is used, then the integer will replace empty or zero values.
                        Other options are ('na', 'nan', 'none', 'null') which will skip the value in the calculation
        :return: None
        """
        self._origbal_wa_zero = pandas_weighted_average_factory(weights=self.tape['bal_orig'], zeros=kwargs.get('wa_zeros', 0))
        self._origbal_wa_zero_int = pandas_weighted_average_factory(weights=self.tape['bal_orig'], zeros=kwargs.get('wa_zeros', 0), rounding=True, output_type='int')
        self._currbal_wa_zero = pandas_weighted_average_factory(weights=self.tape['bal_curr'], zeros=kwargs.get('wa_zeros', 0))
        self._currbal_wa_zero_int = pandas_weighted_average_factory(weights=self.tape['bal_curr'], zeros=kwargs.get('wa_zeros', 0), rounding=True, output_type='int')
        self._currlimit_wa_zero = pandas_weighted_average_factory(weights=self.tape['bal_limit_curr'], zeros=kwargs.get('wa_zeros', 0))
        self._currlimit_wa_zero_int = pandas_weighted_average_factory(weights=self.tape['bal_limit_curr'], zeros=kwargs.get('wa_zeros', 0), rounding=True, output_type='int')

    @staticmethod
    def strat_summary_consumer_closed(input_tape: pd.DataFrame, stratification_variable: str, stratification_buckets: list, **kwargs) -> pd.DataFrame:
        #Check that the required fields for the strat are in the input_tape:
        required_fields = ('bal_orig', 'bal_curr', 'rate_margin', 'term_orig', 'term_rem', 'fico_orig', 'fico_curr',
                            'uw_ltv_orig', 'bal_orig_cum', 'prop_appraisal', 'uw_dti_orig', 'fc_status', 'bk_status',
                            'state', 'mod_type')
        if not all(x in input_tape.columns for x in required_fields):
            raise ValueError(f'Not all required fields are present in the input_tape.  Required fields are: {required_fields}')

        #Create the weighted average functions requried for dataframe summary
        origbal_weight = pandas_weighted_average_factory(weights=input_tape['origbal'], zeros=kwargs.get('zeros', 0))
        origbal_weight_int = pandas_weighted_average_factory(weights=input_tape['origbal'],
                                                             zeros=kwargs.get('zeros', 0), rounding=True,
                                                             output_type='int')
        currbal_weight = pandas_weighted_average_factory(weights=input_tape['currbal'], zeros=kwargs.get('zeros', 0))
        currbal_weight_int = pandas_weighted_average_factory(weights=input_tape['currbal'],
                                                             zeros=kwargs.get('zeros', 0), rounding=True,
                                                             output_type='int')

        #Calculate teh top two stated by count of assets in the input_tape
        top_1_state = input_tape[['prop_state', 'count']].groupby(['prop_state']).count().sort_values(by='count', ascending=False)[:1].index[0]
        top_2_state = input_tape[['prop_state', 'count']].groupby(['prop_state']).count().sort_values(by='count', ascending=False)[1:2].index[0]

        #Create the summary dataframe
        summary_strat = input_tape.groupby(stratification_variable).agg(
            count=('bal_orig', 'count'),
            count_pct=('bal_orig', lambda x: round(x.count() / input_tape['bal_orig'].count() * 100, 3)),
            origbal=('bal_orig', 'sum'),
            origbal_pct=('bal_orig', lambda x: round(x.sum() / input_tape['bal_orig'].sum() * 100, 3)),
            currbal=('bal_curr', 'sum'),
            currbal_pct=('bal_curr', lambda x: round(x.sum() / input_tape['bal_curr'].sum() * 100, 3)),
            factor=('bal_curr', lambda x: round(x.sum() / self.tape.loc[x.index, 'bal_orig'].sum() * 100, 3)),
            wa_origrate=('rate_margin', origbal_weight),
            wa_origterm=('term_orig', origbal_weight_int),
            wa_remterm=('term_rem', currbal_weight_int),
            wa_origfico=('fico_orig', origbal_weight_int),
            wa_currfico=('fico_curr', currbal_weight_int),
            wa_origltv=('uw_ltv_orig', origbal_weight),
            wa_origcltv=('bal_orig_cum', lambda x: x.sum() / self.tape.loc[x.index, 'prop_appraisal'].sum()),
            wa_origdti=('uw_dti_orig', origbal_weight),
            fc_pct=('fc_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            bk_pct=('bk_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            # CA_pct=('state', lambda x: round(x.str.contains('CA').sum() / x.count() * 100, 3)),
            # FL_pct=('state', lambda x: round(x.str.contains('FL').sum() / x.count() * 100, 3)),
            # TX_pct=('state', lambda x: round(x.str.contains('TX').sum() / x.count() * 100, 3)),
            top1_pct=('state', lambda x: round(x.str.contains(top_1_state).sum() / x.count() * 100, 3)),
            top2_pct=('state', lambda x: round(x.str.contains(top_2_state).sum() / x.count() * 100, 3))
        )
        summary_strat.rename(columns={'top1_pct': f'{top_1_state.upper()}_pct', 'top2_pct': f'{top_2_state.upper()}_pct'}, inplace=True)
        return summary_strat

    @staticmethod
    def strat_summary_consumer_open(input_tape: pd.DataFrame, stratification_variable: str, stratification_buckets: list = None) -> pd.DataFrame:
        # Check that the required fields for the strat are in the input_tape:
        required_fields = ('bal_orig', 'bal_curr', 'rate_margin', 'term_orig', 'term_rem', 'fico_orig', 'fico_curr',
                           'uw_ltv_orig', 'bal_orig_cum', 'prop_appraisal', 'uw_dti_orig', 'fc_status', 'bk_status',
                           'state', 'mod_type')
        if not all(x in input_tape.columns for x in required_fields):
            raise ValueError(
                f'Not all required fields are present in the input_tape.  Required fields are: {required_fields}')

        # Create the weighted average functions requried for dataframe summary
        currbal_weight = pandas_weighted_average_factory(weights=input_tape['bal_curr'], zeros=kwargs.get('zeros', 0))
        currbal_weight_int = pandas_weighted_average_factory(weights=input_tape['bal_curr'],
                                                             zeros=kwargs.get('zeros', 0), rounding=True,
                                                             output_type='int')
        currlimit_weight = pandas_weighted_average_factory(weights=input_tape['origbal'], zeros=kwargs.get('zeros', 0))
        currlimit_weight_int = pandas_weighted_average_factory(weights=input_tape['origbal'],
                                                               zeros=kwargs.get('zeros', 0), rounding=True,
                                                               output_type='int')

        # Calculate teh top two stated by count of assets in the input_tape
        top_1_state = \
        input_tape[['prop_state', 'count']].groupby(['prop_state']).count().sort_values(by='count', ascending=False)[
        :1].index[0]
        top_2_state = \
        input_tape[['prop_state', 'count']].groupby(['prop_state']).count().sort_values(by='count', ascending=False)[
        1:2].index[0]


        summary_strat = input_tape.groupby(stratification_variable).agg(
            count=('bal_limit_curr', 'count'),
            count_pct=('bal_limit_curr', lambda x: round(x.count() / input_tape['bal_limit_curr'].count() * 100, 3)),
            currbal=('bal_curr', 'sum'),
            currbal_pct=('bal_curr', lambda x: round(x.sum() / input_tape['bal_curr'].sum() * 100, 3)),
            currlimit=('bal_limit_curr', 'sum'),
            currlimit_pct=('bal_limit_curr', lambda x: round(x.sum() / input_tape['bal_limit_curr'].sum() * 100, 3)),
            currutil=('bal_curr', lambda x: round(x.sum() / input_tape[x.index, 'bal_limit_curr'].sum() * 100, 3)),
            wa_origrate=('rate_margin', origbal_wa_zero),
            wa_origfico=('fico_orig', origbal_wa_zero_int),
            wa_currfico=('fico_curr', currbal_wa_zero_int),
            wa_origdti=('uw_dti_orig', origbal_wa_zero),
            fc_pct=('fc_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            bk_pct=('bk_status', lambda x: x.count() / (x.count() + x.isna().sum()) * 100),
            CA_pct=('state', lambda x: round(x.str.contains('CA').sum() / x.count() * 100, 3)),
            FL_pct=('state', lambda x: round(x.str.contains('FL').sum() / x.count() * 100, 3)),
            TX_pct=('state', lambda x: round(x.str.contains('TX').sum() / x.count() * 100, 3)),
            top1_pct=('state', lambda x: round(x.str.contains(top_1_state).sum() / x.count() * 100, 3)),
            top2_pct = ('state', lambda x: round(x.str.contains(top_2_state).sum() / x.count()*100,3))
            #60day_dpd_pct = ('dq_string', lambda x: round(x.str.contains('60').sum()/x.count()*100,3))
        )
        return summary_strat


    
    
    
    
    
    # def strat_summary_extended(self):
    #     summary_extended_strat = dataframe.groupby(stratification_variable).agg(
    #         count=('bal_orig', 'count'),
    #         count_pct=('bal_orig', lambda x: round(x.count() / self.tape['bal_orig'].count() * 100, 3)),
    #         origbal=('bal_orig', 'sum'),
    #         origbal_pct=('bal_orig', lambda x: round(x.sum() / self.tape['bal_orig'].sum() * 100, 3)),
    #         currbal=('bal_curr', 'sum'),
    #         currbal_pct=('bal_curr', lambda x: round(x.sum() / self.tape['bal_curr'].sum() * 100, 3))
    #
    #         term_orig=('term_orig', origbal_wa_zero_int),
    #         term_rem=('term_rem', currbal_wa_zero_int),
    #
    #         margin=('rate_margin', origbal_wa_zero),
    #         currrate=('rate_curr', currbal_wa_zero),
    #
    #
    #         fico_orig_1=('fico_orig', origbal_wa_zero_int),
    #         fico_orig_2=('fico_orig_borrower2', origbal_wa_zero_int),
    #
    #         fico_curr_1=('fico_curr', origbal_wa_zero_int),
    #         fico_curr_2=('fico_curr_borrower2', origbal_wa_zero_int),
    #         income_stated=('uw_inc_stated', origbal_wa_zero_int)
    #         income_verified=('uw_inc_verify', origbal_wa_zero_int)
    #         dti_orig
    #         dti_curr
    #         prop_value
    #         prop_value_age
    #         ltv_orig
    #         ltv_curr
    #         cltv_orig
    #         cltv_curr
    #     )
        pass

    def strat_performance(self):
        #count
        #curr_bal
        #factor
        #wa_fico
        #wa_origterm
        #wala
        #orig_margin
        #curr_margin
        #late_margin
        #NPL_margin
        #%Curr
        #%30
        #%60
        #%90
        #%120+
        #%BK
        #%FC
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


class ConsumerMortgageStratification(Stratification):
    def __init__(self, tape, variable, **kwargs):
        super.__init__(tape, variable, **kwargs)


class ConsumerHelocStratification(Stratification):
    pass

class ConsumerAutoStratification(Stratification):
    pass

class ConsumerStudentStratification(Stratification):
    pass

class ConsumerCardStratification(Stratification):
    pass

class ConsumerUnsecuredStratification(Stratification):
    pass



# class Stratification_Package:
#     def __init__(self, data_tape: pd.DataFrame, config: varsconfig.AssetVariableConfig):
#         self.tape = data_tape
#         self.stratification_variables = [x for x in config.stratification_variables if x in self.tape.columns]
#
#
#
#
#     def summary_package(self, **kwargs):
#         pass