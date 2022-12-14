import sys
import re
import tkinter as ctk
from PIL import Image
from tkinter import filedialog
import pandas
import customtkinter as ctk
from bootstraptable import Table, FitCriterion
from controller import Controller
from math import ceil
from util import StdoutRedirector


class EntryWithLabel(ctk.CTkFrame):

    def __init__(self,
                 master,
                 frame_color,
                 label_text,
                 label_color,
                 label_text_color,
                 entry_color,
                 entry_default_text="",
                 entry_width=200,
                 label_width=10,
                 entry_border_width=1,
                 entry_font=("Source Sans Pro", 14),
                 entry_state=ctk.NORMAL,
                 label_font=("Source Sans Pro", 14),
                 label_side=ctk.TOP,
                 label_anchor=ctk.W,
                 entry_side=ctk.TOP,
                 entry_anchor=ctk.W,
                 **kwargs):
        super(EntryWithLabel, self).__init__(master=master,
                                             fg_color=frame_color,
                                             **kwargs)

        self.entry_variable = ctk.StringVar()
        self.entry_variable.set(entry_default_text)
        self.entry = ctk.CTkEntry(master=self,
                                  textvariable=self.entry_variable,
                                  width=entry_width,
                                  border_width=entry_border_width,
                                  border_color="gray80",
                                  state=entry_state,
                                  fg_color=entry_color,
                                  font=entry_font
                                  )

        self.label = ctk.CTkLabel(master=self,
                                  text=label_text,
                                  width=label_width,
                                  anchor=ctk.W,
                                  text_color=label_text_color,
                                  fg_color=label_color,
                                  font=label_font)

        self.label_side = label_side
        self.label_anchor = label_anchor
        self.entry_side = entry_side
        self.entry_anchor = entry_anchor

    def pack(self, **kwargs):
        ctk.CTkFrame.pack(self, **kwargs)
        self.label.pack(side=self.label_side, anchor=self.label_anchor)
        self.entry.pack(side=self.entry_side, anchor=self.entry_anchor)

    def destroy(self):
        self.entry.destroy()
        self.label.destroy()
        super().destroy()


