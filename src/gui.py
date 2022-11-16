import sys
import threading
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from pandastable import Table, config, TableModel
import math
import pandas

from click import command


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert("end", string)
        self.text_space.see("end")

    def flush(self):
        pass


class GUI(object):
    def __init__(self, master):
        self.master = master

        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        print(self.screen_width)

        # notebooks and command panel
        self.upper_frame = Frame(master=self.master)
        self.upper_frame.pack(side=TOP, fill=BOTH, expand=True)

        # log output
        self.lower_frame = Frame(master=self.master)
        self.lower_frame.pack(side=BOTTOM, fill=BOTH, expand=True)

        self.input_columns = 6
        self.input_columns_translations = {"a": "Nome",
                                           "b": "Cognome",
                                           "c": "Prestazioni",
                                           "d": "Anestesia",
                                           "e": "Infezioni",
                                           "f": "Data inserimento in lista",
                                          }
        self.output_columns = 10

        self.planning_number = 0

        self.initializeUI()

    def initializeUI(self):
        self.create_upper_menus()
        self.create_notebook()
        self.create_command_panel()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_command_panel(self):
        self.buttons_frame = Labelframe(master=self.upper_frame, text="", width=math.floor(self.screen_width * 0.3))
        self.buttons_frame.pack(side=TOP, fill=Y, expand=True)

        self.test_button = Button(master=self.buttons_frame,
                                  width=12,
                                  text="Test")
        self.test_button.pack()

    def import_callback(self):
        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab, text="Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        self.selected_file = filedialog.askopenfile()
        print(self.selected_file.name)

        import_data_frame = pandas.read_excel(self.selected_file.name)
        self.initialize_input_table(input_tab=input_tab, data_frame=import_data_frame)
        

    def new_planning_callback(self):
        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab, text="Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        self.initialize_input_table(input_tab=input_tab, data_frame=None)


    def create_upper_menus(self):
        menu = Menu(self.master)
        self.master.config(menu=menu)

        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)

        file_menu.add_command(label="Nuova pianificazione", command=self.new_planning_callback)
        file_menu.add_command(label="Importa...", command=self.import_callback)

    def create_notebook(self):
        self.notebook_frame = Frame(self.upper_frame)
        self.notebook_frame.pack(side=LEFT, fill=BOTH, anchor=W)

        self.notebook = Notebook(self.notebook_frame, width=math.floor(self.screen_width * 0.8), height=math.floor(self.screen_height * 0.55))
        self.notebook.pack(expand=True, fill=BOTH)

    def initialize_input_table(self, input_tab, data_frame):
        input_table = Table(parent=input_tab, cols=self.input_columns, dataframe=data_frame)
        
        input_table.model.df = input_table.model.df.rename(columns=self.input_columns_translations)

        options={"cellwidth": 100}
        config.apply_options(options,input_table)

        input_table.columnwidths["Nome"] = 150
        input_table.columnwidths["Cognome"] = 150
        input_table.columnwidths["Prestazioni"] = 450
        input_table.columnwidths["Data inserimento in lista"] = 250

        input_table.show()
        input_table.redraw() # for avoiding the strange behavior of empty first imported table

    def create_log_text_box(self):
        self.output_frame = Frame(master=self.lower_frame)
        self.output_frame.pack(fill=BOTH)

        self.text_box = ScrolledText(master=self.output_frame, width=500, height=16)
        self.text_box.pack(fill=X)
        self.text_box.config(background="#000000", fg="#ffffff")

        sys.stdout = StdoutRedirector(self.text_box)


root = Tk()
root.title("Interventional Radiology Planner & Scheduler")
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.state("zoomed")

# Create a style
style = Style(root)

# Set the theme with the theme_use method
style.theme_use('winnative')  # put the theme name here, that you want to use

gui = GUI(root)

root.mainloop()
