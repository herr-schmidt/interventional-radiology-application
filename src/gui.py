import sys
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from pandastable import Table, config
import tkinter.ttk as ttk
import math
import pandas
import customtkinter as ctk


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert("end", string)
        self.text_space.see("end")

    def flush(self):
        pass


# class ScaleWithLabel(Frame):
# 
#     def __init__(self, master, type, from_, to, value, orient, labelText):
#         super(ScaleWithLabel, self).__init__(master=master)
#         self.labelText = StringVar()
#         self.labelText.set(labelText)
#         self.title_label = Label(master=self, textvariable=self.labelText)
#         self.title_label.pack(side=TOP, anchor=NW, pady=(0, 5))
# 
#         self.variable = None
#         self.type = type
#         if(type == "int"):
#             self.variable = IntVar(value=value)
#         else:
#             self.variable = DoubleVar(value=value)
#         self.slider = Scale(
#             master=self,
#             from_=from_,
#             to=to,
#             resolution=0.05,
#             variable=self.variable,
#             orient=orient,
#             label="ASDASD",
#         )
#         self.slider.pack(side=LEFT)
# 
#         self.value_label = Label(
#             master=self,
#             textvariable=self.variable,
#             width=4,
#             state=DISABLED,
#             anchor=CENTER,
#             relief=SOLID,
#             borderwidth=1
#         )
#         self.value_label.pack(expand=True, side=RIGHT, padx=(10, 0))


class ButtonToolTip:
    def __init__(self, button, text=None):
        self.button = button
        self.text = text

        self.button.bind('<Enter>', self.on_enter)
        self.button.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        self.tooltip = Toplevel()
        self.tooltip.overrideredirect(True)
        self.tooltip.geometry(f'+{self.button.winfo_rootx()+30}+{self.button.winfo_rooty()+30}')

        self.label = Label(self.tooltip,
                           text=self.text,
                           background="#ffffe0",
                           relief=SOLID,
                           borderwidth=1)
        self.label.pack()

    def on_leave(self, event):
        self.tooltip.destroy()


