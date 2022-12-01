import sys
import tkinter as tk
from PIL import Image
from tkinter import filedialog
import tkinter.ttk as ttk
import math
import pandas
import customtkinter as ctk
from bootstraptable import Table, FitCriterion
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

        self.entry_variable = tk.StringVar()
        self.entry = ctk.CTkEntry(master=self, textvariable=self.entry_variable, width=entry_width, border_width=1, border_color="gray90")

        self.label = ctk.CTkLabel(master=self, text=label_text, width=label_width, anchor=tk.W, fg_color="#ffffff", font=("Microsoft Tai Le", 10))

        self.label.pack(side=tk.TOP, anchor=tk.W)
        self.entry.pack(side=tk.LEFT)
        

class InsertionDialog():

    def __init__(self):
        self.dialog = ctk.CTkToplevel(fg_color="#ffffff")

        dialog_frame = ctk.CTkFrame(master=self.dialog, width=100, height=100, fg_color="#ffffff")

        registry_label = ctk.CTkLabel(master=dialog_frame, text="Anagrafica", font=("Microsoft Tai Le", 12), width=10)
        name_entry = EntryWithLabel(dialog_frame, "Nome")
        surname_entry = EntryWithLabel(dialog_frame, "Cognome")

        planning_label = ctk.CTkLabel(master=dialog_frame, text="Pianificazione", font=("Microsoft Tai Le", 12), width=14)
        waiting_list_date_entry = EntryWithLabel(dialog_frame, "Inserimento in lista d'attesa", label_width=24)

        anesthesia = tk.BooleanVar(False)
        infections = tk.BooleanVar(False)

        anesthesia_checkbox = ctk.CTkCheckBox(master=dialog_frame, variable=anesthesia, border_color="gray90", border_width=1, hover=False, text="Anestesia", font=("Microsoft Tai Le", 10), checkmark_color="#ffffff", fg_color="#287cfa")
        infections_checkbox = ctk.CTkCheckBox(master=dialog_frame, variable=infections, border_color="gray90", border_width=1, hover=False, text="Infezioni in atto", font=("Microsoft Tai Le", 10), checkmark_color="#ffffff", fg_color="#287cfa")

        dialog_frame.pack()

        registry_label.pack(side=tk.TOP, anchor=tk.W, padx=(20, 0))
        name_entry.pack(side=tk.TOP, anchor=tk.W, padx=(20, 20), pady=(5, 5))
        surname_entry.pack(side=tk.TOP, anchor=tk.W, padx=(20, 20), pady=(0, 20))

        planning_label.pack(side=tk.TOP, anchor=tk.W, padx=(20, 0))
        waiting_list_date_entry.pack(side=tk.TOP, anchor=tk.W, padx=(20, 20), pady=(5, 5))
        anesthesia_checkbox.pack(side=tk.TOP, anchor=tk.W, padx=(20, 20), pady=(5, 5))
        infections_checkbox.pack(side=tk.TOP, anchor=tk.W, padx=(20, 20), pady=(0, 20))


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

    FRAME_BORDER_COLOR = "gray90"

    def __init__(self, master):
        self.master = master

        # left toolbar frame
        self.toolbar_frame = ctk.CTkFrame(master=self.master, fg_color="#F4F4F8", corner_radius=0)
        self.toolbar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        # log output and footer
        self.right_frame = ctk.CTkFrame(master=self.master, fg_color="#F4F4F8")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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
        self.create_toolbar()
        self.create_summary_frame()
        self.create_notebook()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_summary_frame(self):
        self.summary_frame = ctk.CTkFrame(master=self.right_frame, fg_color="#FFFFFF", width=300, border_color=self.FRAME_BORDER_COLOR, border_width=1)
        self.summary_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=(5, 10), pady=(10, 10))

    def create_toolbar(self):
        toolbar_icon_sampling_X = 20
        toolbar_icon_sampling_Y = 20

        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/new-document.png",
            "new_button",
            self.new_planning_callback,
            text="Nuova scheda",
        )
        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/xlsx-file-format-extension.png",
            "open_button",
            self.import_callback,
            text="Importa...",
        )
        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/floppy-disk.png",
            "save_button",
            self.export_callback,
            text="Salva",
        )
        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/bin.png",
            "close_active_tab_button",
            self.close_active_tab,
            text="Chiudi scheda attiva",
            state=tk.DISABLED,
        )

        separator = ttk.Separator(master=self.toolbar_frame, orient="horizontal")
        separator.pack(side=tk.TOP, padx=(5, 5), pady=(5, 5), fill=tk.X)

        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/add-user.png",
            self.ADD_PATIENT_BUTTON,
            self.add_patient,
            text="Aggiungi paziente",
            state=tk.NORMAL,
        )

        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/editing.png",
            self.EDIT_PATIENT_BUTTON,
            self.edit_patient,
            text="Modifica paziente",
            state=tk.NORMAL,
        )

        separator = ttk.Separator(master=self.toolbar_frame, orient="horizontal")
        separator.pack(side=tk.TOP, padx=(5, 5), pady=(5, 5), fill=tk.X)

        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/play-button.png",
            "play_button",
            self.launch_solver,
            text="Calcola pianificazione",
            state=tk.NORMAL,
        )

        self.add_toolbar_button(
            toolbar_icon_sampling_X,
            toolbar_icon_sampling_Y,
            "resources/stop-button.png",
            "stop_button",
            self.stop_solver,
            text="Interrompi pianificazione",
            state=tk.NORMAL,
        )
    
    def launch_solver(self):
        pass

    def stop_solver(self):
        pass

    def add_toolbar_button(
        self,
        x_subsample,
        y_subsample,
        icon_path,
        button_name,
        command,
        text=None,
        state=tk.NORMAL,
    ):
        icon = ctk.CTkImage(Image.open(icon_path))

        # to avoid garbage collection of a PhotoImage we need to keep a reference to it
        self.icons.append(icon)
        button = ctk.CTkButton(
            master=self.toolbar_frame,
            image=icon,
            command=command,
            state=state,
            fg_color="#F4F4F8",
            # border_width=1,
            # border_color="gray90",
            hover_color="#D7D8D9",
            text=text,
            text_color="#000000",
            font=("Microsoft Tai Le Bold", 11),
            width=48,
            height=48,
            anchor=tk.W
        )
        button.pack(side=tk.TOP, anchor=tk.W, expand=False, fill=tk.X, padx=(5, 5), pady=(5, 5))

        # tktooltip.ToolTip(widget=button, msg=text, fg="#000000", bg="#ffffff")


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
            close_active_tab_button.state = tk.DISABLED

    def solve(self):
        pass

    def import_callback(self):
        selected_file = filedialog.askopenfile(
            filetypes=[(self.EXCEL_FILE,
                        ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        input_tab = self.notebook.add("Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        import_data_frame = pandas.read_excel(selected_file.name)
        self.initialize_input_table(input_tab=input_tab, data_frame=import_data_frame)

    def export_callback(self):
        selected_filetype = tk.StringVar()
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
        input_tab = self.notebook.add("Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        self.initialize_input_table(input_tab=input_tab, data_frame=None)

    def create_notebook(self):
        self.notebook = ctk.CTkTabview(self.right_frame, fg_color="#FFFFFF", border_color=self.FRAME_BORDER_COLOR, border_width=1)
        self.notebook.pack(side=tk.TOP, expand=True, fill= tk.BOTH, padx=(10, 5), pady=(0, 5))

    def initialize_input_table(self, input_tab, data_frame):
        if data_frame is None:
            columns = {
            "Nome": [],
            "Cognome": [],
            "Prestazioni": [],
            "Anestesia": [],
            "Infezioni": [],
            "Data inserimento in lista": [],
            }
            data_frame = pandas.DataFrame(data=columns)

        table = Table(master=input_tab,
                data_frame=data_frame,
                row_height=60,
                header_height=60,
                fit_criterion=FitCriterion.FIT_HEADER_AND_COL_MAX_LENGTH,
                row_separator_width=1)
        table.pack()

        close_active_tab_button = self.upper_frame.nametowidget("toolbar_frame.close_active_tab_button")
        close_active_tab_button.state = tk.NORMAL

    def create_log_text_box(self):
        # self.output_frame = Frame(master=self.lower_frame)
        # self.output_frame.pack(fill=tk.BOTH, expand=True)

        self.text_box = ctk.CTkTextbox(master=self.right_frame, fg_color="#FFFFFF", border_color=self.FRAME_BORDER_COLOR, border_width=1)
        self.text_box.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=(10, 5), pady=(5, 10))
        # self.text_box.config(background="#ffffff", fg="#000000", font=("Roboto", 10))

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
