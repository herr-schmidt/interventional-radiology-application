import pandas as pd


class Controller():

    DEFAULT_TAB_NAME = "Lista pazienti "

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.planning_number = 0

    def export_sheet(self, data_frame: pd.DataFrame, file_name):
        data_frame.to_excel(file_name,
                            header=list(data_frame.columns),
                            index=False  # avoid writing a column of indices
                            )

    def import_sheet(self, selected_file):
        tab_name = self.get_tab_name()

        import_data_frame = pd.read_excel(selected_file.name)
        self.view.initialize_input_table(tab_name=tab_name,
                                         data_frame=import_data_frame)

    def create_empty_planning(self):
        tab_name = self.get_tab_name()

        self.view.initialize_input_table(tab_name=tab_name,
                                         data_frame=None)

    def get_tab_name(self):
        tab_name = self.DEFAULT_TAB_NAME + str(self.planning_number)
        self.planning_number += 1
        return tab_name
