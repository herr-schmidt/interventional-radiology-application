import sys
import tkinter as tk
from PIL import Image
from tkinter import filedialog
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

    def __init__(self, master, frame_color, label_text, label_color, entry_color, entry_width=200, label_width=10, font=("Source Sans Pro", 14)):
        super(EntryWithLabel, self).__init__(master=master,
                                             width=200,
                                             fg_color=frame_color)

        self.entry_variable = tk.StringVar()
        self.entry = ctk.CTkEntry(master=self,
                                  textvariable=self.entry_variable,
                                  width=entry_width,
                                  border_width=1,
                                  border_color="gray90",
                                  fg_color=entry_color)

        self.label = ctk.CTkLabel(master=self,
                                  text=label_text,
                                  width=label_width,
                                  anchor=tk.W,
                                  fg_color=label_color,
                                  font=font)

        self.label.pack(side=tk.TOP, anchor=tk.W)
        self.entry.pack(side=tk.LEFT)


class InsertionDialog():

    def __init__(self, frame_color, section_font, elements_font, labels_color, entries_color, checkboxes_color, checkmarks_color):
        self.dialog = ctk.CTkToplevel(fg_color=frame_color)

        dialog_frame = ctk.CTkFrame(master=self.dialog,
                                    width=100, height=100,
                                    fg_color=frame_color)

        registry_label = ctk.CTkLabel(master=dialog_frame,
                                      text="Anagrafica",
                                      font=section_font,
                                      width=10)
        name_entry = EntryWithLabel(dialog_frame,
                                    label_text="Nome",
                                    frame_color=frame_color,
                                    label_color=labels_color,
                                    entry_color=entries_color)
        surname_entry = EntryWithLabel(dialog_frame,
                                       label_text="Cognome",
                                       frame_color=frame_color,
                                       label_color=labels_color,
                                       entry_color=entries_color)

        planning_label = ctk.CTkLabel(master=dialog_frame,
                                      text="Pianificazione",
                                      font=section_font,
                                      width=14)
        waiting_list_date_entry = EntryWithLabel(
            dialog_frame,
            frame_color=frame_color,
            label_text="Inserimento in lista d'attesa",
            label_width=24,
            label_color=labels_color,
            entry_color=entries_color)

        anesthesia = tk.BooleanVar(False)
        infections = tk.BooleanVar(False)

        anesthesia_checkbox = ctk.CTkCheckBox(master=dialog_frame,
                                              variable=anesthesia,
                                              border_color="gray90",
                                              border_width=1,
                                              hover=False,
                                              text="Anestesia",
                                              font=elements_font,
                                              checkmark_color=checkmarks_color,
                                              fg_color=checkboxes_color)
        infections_checkbox = ctk.CTkCheckBox(master=dialog_frame,
                                              variable=infections,
                                              border_color="gray90",
                                              border_width=1,
                                              hover=False,
                                              text="Infezioni in atto",
                                              font=elements_font,
                                              checkmark_color=checkmarks_color,
                                              fg_color=checkboxes_color)

        dialog_frame.pack()

        registry_label.pack(side=tk.TOP,
                            anchor=tk.W,
                            padx=(20, 0))
        name_entry.pack(side=tk.TOP,
                        anchor=tk.W,
                        padx=(20, 20),
                        pady=(5, 5))
        surname_entry.pack(side=tk.TOP,
                           anchor=tk.W,
                           padx=(20, 20),
                           pady=(0, 20))

        planning_label.pack(side=tk.TOP, anchor=tk.W, padx=(20, 0))
        waiting_list_date_entry.pack(side=tk.TOP,
                                     anchor=tk.W,
                                     padx=(20, 20),
                                     pady=(5, 5))
        anesthesia_checkbox.pack(side=tk.TOP,
                                 anchor=tk.W,
                                 padx=(20, 20),
                                 pady=(5, 5))
        infections_checkbox.pack(side=tk.TOP,
                                 anchor=tk.W,
                                 padx=(20, 20),
                                 pady=(0, 20))


