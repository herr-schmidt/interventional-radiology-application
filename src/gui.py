import sys
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from pandastable import Table, config, ToolTip
import tkinter.ttk as ttk
import math
import pandas
import customtkinter as ctk
import numpy as np


class StdoutRedirector(object):

    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert("end", string)
        self.text_space.see("end")

    def flush(self):
        pass


class EntryWithLabel(Frame):

    def __init__(self, master, label_text, entry_width=20, label_width=10):
        super(EntryWithLabel, self).__init__(master=master, width=200)

        self.entry_variable = StringVar()
        self.entry = Entry(master=self, textvariable=self.entry_variable, width=entry_width)

        self.label = Label(master=self, text=label_text, width=label_width, anchor=W)

        self.label.pack(side=LEFT)
        self.entry.pack(side=LEFT)


class CheckboxWithLabel(Frame):

    def __init__(self, master, label_text):
        super(CheckboxWithLabel, self).__init__(master=master)

        self.entry_variable = BooleanVar()
        self.checkbox = Checkbutton(master=self, variable=self.entry_variable)

        self.label = Label(master=self, text=label_text)

        self.checkbox.pack(side=LEFT, anchor=W)
        self.label.pack(side=LEFT, anchor=W)
        

class InsertionDialog():

    def __init__(self, button):
        self.button = button

        self.button.bind("<Button-1>", self.handle_left_click)

    def handle_left_click(self, event):
        self.dialog = Toplevel()

        dialog_frame = Frame(master=self.dialog, width=100, height=100)

        registry_frame = LabelFrame(master=dialog_frame, text="Anagrafica")
        name_entry = EntryWithLabel(registry_frame, "Nome")
        surname_entry = EntryWithLabel(registry_frame, "Cognome")

        planning_frame = LabelFrame(master=dialog_frame, text="Pianificazione")
        waiting_list_date_entry = EntryWithLabel(planning_frame, "Inserimento in lista d'attesa", label_width=24)
        anesthesia_checkbox = CheckboxWithLabel(planning_frame, "Anestesia")
        infections_checkbox = CheckboxWithLabel(planning_frame, "Infezioni in atto")

        dialog_frame.pack()
        registry_frame.pack(side=TOP, padx=(10, 10), pady=(10, 5), expand=True, fill=X)
        planning_frame.pack(side=BOTTOM, padx=(10, 10), pady=(5, 10), expand=True, fill=X)

        name_entry.pack(side=TOP, anchor=W, padx=(5, 5), pady=(5, 5))
        surname_entry.pack(side=TOP, anchor=W, padx=(5, 5), pady=(0, 5))
        waiting_list_date_entry.pack(side=TOP, anchor=W, padx=(5, 5), pady=(5, 5))
        anesthesia_checkbox.pack(side=TOP, anchor=W, padx=(5, 5), pady=(0, 5))
        infections_checkbox.pack(side=TOP, anchor=W, padx=(5, 5), pady=(0, 5))