class GUI(object):

    # constants
    EXCEL_FILE = "File Excel"
    ODF_FILE = "ODF Spreadsheet (.odf)"

    WHITE = "#FFFFFF"
    BLACK = "#000000"
    CRAYON_BLUE = "#287CFA"
    DARK_CRAYON_BLUE = "#1265EA"
    THEME1_COLOR1 = "#F4F4F8"
    THEME1_COLOR2 = "#FFFFFF"
    # THEME1_COLOR2 = "#DBDBDB"

    THEME2_COLOR1 = "#565766"
    THEME2_COLOR2 = "#342E37"

    SOURCE_SANS_PRO_SMALL = ("Source Sans Pro", 14)
    SOURCE_SANS_PRO_MEDIUM = ("Source Sans Pro", 18)
    SOURCE_SANS_PRO_MEDIUM_BOLD = ("Source Sans Pro Bold", 18)

    PLANNING_HEADER = {"Nome": [],
                       "Cognome": [],
                       "Prestazioni": [],
                       "Anestesia": [],
                       "Infezioni": [],
                       "Data inserimento in lista": [],
                       }

    WELCOME_MESSAGE = "Welcome to the Interventional Radiology Planner and Scheduler."
    PROCEDURES = {"69-39993": "69-39993",
                  "69-87541": "69-87541",
                  "69-51991": "69-51991",
                  "69-56991": "69-56991",
                  "69-55121": "69-55121",
                  "69-5198": "69-5198",
                  "69-8847": "69-8847",
                  "69-88495": "69-88495",
                  "69-8783": "69-8783",
                  "69-99252": "69-99252",
                  "69-4311": "69-4311",
                  "69-56992": "69-56992",
                  "69-391": "69-391",
                  "69-51993": "69-51993",
                  "69-55122": "69-55122",
                  "69-51992": "69-51992",
                  "69-51121": "69-51121",
                  "69-9929A": "69-9929A",
                  "69-9852": "69-9852",
                  "69-39992": "69-39992",
                  "69-5019": "69-5019",
                  "69-54991": "69-54991",
                  "69-88422": "69-88422",
                  "69-88651": "69-88651",
                  "69-88494": "69-88494",
                  "69-549110": "69-549110",
                  "69-8845": "69-8845",
                  "69-83211": "69-83211",
                  "69-39998": "69-39998",
                  "69-6011": "69-6011",
                  "69-DBT": "69-DBT",
                  "69-887410": "69-887410",
                  "69-88441": "69-88441",
                  "69-5110": "69-5110",
                  "69-5103": "69-5103",
                  "69-5029": "69-5029",
                  "69-40192": "69-40192",
                  "69-40191": "69-40191"
                  }

    class InsertionDialog():

        def __init__(self,
                     parent_view,
                     frame_color_1,
                     frame_color_2,
                     section_font,
                     elements_font,
                     labels_color,
                     labels_text_color,
                     entries_color,
                     checkboxes_color,
                     checkmarks_color):

            self.parent_view = parent_view
            self.procedure_variables = {}

            self.frame_color_1 = frame_color_1
            self.frame_color_2 = frame_color_2
            self.section_font = section_font
            self.elements_font = elements_font
            self.labels_color = labels_color
            self.labels_text_color = labels_text_color
            self.entries_color = entries_color
            self.checkboxes_color = checkboxes_color
            self.checkmarks_color = checkmarks_color

            self.dialog = ctk.CTkToplevel(fg_color=frame_color_1)

            self.procedure_checkboxes = []
            self.checkbox_frames = []
            self.checkboxes_per_row = 4
            self.checkbox_frames_number = ceil(len(self.parent_view.PROCEDURES.items()) / self.checkboxes_per_row)

            self.summary_procedures_labels = {}

            self.create_registry_frame()
            self.create_summary_frame()
            self.create_procedure_frame()

            # self.confirm_button = ctk.CTkButton(master=self.registry_frame,
            #                                     text="Conferma",
            #                                     fg_color=checkboxes_color,
            #                                     hover_color="#1265EA",
            #                                     font=elements_font,
            #                                     text_color="#FFFFFF",
            #                                     width=100,
            #                                     corner_radius=3,
            #                                     command=self.save_patient)



            self.pack_summary_frame()
            self.pack_registry_frame()
            self.pack_procedure_frame()

            # self.confirm_button.pack(side=ctk.BOTTOM,
            #                          anchor=ctk.E,
            #                          padx=(0, 20),
            #                          pady=(0, 20))

            # self.summary_label.pack(side=ctk.TOP,
            #                        anchor=ctk.NW,
            #                        padx=(20, 150),
            #                        pady=(0, 0))

            self.bind_summary_interaction()

        def pack_registry_frame(self):
            self.registry_frame.pack(side=ctk.LEFT, fill=ctk.Y,
                                               padx=(20, 10),
                                               pady=(20, 20))

            self.registry_label.pack(side=ctk.TOP,
                                     anchor=ctk.W,
                                     padx=(20, 0),
                                     pady=(20, 0))
            self.name_entry.pack(side=ctk.TOP,
                                 anchor=ctk.W,
                                 padx=(20, 20))
            self.surname_entry.pack(side=ctk.TOP,
                                    anchor=ctk.W,
                                    padx=(20, 20))

            self.waiting_list_date_entry.pack(side=ctk.TOP,
                                              anchor=ctk.W,
                                              padx=(20, 20),
                                              pady=(0, 5))
            self.anesthesia_checkbox.pack(side=ctk.TOP,
                                          anchor=ctk.W,
                                          padx=(20, 20),
                                          pady=(5, 5))
            self.infections_checkbox.pack(side=ctk.TOP,
                                          anchor=ctk.W,
                                          padx=(20, 20),
                                          pady=(0, 20))


        def create_registry_entry(self, label_text):
            return EntryWithLabel(self.registry_frame,
                                  label_text=label_text,
                                  frame_color=self.frame_color_1,
                                  label_color=self.labels_color,
                                  label_text_color=self.labels_text_color,
                                  entry_color=self.frame_color_1)

        def create_registry_checkbox(self, label_text):
            variable = ctk.BooleanVar(False)
            return ctk.CTkCheckBox(master=self.registry_frame,
                                                       variable=variable,
                                                       border_color="gray80",
                                                       border_width=1,
                                                       hover=False,
                                                       text=label_text,
                                                       text_color=self.labels_text_color,
                                                       font=self.elements_font,
                                                       checkmark_color=self.checkmarks_color,
                                                       fg_color=self.checkboxes_color,
                                                       checkbox_height=15,
                                                       checkbox_width=15,
                                                       corner_radius=3,
                                                       command=lambda label_text=label_text: self.update_summary_checkboxes(label_text))

        def update_summary_checkboxes(self, label_text):
            if label_text == "Anestesia":
                if self.anesthesia_checkbox.get():
                    self.summary_anesthesia_entry.entry_variable.set("Sì")
                else:
                    self.summary_anesthesia_entry.entry_variable.set("No")
            if label_text == "Infezioni in atto":
                if self.infections_checkbox.get():
                    self.summary_infections_entry.entry_variable.set("Sì")
                else:
                    self.summary_infections_entry.entry_variable.set("No")

        def create_registry_frame(self):
            self.registry_frame = ctk.CTkFrame(master=self.dialog,
                                               width=100,
                                               height=100,
                                               fg_color=self.frame_color_1,
                                               border_width=1,
                                               border_color="gray80")

            self.registry_label = ctk.CTkLabel(master=self.registry_frame,
                                               text="Informazioni paziente",
                                               font=self.section_font,
                                               text_color=self.labels_text_color,
                                               width=10)
            self.name_entry = self.create_registry_entry(label_text="Nome")
            self.surname_entry = self.create_registry_entry(label_text="Cognome")
            self.waiting_list_date_entry = self.create_registry_entry(label_text="Inserimento in lista d'attesa")

            self.anesthesia_checkbox = self.create_registry_checkbox(label_text="Anestesia")
            self.infections_checkbox = self.create_registry_checkbox(label_text="Infezioni in atto")

        def bind_summary_interaction(self):
            self.name_entry.entry_variable.trace_add(mode="write",
                                                     callback=lambda *_,
                                                     var=self.name_entry.entry_variable,
                                                     summary_var=self.summary_name_entry.entry_variable: self.update_summary(var, summary_var))
            self.surname_entry.entry_variable.trace_add(mode="write",
                                                     callback=lambda *_,
                                                     var=self.surname_entry.entry_variable,
                                                     summary_var=self.summary_surname_entry.entry_variable: self.update_summary(var, summary_var))
            self.waiting_list_date_entry.entry_variable.trace_add(mode="write",
                                                     callback=lambda *_,
                                                     var=self.waiting_list_date_entry.entry_variable,
                                                     summary_var=self.summary_date_entry.entry_variable: self.update_summary(var, summary_var))

        def update_summary(self, var, summary_var):
            summary_var.set(var.get())

        def pack_summary_frame(self):
            self.summary_outer_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, padx=(20, 20), pady=(0, 20))
            self.summary_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, pady=(0, 20))
            self.summary_registry_frame.pack(side=ctk.LEFT, fill=ctk.Y)
            self.summary_procedure_frame.pack(side=ctk.LEFT, fill=ctk.BOTH)

            self.summary_label.pack(side=ctk.TOP)

            self.pack_summary_entry(self.summary_name_entry)
            self.pack_summary_entry(self.summary_surname_entry)
            self.pack_summary_entry(self.summary_date_entry)
            self.pack_summary_entry(self.summary_anesthesia_entry)
            self.pack_summary_entry(self.summary_infections_entry)

            self.pack_summary_entry(self.summary_procedures_label, padx=(10, 0), fill=None)

        def pack_summary_entry(self, summary_label, padx=(20, 10), fill=ctk.X):
            summary_label.pack(side=ctk.TOP,
                               anchor=ctk.W,
                               padx=padx,
                               pady=(0, 0),
                               fill=fill)

        def create_summary_frame(self):
            self.summary_outer_frame = ctk.CTkFrame(master=self.dialog,
                                              fg_color=self.frame_color_2)
            self.summary_frame = ctk.CTkFrame(master=self.summary_outer_frame,
                                              fg_color=self.frame_color_2)

            self.summary_registry_frame = ctk.CTkFrame(master=self.summary_frame,
                                                       fg_color=self.frame_color_2,
                                                       width=300)

            self.summary_name_entry = self.create_summary_entry("Nome: ")
            self.summary_surname_entry = self.create_summary_entry("Cognome: ")
            self.summary_date_entry = self.create_summary_entry("Inserimento in lista: ")
            self.summary_anesthesia_entry = self.create_summary_entry("Anestesia: ", entry_text="No")
            self.summary_infections_entry = self.create_summary_entry("Infezioni in atto: ", entry_text="No")

            self.summary_procedure_frame = ctk.CTkFrame(master=self.summary_frame,
                                                        fg_color=self.frame_color_2)

            self.summary_procedures_label = ctk.CTkLabel(master=self.summary_procedure_frame,
                                                         text="Procedure:",
                                                         font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                                         text_color=self.labels_text_color,
                                                         width=10)

            self.summary_label = ctk.CTkLabel(master=self.summary_outer_frame,
                                         fg_color=self.frame_color_2,
                                         # corner_radius=0,
                                         text="Riepilogo paziente",
                                         font=self.parent_view.SOURCE_SANS_PRO_MEDIUM_BOLD)

        def create_summary_entry(self, label_text, entry_text=""):
            return EntryWithLabel(master=self.summary_registry_frame,
                                  label_text=label_text,
                                  entry_default_text=entry_text,
                                  label_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                  entry_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                  frame_color=self.frame_color_2,
                                  label_color=self.frame_color_2,
                                  label_text_color=self.labels_text_color,
                                  entry_color=self.frame_color_2,
                                  entry_border_width=0,
                                  entry_state=ctk.DISABLED,
                                  entry_width=140,
                                  label_side=ctk.LEFT,
                                  label_anchor=ctk.W,
                                  entry_side=ctk.RIGHT,
                                  entry_anchor=ctk.E)

        def pack_procedure_frame(self):
            self.procedures_frame.pack(side=ctk.RIGHT, fill=ctk.Y,
                                                 padx=(10, 20),
                                                 pady=(20, 20))
            self.procedures_label.pack(side=ctk.TOP, anchor=ctk.NW, padx=(20, 0), pady=(20,0))
            self.procedures_label_searchbox.pack(side=ctk.TOP, anchor=ctk.NW, padx=(20, 0))

            self.pack_checkbox_frames()
            self.pack_procedure_checkboxes()

        def pack_checkbox_frames(self):
            for idx in range(0, self.checkbox_frames_number):
                pady = (0, 0)
                if idx == 0:
                    pady = (20, 0)
                if idx == self.checkbox_frames_number - 1:
                    pady = (0, 20)
                self.checkbox_frames[idx].pack(side=ctk.TOP,
                               padx=(20, 1),
                               pady=pady,
                               fill=ctk.X)

        def create_procedure_frame(self):
            self.procedures_frame = ctk.CTkFrame(master=self.dialog,
                                                 fg_color=self.frame_color_1,
                                                 border_color="gray80",
                                                 border_width=1)
            self.procedures_label = ctk.CTkLabel(master=self.procedures_frame,
                                            text="Prestazioni",
                                            font=self.section_font,
                                            text_color=self.labels_text_color,
                                            width=10)

            self.procedures_label_searchbox = EntryWithLabel(master=self.procedures_frame,
                                                        label_text="Filtra per nome",
                                                        frame_color=self.frame_color_1,
                                                        label_color=self.labels_color,
                                                        label_text_color=self.labels_text_color,
                                                        entry_color=self.frame_color_1)

            self.procedures_label_searchbox.entry_variable.trace_add(mode="write",
                                                                callback=lambda *_,
                                                                var=self.procedures_label_searchbox.entry_variable: self.filter_procedures(var))

            self.initialize_procedure_checkboxes()

        def initialize_procedure_checkboxes(self):
            for idx in range(0, self.checkbox_frames_number):
                row_frame = ctk.CTkFrame(master=self.procedures_frame,
                                         fg_color=self.frame_color_1)
                self.checkbox_frames.append(row_frame)

            for procedure in self.parent_view.PROCEDURES.items():
                procedure_variable = ctk.BooleanVar(False)
                self.procedure_variables[procedure[0]] = procedure_variable

            self.create_procedure_checkboxes(procedures=list(self.parent_view.PROCEDURES.items()))

        def save_patient(self):
            self.dialog.destroy()

        def filter_procedures(self, var):
            pattern = var.get()
            filtered_procedures = []
            if pattern == "":
                filtered_procedures = list(self.parent_view.PROCEDURES.items())
            else:
                for procedure in self.parent_view.PROCEDURES.items():
                    if re.search(pattern.lower(), procedure[1].lower()) is not None:
                        filtered_procedures.append(procedure)

            self.create_procedure_checkboxes(procedures=filtered_procedures)
            self.pack_procedure_checkboxes()

        def pack_procedure_checkboxes(self):
            for checkbox in self.procedure_checkboxes:
                checkbox.pack(side=ctk.LEFT,
                              anchor=ctk.W,
                              padx=(0, 20))

        def create_procedure_checkboxes(self, procedures):
            if len(procedures) == len(self.procedure_checkboxes):
                return

            for checkbox in self.procedure_checkboxes:
                checkbox.destroy()

            self.procedure_checkboxes = []

            for frame in self.checkbox_frames:
                frame_checkboxes = 0
                while frame_checkboxes < self.checkboxes_per_row and procedures:
                    procedure = procedures.pop(0)
                    procedure_variable = self.procedure_variables[procedure[0]]
                    procedure_checkbox = ctk.CTkCheckBox(master=frame,
                                                         variable=procedure_variable,
                                                         border_color="gray80",
                                                         border_width=1,
                                                         hover=False,
                                                         text=procedure[0],
                                                         text_color=self.labels_text_color,
                                                         font=self.elements_font,
                                                         checkmark_color=self.checkmarks_color,
                                                         fg_color=self.checkboxes_color,
                                                         checkbox_height=15,
                                                         checkbox_width=15,
                                                         corner_radius=3,
                                                         width=90,
                                                         command=lambda *_, procedure_code=procedure[0], procedure_variable=procedure_variable: self.update_summary_procedures(procedure_code, procedure_variable))
                    self.procedure_checkboxes.append(procedure_checkbox)
                    frame_checkboxes += 1

                if not procedures:
                    break

        def update_summary_procedures(self, procedure_code, procedure_variable):
            if procedure_variable.get():
                text = "￮ " + procedure_code + " " + self.parent_view.PROCEDURES[procedure_code]
                summary_label = ctk.CTkLabel(master=self.summary_procedure_frame,
                                             text=text)
                self.summary_procedures_labels[procedure_code] = summary_label
                summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(20, 0))
            else:
                self.summary_procedures_labels[procedure_code].destroy()
                del self.summary_procedures_labels[procedure_code]


    def __init__(self, master):
        self.master = master

        self.dialogs = []
        self.planning_number = 0
        self.tabs = 0
        self.tables = dict()

        self.controller: Controller = None

        self.initializeUI()

    def bind_controller(self, controller):
        self.controller = controller

    def initializeUI(self):
        self.theme = "light"

        # left toolbar frame
        self.toolbar_frame = ctk.CTkFrame(master=self.master,
                                          fg_color=(self.THEME1_COLOR2,
                                                    self.THEME2_COLOR2),
                                          corner_radius=0)
        self.toolbar_frame.pack(side=ctk.LEFT, fill=ctk.Y, expand=False)

        # log output and footer
        self.right_frame = ctk.CTkFrame(master=self.master,
                                        fg_color=(self.THEME1_COLOR1,
                                                  self.THEME2_COLOR1),
                                        corner_radius=0)
        self.right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        self.create_toolbar()
        self.create_summary_frame()
        self.create_notebook()
        self.create_log_text_box()

        print(self.WELCOME_MESSAGE)

    def create_summary_frame(self):
        self.summary_frame = ctk.CTkFrame(master=self.right_frame,
                                          fg_color=(self.THEME1_COLOR2, self.THEME2_COLOR2))
        self.summary_frame.pack(side=ctk.RIGHT,
                                fill=ctk.Y,
                                expand=False,
                                padx=(10, 20),
                                pady=(20, 20))

        right_x_pad = 150

        summary_label = ctk.CTkLabel(master=self.summary_frame,
                                     fg_color=(self.THEME1_COLOR2,
                                               self.THEME2_COLOR2),
                                     text="Riepilogo pazienti",
                                     font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        summary_label.pack(side=ctk.TOP,
                           anchor=ctk.W,
                           padx=(20, right_x_pad),
                           pady=(20, 0))

        total_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                            fg_color=(self.THEME1_COLOR2,
                                                      self.THEME2_COLOR2),
                                            text="Pazienti totali: ",
                                            font=self.SOURCE_SANS_PRO_SMALL)
        total_patients_label.pack(side=ctk.TOP,
                                  anchor=ctk.W,
                                  padx=(20, right_x_pad),
                                  pady=(0, 0))

        total_anesthesia_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                                       fg_color=(self.THEME1_COLOR2,
                                                                 self.THEME2_COLOR2),
                                                       text="Pazienti con anestesia: ",
                                                       font=self.SOURCE_SANS_PRO_SMALL)
        total_anesthesia_patients_label.pack(side=ctk.TOP,
                                             anchor=ctk.W,
                                             padx=(20, right_x_pad),
                                             pady=(0, 0))

        total_infectious_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                                       fg_color=(self.THEME1_COLOR2,
                                                                 self.THEME2_COLOR2),
                                                       text="Pazienti con infezioni in atto: ",
                                                       font=self.SOURCE_SANS_PRO_SMALL)
        total_infectious_patients_label.pack(side=ctk.TOP,
                                             anchor=ctk.W,
                                             padx=(20, right_x_pad),
                                             pady=(0, 0))

        solver_label = ctk.CTkLabel(master=self.summary_frame,
                                    fg_color=(self.THEME1_COLOR2,
                                              self.THEME2_COLOR2),
                                    text="Riepilogo impostazioni solver",
                                    font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        solver_label.pack(side=ctk.TOP,
                          anchor=ctk.W,
                          padx=(20, right_x_pad),
                          pady=(20, 0))

        gap_label = ctk.CTkLabel(master=self.summary_frame,
                                 fg_color=(self.THEME1_COLOR2,
                                           self.THEME2_COLOR2),
                                 text="Gap (%): ",
                                 font=self.SOURCE_SANS_PRO_SMALL)
        gap_label.pack(side=ctk.TOP,
                       anchor=ctk.W,
                       padx=(20, right_x_pad),
                       pady=(0, 0))
        time_limit_label = ctk.CTkLabel(master=self.summary_frame,
                                        fg_color=(self.THEME1_COLOR2,
                                                  self.THEME2_COLOR2),
                                        text="Timeout (s): ",
                                        font=self.SOURCE_SANS_PRO_SMALL)
        time_limit_label.pack(side=ctk.TOP,
                              anchor=ctk.W,
                              padx=(20, right_x_pad),
                              pady=(0, 0))

    def create_toolbar(self):

        self.create_toolbar_button("resources/new.png",
                                   "resources/new_w.png",
                                   self.new_planning_callback,
                                   text="Nuova scheda",
                                   pady=(20, 0)
                                   )
        self.create_toolbar_button("resources/xlsx.png",
                                   "resources/xlsx_w.png",
                                   self.import_callback,
                                   text="Importa da file Excel",
                                   )
        self.create_toolbar_button("resources/export.png",
                                   "resources/export_w.png",
                                   self.export_callback,
                                   text="Esporta in file Excel",
                                   )
        self.close_tab_button = self.create_toolbar_button("resources/delete.png",
                                                           "resources/delete_w.png",
                                                           self.close_active_tab,
                                                           text="Chiudi scheda attiva",
                                                           state=ctk.DISABLED,
                                                           )

        self.create_toolbar_button("resources/add-patient.png",
                                   "resources/add-patient_w.png",
                                   self.add_patient,
                                   text="Aggiungi paziente"
                                   )

        self.create_toolbar_button("resources/edit.png",
                                   "resources/edit_w.png",
                                   self.edit_patient,
                                   text="Modifica paziente selezionato"
                                   )

        self.create_toolbar_button("resources/run.png",
                                   "resources/run_w.png",
                                   self.launch_solver,
                                   text="Calcola pianificazione"
                                   )

        self.create_toolbar_button("resources/stop.png",
                                   "resources/stop_w.png",
                                   self.stop_solver,
                                   text="Interrompi pianificazione"
                                   )

        self.theme_mode_switch = ctk.CTkSwitch(master=self.toolbar_frame,
                                               text="Modalità notturna",
                                               font=self.SOURCE_SANS_PRO_SMALL,
                                               command=self.switch_theme_mode,
                                               progress_color=self.DARK_CRAYON_BLUE)
        self.theme_mode_switch.pack(side=ctk.BOTTOM, pady=(0, 20))

    def switch_theme_mode(self):
        if self.theme == "light":
            self.theme = "dark"
            ctk.set_appearance_mode("dark")
            for table in self.tables.values():
                table.switch_theme("dark")
        else:
            self.theme = "light"
            ctk.set_appearance_mode("light")
            for table in self.tables.values():
                table.switch_theme("light")

    def launch_solver(self):
        pass

    def stop_solver(self):
        pass

    def create_toolbar_button(self,
                              theme1_icon_path,
                              theme2_icon_path,
                              command,
                              text=None,
                              state=ctk.NORMAL,
                              padx=(0, 0),
                              pady=(0, 0)
                              ):
        icon = ctk.CTkImage(Image.open(theme1_icon_path),
                            Image.open(theme2_icon_path))

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
            anchor=ctk.W
        )
        button.pack(side=ctk.TOP, anchor=ctk.W, expand=False,
                    fill=ctk.X, padx=padx, pady=pady)
        button.bind("<Enter>", command=self.hover_button, add="+")

        return button

    def hover_button(self, event):
        print(event.widget)

    def add_patient(self):
        self.InsertionDialog(parent_view=self,
                             frame_color_1=(self.WHITE,
                                         self.THEME2_COLOR2),
                             frame_color_2=(self.THEME1_COLOR1,
                                         self.THEME2_COLOR1),
                             section_font=self.SOURCE_SANS_PRO_MEDIUM,
                             elements_font=self.SOURCE_SANS_PRO_SMALL,
                             labels_color=(self.WHITE,
                                           self.THEME2_COLOR2),
                             labels_text_color=(self.BLACK,
                                                self.WHITE),
                             entries_color=(self.THEME1_COLOR1,
                                            self.THEME2_COLOR1),
                             checkmarks_color=self.WHITE,
                             checkboxes_color=self.CRAYON_BLUE)

    def edit_patient(self):
        dialog = self.InsertionDialog(parent_view=self,
                                      frame_color_1=(self.WHITE,
                                                   self.THEME2_COLOR2),
                                      frame_color_2=(self.THEME1_COLOR1,
                                                   self.THEME2_COLOR1),
                                      section_font=self.SOURCE_SANS_PRO_MEDIUM,
                                      elements_font=self.SOURCE_SANS_PRO_SMALL,
                                      labels_color=(self.WHITE,
                                                    self.THEME2_COLOR2),
                                      labels_text_color=(self.BLACK,
                                                         self.WHITE),
                                      entries_color=(self.THEME1_COLOR1,
                                                     self.THEME2_COLOR1),
                                      checkmarks_color=self.WHITE,
                                      checkboxes_color=self.CRAYON_BLUE)

    def close_active_tab(self):
        active_tab = self.notebook.get()
        self.notebook.delete(active_tab)
        self.tabs -= 1

        if self.tabs == 0:
            self.close_tab_button.configure(state=ctk.DISABLED)

    def solve(self):
        pass

    def import_callback(self):
        selected_file = filedialog.askopenfile(
            filetypes=[(self.EXCEL_FILE,
                        ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        controller.import_sheet(selected_file=selected_file)

    def export_callback(self):
        selected_filetype = ctk.StringVar()
        file_name = filedialog.asksaveasfilename(filetypes=[(self.EXCEL_FILE, ["*.xlsx"])],
                                                 typevariable=selected_filetype)
        if selected_filetype.get() == self.EXCEL_FILE:
            extension = ".xlsx"
        else:
            raise Exception("...")

        file_name += str(extension)

        selected_tab = self.notebook.get()
        table = self.tables[selected_tab]

        self.controller.export_sheet(table.data_frame, file_name)

    def new_planning_callback(self):
        controller.create_empty_planning()

    def create_notebook(self):
        self.notebook = ctk.CTkTabview(self.right_frame,
                                       fg_color=(self.WHITE,
                                                 self.THEME2_COLOR2),
                                       segmented_button_selected_color=self.CRAYON_BLUE,
                                       segmented_button_selected_hover_color=self.DARK_CRAYON_BLUE)
        self.notebook.pack(side=ctk.TOP,
                           expand=True,
                           fill=ctk.BOTH,
                           padx=(20, 10),
                           pady=(0, 10))

    def initialize_input_table(self, tab_name, data_frame):
        if data_frame is None:
            columns = self.PLANNING_HEADER
            data_frame = pandas.DataFrame(data=columns)

        input_tab = self.notebook.add(tab_name)

        table = Table(master=input_tab,
                      data_frame=data_frame,
                      row_height=60,
                      header_height=60,
                      fit_criterion=FitCriterion.FIT_HEADER_AND_COL_MAX_LENGTH,
                      row_separator_width=1,
                      width=1200,
                      pagination_size=3,
                      theme=self.theme,
                      even_row_colors=("#ffffff", self.THEME2_COLOR2))
        table.pack()

        self.tables[tab_name] = table

        self.tabs += 1
        self.close_tab_button.configure(state=ctk.NORMAL)

    def create_log_text_box(self):
        self.text_box = ctk.CTkTextbox(master=self.right_frame,
                                       fg_color=(self.WHITE,
                                                 self.THEME2_COLOR2),
                                       text_color=(self.BLACK, self.WHITE),
                                       font=self.SOURCE_SANS_PRO_SMALL)
        self.text_box.pack(side=ctk.TOP,
                           fill=ctk.BOTH,
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
controller = Controller(model=None, view=gui)
gui.bind_controller(controller=controller)

root.mainloop()
