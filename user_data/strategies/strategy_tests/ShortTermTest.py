import unittest

import pandas


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        dataframe = pandas.DataFrame(
            columns=['date', 'open', 'high', 'low', 'close', 'volume', 'macdhist', 'ema7', 'ema14'])
        data = {
            
        }
        pandas.concat(dataframe, )
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_entry_signal(self):
        self.assertEqual(True, False)  # add assertion here

    def test_exit_signal(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
