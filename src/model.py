import datetime

class Patient:

    def __init__(self, name: str, surname: str, services: list[str], anesthesia: bool, infectious: bool, list_insertion_date: datetime):
        self.name = name
        self.surname =surname
        self.services = services
        self.anesthesia = anesthesia
        self.infectious = infectious
        self.list_insertion_date = list_insertion_date

        