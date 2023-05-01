class Stratification:
    def __init__(self, tape, variable, buckets):
        self.tape = tape
        self.variable = variable
        self.buckets = buckets
        self.stratified_tape = None
        self.stratified_tape = self.stratify()
        self.stratified_tape = self.stratify()

    def _get_lowest_bucket(self, precision=2):
        x = self.tape[self.variable].min()
        if x < 1:
            factor = 10000
            precision = precision + 1
        else:
            factor = 1
        x = x * factor
        return round_to_nearest(x, base=5 * 10 ** (int(math.log10(x)) - (precision - 1)), \
                                method='down') / factor

    def _get_highest_bucket(self, precision=2):
        x = self.tape[self.variable].max()
        if x < 1:
            factor = 10000
            precision = precision + 1
        else:
            factor = 1
        x = x * factor
        return round_to_nearest(x, base=5 * 10 ** (int(math.log10(x)) - (precision - 1)), \
                                method='up') / factor

    def bucketize_data(self, max_buckets=10, **kwargs) -> list:

        min_value = self.tape[self.variable].min()
        max_value = self.tape[self.variable].max()

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
            'rate': ('step', round_to_nearest(((self._get_highest_bucket() - self._get_lowest_bucket()) / max_buckets),
                                              base=round_base, method='down') if 'rate' in self.variable else None),
            'margin': ('step', round_to_nearest(((self._get_highest_bucket() - self._get_lowest_bucket()) / max_buckets),
                                                base=round_base, method='down') if 'margin' in self.variable else None),
        }

        if self.tape[self.variable].dtype in \
                (str, pd.StringDtype, 'str', 'string', object, 'object', pd.CategoricalDtype, 'category'):
            return dataframe[variable_name].unique().tolist()
        else:
            preset_bucket = False
            for k in buckets_dict.keys():
                if k in self.variable:
                    preset_bucket = k
                    break
                else:
                    pass
            if preset_bucket:
                if buckets_dict[preset_bucket][0] == 'bucket':
                    return list(buckets_dict[preset_bucket][1])
                elif buckets_dict[preset_bucket][0] == 'step':
                    top_bucket = self._get_highest_bucket()
                    bottom_bucket = self._get_lowest_bucket()
                    step_size = buckets_dict[preset_bucket][1]
                    return [bottom_bucket + step_size * i for i in range(max_buckets + 1)]
            else:
                top_bucket = self._get_highest_bucket()
                bottom_bucket = self._get_lowest_bucket()
                step_size = (top_bucket - bottom_bucket) / max_buckets
                return [bottom_bucket + step_size * i for i in range(max_buckets + 1)]