class GUI(object):

    # constants
    EXCEL_FILE = "File Excel"
    ODF_FILE = "ODF Spreadsheet (.odf)"

    WHITE = "#FFFFFF"
    BLACK = "#000000"
    CRAYON_BLUE = "#287CFA"
    THEME1_COLOR1 = "#F4F4F8"
    THEME1_COLOR2 = "#DBDBDB"

    THEME2_COLOR1 = "#565766"
    THEME2_COLOR2 = "#342E37"

    SOURCE_SANS_PRO_SMALL = ("Source Sans Pro", 14)
    SOURCE_SANS_PRO_MEDIUM = ("Source Sans Pro", 18)
    SOURCE_SANS_PRO_MEDIUM_BOLD = ("Source Sans Pro Bold", 18)

    def __init__(self, master):
        self.master = master

        # left toolbar frame
        self.toolbar_frame = ctk.CTkFrame(master=self.master,
                                          fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
                                          corner_radius=0)
        self.toolbar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        # log output and footer
        self.right_frame = ctk.CTkFrame(master=self.master,
                                        fg_color=(self.THEME1_COLOR1, self.THEME2_COLOR1),
                                        corner_radius=0)
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
        self.dialogs = []

        self.planning_number = 0
        self.tabs = 0

        self.initializeUI()

    def initializeUI(self):
        self.create_toolbar()
        self.create_summary_frame()
        self.create_notebook()
        self.create_log_text_box()

        print("Welcome to the Interventional Radiology Planner and Scheduler.")

    def create_summary_frame(self):
        self.summary_frame = ctk.CTkFrame(master=self.right_frame,
                                          fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2))
        self.summary_frame.pack(side=tk.RIGHT,
                                fill=tk.Y,
                                expand=False,
                                padx=(10, 20),
                                pady=(20, 20))

        right_x_pad = 150

        summary_label = ctk.CTkLabel(master=self.summary_frame,
                                     fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
                                     text="Riepilogo pazienti",
                                     font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        summary_label.pack(side=tk.TOP,
                           anchor=tk.W,
                           padx=(20, right_x_pad),
                           pady=(20, 0))

        total_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                            fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
                                            text="Pazienti totali: ",
                                            font=self.SOURCE_SANS_PRO_SMALL)
        total_patients_label.pack(side=tk.TOP,
                                  anchor=tk.W,
                                  padx=(20, right_x_pad),
                                  pady=(10, 0))

        total_anesthesia_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                                       fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
                                                       text="Pazienti con anestesia: ",
                                                       font=self.SOURCE_SANS_PRO_SMALL)
        total_anesthesia_patients_label.pack(side=tk.TOP,
                                             anchor=tk.W,
                                             padx=(20, right_x_pad),
                                             pady=(0, 0))

        total_infectious_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                                       fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
                                                       text="Pazienti con infezioni in atto: ",
                                                       font=self.SOURCE_SANS_PRO_SMALL)
        total_infectious_patients_label.pack(side=tk.TOP,
                                             anchor=tk.W,
                                             padx=(20, right_x_pad),
                                             pady=(0, 0))

        solver_label = ctk.CTkLabel(master=self.summary_frame,
                                     fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
                                     text="Riepilogo solver",
                                     font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        solver_label.pack(side=tk.TOP,
                           anchor=tk.W,
                           padx=(20, right_x_pad),
                           pady=(20, 0))

    def create_toolbar(self):

        self.create_toolbar_button("resources/new.png",
                                   self.new_planning_callback,
                                   text="Nuova scheda",
                                   pady=(20, 0)
                                   )
        self.create_toolbar_button("resources/xlsx.png",
                                   self.import_callback,
                                   text="Importa da file Excel",
                                   )
        self.create_toolbar_button("resources/export.png",
                                   self.export_callback,
                                   text="Esporta in file Excel",
                                   )
        self.close_tab_button = self.create_toolbar_button("resources/delete.png",
                                                           self.close_active_tab,
                                                           text="Chiudi scheda attiva",
                                                           state=tk.DISABLED,
                                                           )

        self.create_toolbar_button("resources/add-patient.png",
                                   self.add_patient,
                                   text="Aggiungi paziente",
                                   state=tk.NORMAL,
                                   )

        self.create_toolbar_button("resources/edit.png",
                                   self.edit_patient,
                                   text="Modifica paziente selezionato",
                                   state=tk.NORMAL,
                                   )

        self.create_toolbar_button("resources/run.png",
                                   self.launch_solver,
                                   text="Calcola pianificazione",
                                   state=tk.NORMAL,
                                   )

        self.create_toolbar_button("resources/stop.png",
                                   self.stop_solver,
                                   text="Interrompi pianificazione",
                                   state=tk.NORMAL,
                                   )

    def launch_solver(self):
        pass

    def stop_solver(self):
        pass

    def create_toolbar_button(self,
                              icon_path,
                              command,
                              text=None,
                              state=tk.NORMAL,
                              padx=(0, 0),
                              pady=(0, 0)
                              ):
        icon = ctk.CTkImage(Image.open(icon_path))

        button = ctk.CTkButton(
            master=self.toolbar_frame,
            image=icon,
            command=command,
            state=state,
            fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2),
            hover_color=(self.THEME1_COLOR1, self.THEME2_COLOR1),
            corner_radius=0,
            border_spacing=15,
            text=text,
            text_color=(self.BLACK, self.WHITE),
            font=self.SOURCE_SANS_PRO_SMALL,
            # width=48,
            # height=48,
            anchor=tk.W
        )
        button.pack(side=tk.TOP, anchor=tk.W, expand=False,
                    fill=tk.X, padx=padx, pady=pady)
        button.bind("<Enter>", command=self.hover_button, add="+")

        return button

    def hover_button(self, event):
        print(event.widget)
        ctk.set_appearance_mode("dark")

    def add_patient(self):
        dialog = InsertionDialog(frame_color=self.WHITE,
                                 section_font=self.SOURCE_SANS_PRO_MEDIUM,
                                 elements_font=self.SOURCE_SANS_PRO_SMALL,
                                 labels_color=self.WHITE,
                                 entries_color=(self.THEME1_COLOR1, self.THEME2_COLOR1),
                                 checkmarks_color=self.WHITE,
                                 checkboxes_color=self.CRAYON_BLUE)

    def edit_patient(self):
        dialog = InsertionDialog(frame_color=self.WHITE,
                                 section_font=self.SOURCE_SANS_PRO_MEDIUM,
                                 elements_font=self.SOURCE_SANS_PRO_SMALL,
                                 labels_color=self.WHITE,
                                 entries_color=(self.THEME1_COLOR1, self.THEME2_COLOR1),
                                 checkmarks_color=self.WHITE,
                                 checkboxes_color=self.CRAYON_BLUE)

    def close_active_tab(self):
        active_tab = self.notebook.get()
        self.notebook.delete(active_tab)
        self.tabs -= 1

        if self.tabs == 0:
            self.close_tab_button.configure(state=tk.DISABLED)

    def solve(self):
        pass

    def import_callback(self):
        selected_file = filedialog.askopenfile(
            filetypes=[(self.EXCEL_FILE,
                        ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        input_tab = self.notebook.add(
            "Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        import_data_frame = pandas.read_excel(selected_file.name)
        self.initialize_input_table(input_tab=input_tab,
                                    data_frame=import_data_frame)

    def export_callback(self):
        selected_filetype = tk.StringVar()
        file_name = filedialog.asksaveasfilename(filetypes=[(self.EXCEL_FILE, ["*.xlsx"]), (self.ODF_FILE, "*.odf*")],
                                                 typevariable=selected_filetype)
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
                                  index=False  # avoid writing a column of indices
                                  )

    def new_planning_callback(self):
        input_tab = self.notebook.add(
            "Lista pazienti " + str(self.planning_number))
        self.planning_number += 1

        self.initialize_input_table(input_tab=input_tab, data_frame=None)

    def create_notebook(self):
        self.notebook = ctk.CTkTabview(self.right_frame,
                                       fg_color=(self.WHITE, self.THEME2_COLOR2))
        self.notebook.pack(side=tk.TOP,
                           expand=True,
                           fill=tk.BOTH,
                           padx=(20, 10),
                           pady=(0, 10))

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
                      row_separator_width=1,
                      width=1200,
                      pagination_size=2)
        table.pack()

        self.tabs += 1
        self.close_tab_button.configure(state=tk.NORMAL)

    def create_log_text_box(self):
        self.text_box = ctk.CTkTextbox(master=self.right_frame,
                                       fg_color=(self.WHITE, self.THEME2_COLOR2),
                                       text_color=(self.BLACK, self.WHITE),
                                       font=self.SOURCE_SANS_PRO_SMALL)
        self.text_box.pack(side=tk.TOP,
                           fill=tk.BOTH,
                           expand=False,
                           padx=(20, 10),
                           pady=(10, 20))

        sys.stdout = StdoutRedirector(self.text_box)


root = ctk.CTk()
ctk.set_appearance_mode("light")
root.title("Interventional Radiology Planner & Scheduler")
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),
              root.winfo_screenheight()))
root.state("zoomed")

gui = GUI(root)

root.mainloop()
