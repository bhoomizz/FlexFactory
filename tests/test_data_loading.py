
import unittest
from unittest.mock import patch

from src.baseline import read_csv


class TestDataLoading(unittest.TestCase):

    def test_missing_csv_file_raises_error(self):
        with patch("builtins.open", side_effect=FileNotFoundError("missing.csv")):
            with self.assertRaises(FileNotFoundError):
                read_csv("missing.csv")


if __name__ == "__main__":
    unittest.main()
