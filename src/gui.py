import sys
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
# from pandastable import Table, config
import tkinter.ttk as ttk
import math
import pandas
import customtkinter as ctk
from bootstraptable import Table, FitCriterion
import tktooltip
import pandas as pd


class StdoutRedirector(object):

    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert("end", string)
        self.text_space.see("end")

    def flush(self):
        pass


class EntryWithLabel(ctk.CTkFrame):

    def __init__(self, master, label_text, entry_width=200, label_width=10):
        super(EntryWithLabel, self).__init__(master=master, width=200, fg_color="#ffffff")

        self.entry_variable = StringVar()
        self.entry = ctk.CTkEntry(master=self, textvariable=self.entry_variable, width=entry_width, border_width=1, border_color="gray90")

        self.label = ctk.CTkLabel(master=self, text=label_text, width=label_width, anchor=W, fg_color="#ffffff", text_font=("Microsoft Tai Le", 10))

        self.label.pack(side=TOP, anchor=W)
        self.entry.pack(side=LEFT)
        

class InsertionDialog():

    def __init__(self):
        self.dialog = ctk.CTkToplevel(fg_color="#ffffff")

        dialog_frame = ctk.CTkFrame(master=self.dialog, width=100, height=100, fg_color="#ffffff")

        registry_label = ctk.CTkLabel(master=dialog_frame, text="Anagrafica", text_font=("Microsoft Tai Le", 12), width=10)
        name_entry = EntryWithLabel(dialog_frame, "Nome")
        surname_entry = EntryWithLabel(dialog_frame, "Cognome")

        planning_label = ctk.CTkLabel(master=dialog_frame, text="Pianificazione", text_font=("Microsoft Tai Le", 12), width=14)
        waiting_list_date_entry = EntryWithLabel(dialog_frame, "Inserimento in lista d'attesa", label_width=24)

        anesthesia = BooleanVar(False)
        infections = BooleanVar(False)

        anesthesia_checkbox = ctk.CTkCheckBox(master=dialog_frame, variable=anesthesia, border_color="gray90", border_width=1, hover=False, text="Anestesia", text_font=("Microsoft Tai Le", 10), checkmark_color="#ffffff", fg_color="#287cfa")
        infections_checkbox = ctk.CTkCheckBox(master=dialog_frame, variable=infections, border_color="gray90", border_width=1, hover=False, text="Infezioni in atto", text_font=("Microsoft Tai Le", 10), checkmark_color="#ffffff", fg_color="#287cfa")

        dialog_frame.pack()

        registry_label.pack(side=TOP, anchor=W, padx=(20, 0))
        name_entry.pack(side=TOP, anchor=W, padx=(20, 20), pady=(5, 5))
        surname_entry.pack(side=TOP, anchor=W, padx=(20, 20), pady=(0, 20))

        planning_label.pack(side=TOP, anchor=W, padx=(20, 0))
        waiting_list_date_entry.pack(side=TOP, anchor=W, padx=(20, 20), pady=(5, 5))
        anesthesia_checkbox.pack(side=TOP, anchor=W, padx=(20, 20), pady=(5, 5))
        infections_checkbox.pack(side=TOP, anchor=W, padx=(20, 20), pady=(0, 20))


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
        self.upper_frame = ctk.CTkFrame(master=self.master, name="upper_frame", fg_color="#F2F2F2")
        self.upper_frame.pack(side=TOP, fill=BOTH, expand=True)

        # log output and footer
        self.lower_frame = ctk.CTkFrame(master=self.master, name="lower_frame", fg_color="#F2F2F2")
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
        # self.create_upper_menus()
        self.create_toolbar()
        self.create_notebook()
        self.create_solver_command_panel()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_toolbar(self):
        # toolbar
        toolbar_frame = ctk.CTkFrame(master=self.upper_frame, name="toolbar_frame", fg_color="#E3E4E5")
        toolbar_frame.pack(side=LEFT, fill=Y, expand=False, padx=(10, 10), pady=(10, 10))

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
            "resources/xlsx-file-format-extension.png",
            "open_button",
            self.import_callback,
            text="Importa...",
        )
        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/floppy-disk.png",
            "save_button",
            self.export_callback,
            text="Salva",
        )
        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/bin.png",
            "close_active_tab_button",
            self.close_active_tab,
            text="Chiudi scheda attiva",
            state=DISABLED,
        )

        separator = ttk.Separator(master=toolbar_frame, orient="horizontal")
        separator.pack(side=TOP, padx=(5, 5), pady=(5, 5), fill=X)

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/add-user.png",
            self.ADD_PATIENT_BUTTON,
            self.add_patient,
            text="Aggiungi paziente",
            state=NORMAL,
        )

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/editing.png",
            self.EDIT_PATIENT_BUTTON,
            self.edit_patient,
            text="Modifica paziente",
            state=NORMAL,
        )

        separator = ttk.Separator(master=toolbar_frame, orient="horizontal")
        separator.pack(side=TOP, padx=(5, 5), pady=(5, 5), fill=X)

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/play-button.png",
            "play_button",
            self.launch_solver,
            text="Calcola pianificazione",
            state=NORMAL,
        )

        self.add_toolbar_button(
            toolbar_frame,
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/stop-button.png",
            "stop_button",
            self.stop_solver,
            text="Interrompi pianificazione",
            state=NORMAL,
        )
    
    def launch_solver(self):
        pass

    def stop_solver(self):
        pass

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
        
        # to avoid garbage collection of a PhotoImage we need to keep a reference to it
        self.icons.append(icon)
        button = ctk.CTkButton(
            master=toolbar_frame,
            name=button_name,
            image=icon,
            command=command,
            state=state,
            relief="flat",
            fg_color="#E3E4E5",
            # border_width=1,
            # border_color="gray90",
            hover_color="#D7D8D9",
            text="",
            text_color="#ffffff",
            text_font=("Microsoft Tai Le Bold", 11),
            width=icon.width() + 10,
            height=icon.height() + 10
        )
        button.pack(side=TOP, anchor=CENTER, expand=False, padx=(5, 5), pady=(5, 5))

        tktooltip.ToolTip(widget=button, msg=text, fg="#000000", bg="#ffffff")


    def add_patient(self):
        dialog = InsertionDialog()

    def edit_patient(self):
        dialog = InsertionDialog()

    def close_active_tab(self):
        active_tab = self.notebook.nametowidget(self.notebook.select())
        active_tab.destroy()

        if len(
                self.upper_frame.nametowidget(
                    "notebook_frame.notebook").children) == 0:
            close_active_tab_button = self.upper_frame.nametowidget("toolbar_frame.close_active_tab_button")
            close_active_tab_button.state = DISABLED

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
        solver_frame = ctk.CTkFrame(
            master=self.upper_frame,
            # text="Solver",
            width=math.floor(self.screen_width * 0.3),
            fg_color="#E3E4E5"
        )
        solver_frame.pack(side=BOTTOM,
                          fill=BOTH,
                          expand=True,
                          padx=(10, 10),
                          pady=(10, 10))

        # needed for getting a proper value when calling winfo_width()
        self.master.update_idletasks()

        gap_variable = DoubleVar(value=0.5)
        gap_slider = ctk.CTkSlider(
            master=solver_frame,
            from_=0,
            to=5,
            # resolution=0.05,
            variable=gap_variable,
            # label="Gap relativo (%)",
            orient=HORIZONTAL,
            # length=solver_frame.winfo_width() / 2,
            number_of_steps=5/0.5,
            progress_color="#287cfa",
            button_color="#287cfa",
            fg_color="gray90",
            button_hover_color="#1d60c4"
        )
        gap_slider.pack(side=TOP, anchor=W, padx=(10, 10), pady=(10, 0))

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
        self.initialize_input_table(input_tab=input_tab, data_frame=import_data_frame)

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

        table.data_frame.to_excel(file_name,
                                header=list(table.data_frame.columns),
                                index=False # avoid writing a column of indices
                                )

    def new_planning_callback(self):
        input_tab = ctk.CTkFrame(self.notebook)
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
        self.notebook_frame = ctk.CTkFrame(
            self.upper_frame,
            name="notebook_frame",
            width=math.floor(self.screen_width * 0.65),
            height=math.floor(self.screen_height * 0.5),
            fg_color="#E3E4E5"
        )
        self.notebook_frame.pack(side=LEFT,
                                 # fill=BOTH,
                                 # anchor=W,
                                 padx=(0, 0),
                                 pady=(10, 10))
        # avoid frame from expanding when the inner widget expands
        self.notebook_frame.pack_propagate(False)

        self.notebook = ttk.Notebook(self.notebook_frame, name="notebook")
        self.notebook.pack(expand=True, fill=BOTH, padx=(30, 30), pady=(30, 30))

    def initialize_input_table(self, input_tab, data_frame):
        table = Table(master=input_tab,
                data_frame=data_frame,
                row_height=30,
                header_height=40,
                fit_criterion=FitCriterion.DEFAULT,
                row_separator_width=1)
        table.pack()

        close_active_tab_button = self.upper_frame.nametowidget("toolbar_frame.close_active_tab_button")
        close_active_tab_button.state = NORMAL

    def create_log_text_box(self):
        # self.output_frame = Frame(master=self.lower_frame)
        # self.output_frame.pack(fill=BOTH, expand=True)

        self.text_box = ScrolledText(master=self.lower_frame)
        self.text_box.pack(side=TOP, fill=BOTH, expand=False, padx=(30, 30), pady=(30, 30))
        self.text_box.config(background="#ffffff", fg="#000000", font=("Roboto", 10))

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
