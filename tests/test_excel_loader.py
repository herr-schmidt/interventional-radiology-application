import datetime
import unittest

from src import excel_loader


class TestExcelLoader(unittest.TestCase):

    def test_loading(self):
        loader = excel_loader.ExcelLoader()
        patients = loader.load_patients("./tests/test_files/test_list.xlsx")

        self.assertEqual(patients[0].name, "Silvia")
        self.assertEqual(patients[0].surname, "Verdi")
        self.assertEqual(patients[0].services, "7253|7724")
        self.assertEqual(patients[0].anesthesia, True)
        self.assertEqual(patients[0].infectious, True)
        self.assertEqual(patients[0].list_insertion_date, datetime.datetime(2022, 10, 15))

        self.assertEqual(patients[1].name, "Mario")
        self.assertEqual(patients[1].surname, "Rossi")
        self.assertEqual(patients[1].services, "4455|6442|8353")
        self.assertEqual(patients[1].anesthesia, True)
        self.assertEqual(patients[1].infectious, False)
        self.assertEqual(patients[1].list_insertion_date, datetime.datetime(2022, 11, 12))

        self.assertEqual(patients[2].name, "Maria")
        self.assertEqual(patients[2].surname, "Arancioni")
        self.assertEqual(patients[2].services, "8553|4035|5534")
        self.assertEqual(patients[2].anesthesia, False)
        self.assertEqual(patients[2].infectious, True)
        self.assertEqual(patients[2].list_insertion_date, datetime.datetime(2022, 9, 6))

        self.assertEqual(patients[3].name, "Marco")
        self.assertEqual(patients[3].surname, "Neri")
        self.assertEqual(patients[3].services, "7724|3324")
        self.assertEqual(patients[3].anesthesia, False)
        self.assertEqual(patients[3].infectious, False)
        self.assertEqual(patients[3].list_insertion_date, datetime.datetime(2022, 10, 14))

    def test_loading_empty_file(self):
        loader = excel_loader.ExcelLoader()

        # first pass the exception, then the callable and after that all of its needed parameters
        self.assertRaises(excel_loader.InvalidRow, loader.load_patients, "./tests/test_files/empty_test_list.xlsx")


if __name__ == '__main__':
    unittest.main()