class GUI(object):

    # constants
    EXCEL_FILE = "File Excel"
    ODF_FILE = "ODF Spreadsheet (.odf)"

    ADD_PATIENT_BUTTON = "add_patient_button"
    EDIT_PATIENT_BUTTON = "edit_patient_button"

    BUTTON_COLOR = "gray90"
    BUTTON_HOVER_COLOR = "#e7f1ff"
    BUTTON_FRAME_BORDER_COLOR = "gray70"
    BUTTON_FRAME_BORDER_HOVER_COLOR = "#5fa2ff"

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
        self.input_columns_translations = {
            "a": "Nome",
            "b": "Cognome",
            "c": "Prestazioni",
            "d": "Anestesia",
            "e": "Infezioni",
            "f": "Data inserimento in lista",
        }
        self.icons = []
        self.tooltips = []
        self.dialogs = []

        self.planning_number = 0

        self.initializeUI()

    def initializeUI(self):
        self.create_upper_menus()
        self.create_toolbar()
        self.create_footer()
        self.create_notebook()
        self.create_solver_command_panel()
        # self.create_edit_command_panel()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_footer(self):
        footer = Frame(master=self.lower_frame, name="footer_frame", height=30)
        footer.pack(side=BOTTOM, fill=X, expand=True)

    def create_toolbar(self):
        # toolbar
        toolbar_frame = Frame(master=self.upper_frame, name="toolbar_frame")
        toolbar_frame.pack(side=TOP, fill=X, expand=False)

        toolbar_icon_sampling_X = 20
        toolbar_icon_sampling_Y = 20

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/new-document.png",
            "new_button",
            self.new_planning_callback,
            text="Nuova scheda",
        )
        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/open-folder.png",
            "open_button",
            self.import_callback,
            text="Importa...",
        )
        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/diskette.png",
            "save_button",
            self.export_callback,
            text="Salva",
        )
        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/close.png",
            "close_active_tab_button",
            self.close_active_tab,
            text="Chiudi scheda attiva",
            state=DISABLED,
        )

        separator = ttk.Separator(master=toolbar_frame, orient="vertical")
        separator.pack(side=LEFT, anchor=W, padx=(5, 0), pady=(5, 5), fill=Y)

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/add-patient.png",
            self.ADD_PATIENT_BUTTON,
            self.add_patient,
            text="Aggiungi paziente",
            state=NORMAL,
        )

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/pencil.png",
            self.EDIT_PATIENT_BUTTON,
            self.edit_patient,
            text="Modifica paziente",
            state=NORMAL,
        )

    def add_toolbar_button(
        self,
        toolbar_frame,
        x_subsample,
        y_subsample,
        icon_path,
        button_name,
        command,
        text=None,
        state=NORMAL,
    ):
        icon = PhotoImage(file=icon_path)

        button_frame = Frame(toolbar_frame, highlightbackground="gray70", highlightthickness=1, name=button_name+"_frame",
        height=16, width=16)
        button_frame.pack(side=LEFT, anchor=W, padx=(5, 0), pady=(5, 5))
        
        # to avoid garbage collection of a PhotoImage we need to keep a reference to it
        self.icons.append(icon)
        button = Button(
            master=button_frame,
            name=button_name,
            image=icon,
            command=command,
            state=state,
            relief="flat",
            background=self.BUTTON_COLOR
        )
        button.pack(expand=True, fill=BOTH)

        if text:
            self.tooltips.append(ToolTip.createToolTip(button, text))

        if button_name in [self.ADD_PATIENT_BUTTON,self.EDIT_PATIENT_BUTTON]:
            self.dialogs.append(InsertionDialog(button=button))

        # ToolTip.createToolTip already binds a widget to an enter/leave event, so we use
        # add="+" for binding multiple functions to the same event.
        button.bind("<Enter>", self.repaint_on_enter, add="+")
        button.bind("<Leave>", self.repaint_on_leave, add="+")

    def repaint_on_enter(self, event):
        button = event.widget
        button_frame = button.master
        if button.cget("state") in [ACTIVE, NORMAL]:
            button.configure(bg=self.BUTTON_HOVER_COLOR)
            button_frame.configure(highlightbackground=self.BUTTON_FRAME_BORDER_HOVER_COLOR)

    def repaint_on_leave(self, event):
        button = event.widget
        button_frame = button.master

        button.configure(bg=self.BUTTON_COLOR)
        button_frame.configure(highlightbackground=self.BUTTON_FRAME_BORDER_COLOR)

    def add_patient(self):
        pass

    def edit_patient(self):
        pass

    def close_active_tab(self):
        active_tab = self.notebook.nametowidget(self.notebook.select())
        active_tab.destroy()

        if len(
                self.upper_frame.nametowidget(
                    "notebook_frame.notebook").children) == 0:
            self.upper_frame.nametowidget(
                "toolbar_frame.close_active_tab_button_frame.close_active_tab_button").config(state=DISABLED)

    def create_edit_command_panel(self):
        edit_frame = ttk.Labelframe(
            master=self.upper_frame,
            name="edit_frame",
            text="Edit panel",
            width=math.floor(self.screen_width * 0.3),
        )
        edit_frame.pack(side=TOP,
                        fill=BOTH,
                        expand=True,
                        padx=(5, 5),
                        pady=(5, 0))

    def create_solver_command_panel(self):
        solver_frame = ttk.Labelframe(
            master=self.upper_frame,
            text="Solver",
            width=math.floor(self.screen_width * 0.3)
        )
        solver_frame.pack(side=BOTTOM,
                          fill=BOTH,
                          expand=True,
                          padx=(5, 5),
                          pady=(0, 5))

        # needed for getting a proper value when calling winfo_width()
        self.master.update_idletasks()

        gap_variable = DoubleVar(value=0.5)
        gap_slider = Scale(
            master=solver_frame,
            from_=0,
            to=5,
            resolution=0.05,
            variable=gap_variable,
            label="Gap relativo (%)",
            orient=HORIZONTAL,
            length=solver_frame.winfo_width() / 2,
        )
        gap_slider.pack(anchor=W)

        solve_button = Button(
            master=solver_frame,
            text="Calcola pianificazione",
            name="solve_button",
            command=self.solve,
            state=DISABLED
        )
        solve_button.pack(side=BOTTOM, anchor=E, padx=(0, 5), pady=(0, 5))

    def solve(self):
        pass

    def import_callback(self):
        selected_file = filedialog.askopenfile(
            filetypes=[(self.EXCEL_FILE,
                        ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab,
                          text="Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        import_data_frame = pandas.read_excel(selected_file.name)
        self.initialize_input_table(input_tab=input_tab,
                                    data_frame=import_data_frame)

    def export_callback(self):
        selected_filetype = StringVar()
        file_name = filedialog.asksaveasfilename(filetypes=[(self.EXCEL_FILE,
                        ["*.xlsx"]), (self.ODF_FILE, "*.odf*")],typevariable=selected_filetype)
        if selected_filetype.get() == self.EXCEL_FILE:
            extension = ".xlsx"
        elif selected_filetype.get() == self.ODF_FILE:
            extension = ".odf"
        else:
            raise Exception("...")

        file_name += str(extension)
        
        tabs = self.notebook.tabs()
        current_tab_id = self.notebook.index(self.notebook.select())

        selected_tab = self.notebook.nametowidget(tabs[current_tab_id])
        for w in selected_tab.winfo_children():
            if isinstance(w, Table):
                table = w
                break

        table.model.df.to_excel(file_name,
                                header=list(table.model.df.columns),
                                index=False # avoid writing a column of indices
                                )

    def new_planning_callback(self):
        input_tab = Frame(self.notebook)
        input_tab.pack(fill=BOTH, expand=True)

        self.notebook.add(input_tab,
                          text="Lista pazienti " + str(self.planning_number))
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
        self.notebook_frame = Frame(
            self.upper_frame,
            name="notebook_frame",
            width=math.floor(self.screen_width * 0.8),
            height=math.floor(self.screen_height * 0.5),
        )
        self.notebook_frame.pack(side=LEFT,
                                 fill=BOTH,
                                 anchor=W,
                                 padx=(5, 0),
                                 pady=(5, 5))
        # avoid frame from expanding when the inner widget expands
        self.notebook_frame.pack_propagate(False)

        self.notebook = ttk.Notebook(self.notebook_frame, name="notebook")
        self.notebook.pack(expand=True, fill=BOTH)

    def initialize_input_table(self, input_tab, data_frame):
        input_table = Table(parent=input_tab,
                            cols=self.input_columns,
                            rows=1,
                            dataframe=data_frame,
                            enable_menus=False,
                            editable=False,
                            showstatusbar=True)

        input_table.model.df = input_table.model.df.rename(
            columns=self.input_columns_translations)

        options = {
            "align": "w",
            "cellwidth": 150,
            "floatprecision": 2,
            "font": "Microsoft Tai Le",
            "fontsize": 10,
            "rowheight": 20,
            "colselectedcolor": "#c7deff",
            "rowselectedcolor": "#c7deff",
            "textcolor": "black",
            "statusbar_font": ("Microsoft Tai Le", 10),
            "statusbar_font_color": "#000000",
        }
        config.apply_options(options, input_table)

        input_table.show()

        input_table.columnwidths["Prestazioni"] = 600
        input_table.columnwidths["Data inserimento in lista"] = 300

        input_table.colheader.bgcolor = "#e8e8e8"
        input_table.rowheader.bgcolor = "#e8e8e8"
        input_table.rowindexheader.bgcolor = "#e8e8e8"

        input_table.colheader.colselectedcolor = "#5e9cff"
        input_table.rowheader.rowselectedcolor = "#5e9cff"

        input_table.colheader.textcolor = "black"
        input_table.rowheader.textcolor = "black"

        input_table.statusbar.sfont = ("Microsoft Tai Le", 10)
        input_table.statusbar.clr = "#000000"

        # for avoiding the strange behavior of empty first imported table
        input_table.redraw()

        self.upper_frame.nametowidget(
            "toolbar_frame.close_active_tab_button_frame.close_active_tab_button").config(state=NORMAL)

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
# style = ttk.Style(root)

# Set the theme with the theme_use method
# style.theme_use('winnative')  # put the theme name here, that you want to use

gui = GUI(root)

root.mainloop()
