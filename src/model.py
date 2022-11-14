import datetime

class Patient:

    def __init__(self, name, surname, services, anesthesia, infectious, list_insertion_date):
        self.name = name
        self.surname =surname
        self.services = services
        self.anesthesia = anesthesia
        self.infectious = infectious
        self.list_insertion_date = list_insertion_date

        