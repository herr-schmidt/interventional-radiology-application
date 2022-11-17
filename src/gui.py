import sys
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from pandastable import Table, config
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


class ScaleWithEntry(Frame):

    def round_value(self, value):
        if(self.type == "int"):
            self.variable.set(round(float(value)))
        else:
            self.variable.set(round(float(value), 1))

    def __init__(self, master, type, from_, to, value, orient, labelText):
        super(ScaleWithEntry, self).__init__(master=master)
        self.labelText = StringVar()
        self.labelText.set(labelText)
        self.label = Label(master=self, textvariable=self.labelText)
        self.label.pack(side=TOP, anchor=NW)

        self.variable = None
        self.type = type
        if(type == "int"):
            self.variable = IntVar(value=value)
        else:
            self.variable = DoubleVar(value=value)
        self.slider = Scale(
            master=self,
            from_=from_,
            to=to,
            variable=self.variable,
            # resolution=0.1,
            orient=orient,
            # label=label,
            command=self.round_value
        )
        self.slider.pack(side=LEFT)

        self.entry = Entry(
            master=self,
            textvariable=self.variable,
            width=4,
            state=DISABLED,
            justify=CENTER
        )
        self.entry.pack(expand=True, side=RIGHT)


class GUI(object):
    def __init__(self, master):
        self.master = master

        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        print(self.screen_width)

        # notebooks and command panel
        self.upper_frame = Frame(master=self.master, name="upper_frame")
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
        self.create_solver_command_panel()
        self.create_edit_command_panel()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def close_active_tab(self):
        active_tab = self.notebook.nametowidget(self.notebook.select())
        active_tab.destroy()

        if(len(self.upper_frame.nametowidget("notebook_frame.notebook").children) == 0):
            self.upper_frame.nametowidget("edit_frame.close_active_tab_button").config(state=DISABLED)

    def create_edit_command_panel(self):
        edit_frame = Labelframe(master=self.upper_frame, name="edit_frame", text="Edit panel", width=math.floor(self.screen_width * 0.3))
        edit_frame.pack(side=TOP, fill=BOTH, expand=True, padx=(5, 5), pady=(5, 0))

        close_active_tab_button = Button(master=edit_frame,
                                  name="close_active_tab_button",
                                  state=DISABLED,
                                  text="Chiudi scheda attiva",
                                  command=self.close_active_tab)
        close_active_tab_button.pack(anchor=W, padx=(5, 0))

    def create_solver_command_panel(self):
        solver_frame = Labelframe(master=self.upper_frame, text="Solver", width=math.floor(self.screen_width * 0.3))
        solver_frame.pack(side=BOTTOM, fill=BOTH, expand=True, padx=(5, 5), pady=(0, 5))

        gap_scale = ScaleWithEntry(master=solver_frame,
                                       type="double",
                                       from_=0,
                                       to=5,
                                       value=1,
                                       orient="horizontal",
                                       labelText="Gap relativo (%)")
        gap_scale.pack(anchor=W, padx=(10, 0))

    def import_callback(self):
        selected_file = filedialog.askopenfile(filetypes=[("File Excel", ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab, text="Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        import_data_frame = pandas.read_excel(selected_file.name)
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

        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)

        file_menu.add_command(label="Nuova pianificazione", command=self.new_planning_callback)
        file_menu.add_command(label="Importa...", command=self.import_callback)

    def create_notebook(self):
        self.notebook_frame = Frame(self.upper_frame, name="notebook_frame")
        self.notebook_frame.pack(side=LEFT, fill=BOTH, anchor=W, padx=(5, 0), pady=(5, 5))

        self.notebook = Notebook(self.notebook_frame, name="notebook", width=math.floor(self.screen_width * 0.8), height=math.floor(self.screen_height * 0.55))
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

        self.upper_frame.nametowidget("edit_frame.close_active_tab_button").config(state=ACTIVE)

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
