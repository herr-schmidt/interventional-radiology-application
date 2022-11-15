import sys
import threading
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from pandastable import Table, config
import math

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

        self.initializeUI()

    def initializeUI(self):
        self.create_upper_menus()
        self.create_notebooks()
        self.create_command_panel()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_command_panel(self):
        self.buttons_frame = Labelframe(master=self.upper_frame, text="", width=math.floor(self.screen_width * 0.2))
        self.buttons_frame.pack(side=RIGHT, expand=True, fill=BOTH, anchor=E)

        self.test_button = Button(master=self.buttons_frame,
                                  width=12,
                                  text="Test")
        self.test_button.pack()

    def open_file_callback(self):
        self.selected_file = filedialog.askopenfile()
        print(self.selected_file.name)

    def create_upper_menus(self):
        menu = Menu(self.master)
        self.master.config(menu=menu)

        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)

        file_menu.add_command(label='Open...', command=self.open_file_callback)

    def create_notebooks(self):
        self.notebook_frame = Labelframe(self.upper_frame)
        self.notebook_frame.pack(side=LEFT, fill=BOTH, anchor=W)

        self.notebook = Notebook(self.notebook_frame, width=math.floor(self.screen_width * 0.8), height=math.floor(self.screen_height * 0.6))
        self.notebook.pack(expand=True, fill=BOTH)

        self.input_tab = Frame(self.notebook)
        self.output_tab = Frame(self.notebook)

        self.input_tab.pack(fill=BOTH, expand=True)
        self.output_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(self.input_tab, text='Lista pazienti')
        self.notebook.add(self.output_tab, text='Pianificazione')

        self.initialize_input_table()

    def initialize_input_table(self):
        self.input_table = Table(parent=self.input_tab, cols=self.input_columns)
        self.input_table.model.df = self.input_table.model.df.rename(columns=self.input_columns_translations)

        options={"cellwidth": 100}
        config.apply_options(options,self.input_table)

        self.input_table.columnwidths["Nome"] = 150
        self.input_table.columnwidths["Prestazioni"] = 450
        self.input_table.columnwidths["Data inserimento in lista"] = 250
        self.input_table.autoResizeColumns()
        self.input_table.redraw()

        self.input_table.show()

    def create_log_text_box(self):
        self.output_frame = Frame(master=self.lower_frame)
        self.output_frame.pack(fill=BOTH)

        self.text_box = ScrolledText(master=self.output_frame, width=500, height=20)
        self.text_box.pack(fill=X)
        self.text_box.config(background="#000000", fg="#ffffff")

        sys.stdout = StdoutRedirector(self.text_box)


ws = Tk()
ws.title("Interventional Radiology Planner & Scheduler")

# Create a style
style = Style(ws)

# Set the theme with the theme_use method
style.theme_use('winnative')  # put the theme name here, that you want to use

gui = GUI(ws)

ws.mainloop()
