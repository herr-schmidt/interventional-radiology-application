import datetime
import unittest

from src import excel_loader


class TestExcelLoader(unittest.TestCase):

    def check_loading(self):
        loader = excel_loader.ExcelLoader()
        patients = loader.load_patients("./test_list.xlsx")

        self.assertEqual(patients[0].name, "Silvia")
        self.assertEqual(patients[0].surname, "Verdi")
        self.assertEqual(patients[0].services, "7253|7724")
        self.assertEqual(patients[0].anesthesia, True)
        self.assertEqual(patients[0].infectious, False)
        self.assertEqual(patients[0].list_insertion_date, datetime.datetime(2022, 10, 15))


if __name__ == '__main__':
    unittest.main()
