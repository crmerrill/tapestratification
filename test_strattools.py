import sys
sys.path.append('/Users/crmerrill/lib')
import unittest
import pandas as pd
import numpy as np
import strattools

class TestBucketizeData(unittest.TestCase):
    def setUp(self):
        self.num_datasets = 25

    def generate_random_dataset(self):
        np.random.seed(42)
        data = {
            'fico_score': np.random.randint(500, 850, size=250),
            'original_ltv': np.random.uniform(50, 95, size=250),
            'dti_ratio': np.random.uniform(10, 50, size=250),
            'loan_term': np.random.choice([12, 24, 36, 48, 60, 84, 120, 180, 240, 360], size=250),
            'interest_rate': np.random.uniform(2, 6, size=250),
            'interest_margin': np.random.uniform(0.1, 0.5, size=250)
        }

        return pd.DataFrame(data)

    def test_bucketize_fico(self):
        for _ in range(self.num_datasets):
            df = self.generate_random_dataset()
            expected_buckets = [540, 580, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800]
            result = strattools.bucketize_data(df, 'fico_score')
            self.assertEqual(result, expected_buckets)

    def test_bucketize_ltv(self):
        for _ in range(self.num_datasets):
            df = self.generate_random_dataset()
            expected_buckets = [30.0, 40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0]
            result = strattools.bucketize_data(df, 'original_ltv')
            self.assertEqual(result, expected_buckets)

    def test_bucketize_dti(self):
        for _ in range(self.num_datasets):
            df = self.generate_random_dataset()
            expected_buckets = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0]
            result = strattools.bucketize_data(df, 'dti_ratio')
            self.assertEqual(result, expected_buckets)

    def test_bucketize_term(self):
        for _ in range(self.num_datasets):
            df = self.generate_random_dataset()
            expected_buckets = [3, 6, 12, 24, 36, 48, 60, 84, 120, 180, 240, 360, 420]
            result = strattools.bucketize_data(df, 'loan_term')
            self.assertEqual(result, expected_buckets)

    def test_bucketize_rate(self):
        for _ in range(self.num_datasets):
            df = self.generate_random_dataset()
            expected_step = round(((df['interest_rate'].max() - df['interest_rate'].min()) / 10), 2)
            result = strattools.bucketize_data(df, 'interest_rate')
            self.assertAlmostEqual(result[1] - result[0], expected_step, places=2)

    def test_bucketize_margin(self):
        for _ in range(self.num_datasets):
            df = self.generate_random_dataset()
            expected_step = round(((df['interest_margin'].max() - df['interest_margin'].min()) / 10), 2)
            result = strattools.bucketize_data(df, 'interest_margin')
            self.assertAlmostEqual(result[1] - result[0], expected_step, places=2)


if __name__ == '__main__':
    unittest.main()

