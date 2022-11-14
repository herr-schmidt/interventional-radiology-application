import unittest
import datetime
from excel_loader import ExcelLoader

class TestExcelLoader(unittest.TestCase):

    def check_loading(self):
        excel_loader = ExcelLoader()
        patients = excel_loader.load_patients("./test_list.xlsx")

        self.assertEqual(patients[0].name, "Silvia")
        self.assertEqual(patients[0].surname, "Verdi")
        self.assertEqual(patients[0].services, "7253|7724")
        self.assertEqual(patients[0].anesthesia, True)
        self.assertEqual(patients[0].infectious, False)
        self.assertEqual(patients[0].list_insertion_date, datetime.datetime(2022, 10, 15))