class GUI(object):
    def __init__(self, master):
        self.master = master

        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        # print(self.screen_width)

        # notebooks, command panels and toolbars
        self.upper_frame = Frame(master=self.master, name="upper_frame")
        self.upper_frame.pack(side=TOP, fill=BOTH, expand=True)

        # log output and footer
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
        self.icons = []
        self.tooltips = []

        self.planning_number = 0

        self.initializeUI()

    def initializeUI(self):
        self.create_upper_menus()
        self.create_toolbar()
        self.create_footer()
        self.create_notebook()
        self.create_solver_command_panel()
        self.create_edit_command_panel()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_footer(self):
        footer = Frame(master=self.lower_frame, name="footer_frame", height=30)
        footer.pack(side=BOTTOM, fill=X, expand=True)

    def create_toolbar(self):
        # toolbar
        toolbar_frame = Frame(master=self.upper_frame, name="toolbar_frame")
        toolbar_frame.pack(side=TOP, fill=X, expand=False)

        self.add_toolbar_button(toolbar_frame, 32, 32, "resources/new-document.png", "new_button", self.new_planning_callback, text="Nuova scheda")
        self.add_toolbar_button(toolbar_frame, 32, 32, "resources/open-folder.png", "open_button", self.import_callback, text="Importa...")
        self.add_toolbar_button(toolbar_frame, 32, 32, "resources/close.png", "close_active_tab_button", self.close_active_tab, text="Chiudi scheda attiva", state=DISABLED)

    def add_toolbar_button(self, toolbar_frame, x_subsample, y_subsample, icon_path, button_name, command, text=None, state=NORMAL):
        icon = PhotoImage(file=icon_path).subsample(x_subsample, y_subsample)
        # to avoid garbage collection of a PhotoImage we need to keep a reference to it
        self.icons.append(icon)
        button = Button(master=toolbar_frame,
                        name=button_name,
                        image=icon,
                        command=command,
                        state=state,
                        relief="flat"
                        )
        button.pack(side=LEFT, anchor=W, padx=(5, 0), pady=(5, 5))

        if text:
            self.tooltips.append(ButtonToolTip(button=button, text=text))

    def close_active_tab(self):
        active_tab = self.notebook.nametowidget(self.notebook.select())
        active_tab.destroy()

        if(len(self.upper_frame.nametowidget("notebook_frame.notebook").children) == 0):
            self.upper_frame.nametowidget(
                "toolbar_frame.close_active_tab_button").config(state=DISABLED)

    def create_edit_command_panel(self):
        edit_frame = ttk.Labelframe(master=self.upper_frame, name="edit_frame",
                                text="Edit panel", width=math.floor(self.screen_width * 0.3))
        edit_frame.pack(side=TOP, fill=BOTH, expand=True,
                        padx=(5, 5), pady=(5, 0))

    def create_solver_command_panel(self):
        solver_frame = ttk.Labelframe(
            master=self.upper_frame, text="Solver", width=math.floor(self.screen_width * 0.3))
        solver_frame.pack(side=BOTTOM, fill=BOTH,
                          expand=True, padx=(5, 5), pady=(0, 5))

        gap_variable = DoubleVar(value=0.5)
        gap_slider = Scale(
            master=solver_frame,
            from_=0,
            to=5,
            resolution=0.05,
            variable=gap_variable,
            label="Gap relativo (%)",
            orient=HORIZONTAL,
            length=solver_frame.winfo_width() / 3
        )
        gap_slider.pack(anchor=W)

        # gap_scale = ScaleWithLabel(master=solver_frame,
        #                            type="double",
        #                            from_=0,
        #                            to=5,
        #                            value=1,
        #                            orient="horizontal",
        #                            labelText="Gap relativo (%)")
        # gap_scale.pack(anchor=W, padx=(10, 0))

    def import_callback(self):
        selected_file = filedialog.askopenfile(
            filetypes=[("File Excel", ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab, text="Lista pazienti " +
                          str(self.planning_number))
        self.planning_number += 1

        import_data_frame = pandas.read_excel(selected_file.name)
        self.initialize_input_table(
            input_tab=input_tab, data_frame=import_data_frame)

    def new_planning_callback(self):
        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab, text="Lista pazienti " +
                          str(self.planning_number))
        self.planning_number += 1

        self.initialize_input_table(input_tab=input_tab, data_frame=None)

    def create_upper_menus(self):
        menu = Menu(self.master)
        self.master.config(menu=menu)

        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)

        file_menu.add_command(label="Nuova pianificazione",
                              command=self.new_planning_callback)
        file_menu.add_command(label="Importa...", command=self.import_callback)

    def create_notebook(self):
        self.notebook_frame = Frame(self.upper_frame, name="notebook_frame", width=math.floor(
            self.screen_width * 0.8), height=math.floor(self.screen_height * 0.5))
        self.notebook_frame.pack(side=LEFT, fill=BOTH,
                                 anchor=W, padx=(5, 0), pady=(5, 5))
        # avoid frame from expanding when the inner widget expands
        self.notebook_frame.pack_propagate(False)

        self.notebook = ttk.Notebook(self.notebook_frame, name="notebook")
        self.notebook.pack(expand=True, fill=BOTH)

    def initialize_input_table(self, input_tab, data_frame):
        input_table = Table(
            parent=input_tab, cols=self.input_columns, dataframe=data_frame)

        input_table.model.df = input_table.model.df.rename(
            columns=self.input_columns_translations)

        options = {'align': 'w',
                   'cellwidth': 150,
                   'floatprecision': 2,
                   'font': 'Microsoft Tai Le',
                   'fontsize': 10,
                   'rowheight': 20,
                   'colselectedcolor': "#c7deff",
                   'rowselectedcolor': "#c7deff",
                   'textcolor': 'black'
                   }
        config.apply_options(options, input_table)

        input_table.show()

        input_table.columnwidths["Prestazioni"] = 450
        input_table.columnwidths["Data inserimento in lista"] = 250

        input_table.colheader.bgcolor = "#e8e8e8"
        input_table.rowheader.bgcolor = "#e8e8e8"
        input_table.rowindexheader.bgcolor = "#e8e8e8"

        input_table.colheader.colselectedcolor = "#5e9cff"
        input_table.rowheader.rowselectedcolor = "#5e9cff"

        input_table.colheader.textcolor = "black"
        input_table.rowheader.textcolor = "black"

        input_table.redraw()  # for avoiding the strange behavior of empty first imported table

        self.upper_frame.nametowidget(
            "toolbar_frame.close_active_tab_button").config(state=ACTIVE)

    def create_log_text_box(self):
        # self.output_frame = Frame(master=self.lower_frame)
        # self.output_frame.pack(fill=BOTH, expand=True)

        self.text_box = ScrolledText(master=self.lower_frame)
        self.text_box.pack(side=TOP, fill=BOTH, expand=True)
        self.text_box.config(background="#000000", fg="#ffffff")

        sys.stdout = StdoutRedirector(self.text_box)


root = ctk.CTk()
root.title("Interventional Radiology Planner & Scheduler")
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),
              root.winfo_screenheight()))
root.state("zoomed")

# Create a style
#style = ttk.Style(root)

# Set the theme with the theme_use method
#style.theme_use('winnative')  # put the theme name here, that you want to use

gui = GUI(root)

root.mainloop()
