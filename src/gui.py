import sys
import re
from PIL import Image
from tkinter import filedialog
import pandas
import customtkinter as ctk
from bootstraptable import Table, FitCriterion
from controller import Controller
from math import ceil, floor
from util import StdoutRedirector, DialogMode
import pandas as pd
from embedded_browser import MainBrowserFrame, cef


class EntryWithLabel(ctk.CTkFrame):

    def __init__(self,
                 master,
                 frame_color,
                 label_text,
                 label_color,
                 label_text_color,
                 entry_color,
                 entry_default_text="",
                 entry_border_width=1,
                 entry_font=("Source Sans Pro", 14),
                 entry_state=ctk.NORMAL,
                 label_font=("Source Sans Pro", 14),
                 label_side=ctk.TOP,
                 label_anchor=ctk.W,
                 label_fill=ctk.X,
                 entry_side=ctk.TOP,
                 entry_anchor=ctk.W,
                 entry_fill=ctk.X,
                 **kwargs):
        super(EntryWithLabel, self).__init__(master=master,
                                             fg_color=frame_color,
                                             **kwargs)

        self.entry_variable = ctk.StringVar()
        self.entry_variable.set(entry_default_text)
        self.entry = ctk.CTkEntry(master=self,
                                  textvariable=self.entry_variable,
                                  border_width=entry_border_width,
                                  border_color="gray80",
                                  state=entry_state,
                                  fg_color=entry_color,
                                  font=entry_font
                                  )

        self.label = ctk.CTkLabel(master=self,
                                  text=label_text,
                                  anchor=ctk.W,
                                  text_color=label_text_color,
                                  fg_color=label_color,
                                  font=label_font)

        self.label_side = label_side
        self.label_anchor = label_anchor
        self.label_fill = label_fill
        self.entry_side = entry_side
        self.entry_anchor = entry_anchor
        self.entry_fill = entry_fill

    def pack(self, **kwargs):
        ctk.CTkFrame.pack(self, **kwargs)
        self.label.pack(side=self.label_side,
                        anchor=self.label_anchor,
                        fill=self.label_fill)
        self.entry.pack(side=self.entry_side,
                        anchor=self.entry_anchor,
                        fill=self.entry_fill)

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
                     checkmarks_color,
                     mode=DialogMode.ADD):

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

            self.mode = mode

            self.summary_procedures_labels = {}

            self.create_registry_frame()
            self.create_summary_frame()
            self.create_procedure_frame()
            self.create_buttons()

            self.pack_buttons()
            self.pack_summary_frame()
            self.pack_registry_frame()
            self.pack_procedure_frame()

            self.bind_summary_interaction()

        def pack_buttons(self):
            self.button_frame.pack(side=ctk.BOTTOM, fill=ctk.X)
            self.confirm_button.pack(side=ctk.RIGHT,
                                     anchor=ctk.E,
                                     padx=(0, 20),
                                     pady=(0, 20))

            self.cancel_button.pack(side=ctk.RIGHT,
                                    anchor=ctk.E,
                                    padx=(0, 20),
                                    pady=(0, 20))

        def create_buttons(self):
            self.button_frame = ctk.CTkFrame(master=self.dialog,
                                             fg_color=self.frame_color_1)
            self.confirm_button = ctk.CTkButton(master=self.button_frame,
                                                text="Conferma",
                                                fg_color=self.checkboxes_color,
                                                hover_color="#1265EA",
                                                font=self.elements_font,
                                                text_color="#FFFFFF",
                                                corner_radius=3,
                                                command=self.save_patient)

            self.cancel_button = ctk.CTkButton(master=self.button_frame,
                                               text="Annulla",
                                               fg_color=self.checkboxes_color,
                                               hover_color="#1265EA",
                                               font=self.elements_font,
                                               text_color="#FFFFFF",
                                               corner_radius=3,
                                               command=self.cancel)

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
                                               fg_color=self.frame_color_1,
                                               border_width=1,
                                               border_color="gray80")

            self.registry_label = ctk.CTkLabel(master=self.registry_frame,
                                               text="Informazioni paziente",
                                               font=self.section_font,
                                               text_color=self.labels_text_color)
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
            self.summary_outer_frame.pack(side=ctk.BOTTOM,
                                          fill=ctk.BOTH,
                                          padx=(20, 20),
                                          pady=(0, 20))
            self.summary_frame.pack(side=ctk.BOTTOM,
                                    fill=ctk.BOTH,
                                    pady=(0, 20))
            self.summary_registry_frame.pack(side=ctk.LEFT, fill=ctk.Y)
            self.summary_procedure_frame.pack(side=ctk.LEFT, fill=ctk.BOTH)

            self.summary_label.pack(side=ctk.TOP)

            self.pack_summary_entry(self.summary_name_entry)
            self.pack_summary_entry(self.summary_surname_entry)
            self.pack_summary_entry(self.summary_date_entry)
            self.pack_summary_entry(self.summary_anesthesia_entry)
            self.pack_summary_entry(self.summary_infections_entry)

            self.pack_summary_entry(self.summary_procedures_label,
                                    padx=(10, 0),
                                    fill=None)

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
                                                       fg_color=self.frame_color_2)

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
                                                         text_color=self.labels_text_color)

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
                                  label_side=ctk.LEFT,
                                  label_anchor=ctk.W,
                                  entry_side=ctk.RIGHT,
                                  entry_anchor=ctk.E)

        def pack_procedure_frame(self):
            self.procedures_frame.pack(side=ctk.RIGHT, fill=ctk.Y,
                                       padx=(10, 20),
                                       pady=(20, 20))
            self.procedures_label.pack(side=ctk.TOP,
                                       anchor=ctk.NW,
                                       padx=(20, 0),
                                       pady=(20, 0))
            self.procedures_label_searchbox.pack(side=ctk.TOP,
                                                 anchor=ctk.NW,
                                                 padx=(20, 0))

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
                                                 text_color=self.labels_text_color)

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
            for _ in range(0, self.checkbox_frames_number):
                row_frame = ctk.CTkFrame(master=self.procedures_frame,
                                         fg_color=self.frame_color_1)
                self.checkbox_frames.append(row_frame)

            for procedure in self.parent_view.PROCEDURES.items():
                procedure_variable = ctk.BooleanVar(False)
                self.procedure_variables[procedure[0]] = procedure_variable

            self.create_procedure_checkboxes(
                procedures=list(self.parent_view.PROCEDURES.items()))

        def cancel(self):
            self.dialog.destroy()

        def save_patient(self):
            new_row = self.extract_patient_row()

            active_table_index = self.parent_view.notebook.get()
            table = self.parent_view.tables[active_table_index]
            if self.mode == DialogMode.ADD:
                table.add_row(new_row)
            elif self.mode == DialogMode.EDIT:
                table.update_selected_row(new_row)

            self.dialog.destroy()

        # create a list representing a patient from the dialog's fields
        def extract_patient_row(self):
            patient_row = [""] * 6
            patient_row[0] = self.name_entry.entry_variable.get()
            patient_row[1] = self.surname_entry.entry_variable.get()
            patient_row[2] = self.procedures_as_string()
            patient_row[3] = self.anesthesia_checkbox.get()
            patient_row[4] = self.infections_checkbox.get()
            patient_row[5] = self.waiting_list_date_entry.entry_variable.get()

            return patient_row

        def procedures_as_string(self):
            r = ""
            first = True
            for procedure in self.procedure_checkboxes:
                if procedure.get() == 1:
                    if first:
                        r = r + procedure._text
                        first = False
                    else:
                        r = r + "|" + procedure._text
            return r

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

        self.screen_width = master.winfo_width()
        self.screen_height = master.winfo_height()

        self.toolbar_width = floor(self.screen_width * 0.15)
        self.summary_frame_width = floor(self.screen_width * 0.2)
        self.notebook_width = floor(self.screen_width * 0.65)

        self.notebook_height = floor(self.screen_height * 0.8)
        self.textbox_height = floor(self.screen_height * 0.4)

        self.dialogs = []
        self.planning_number = 0
        self.tables = dict()
        self.tables_dataframes = dict()
        self.tables_edit_buttons = dict()

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
                                          corner_radius=0,
                                          width=self.toolbar_width)
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

        # self.create_log_text_box()

        print(self.WELCOME_MESSAGE)

    def create_summary_entry(self, label_text, entry_text=""):
        return EntryWithLabel(master=self.summary_frame,
                              label_text=label_text,
                              entry_default_text=entry_text,
                              label_font=self.SOURCE_SANS_PRO_SMALL,
                              entry_font=self.SOURCE_SANS_PRO_SMALL,
                              frame_color=(self.WHITE,
                                           self.THEME2_COLOR2),
                              label_color=(self.WHITE,
                                           self.THEME2_COLOR2),
                              label_text_color=(self.BLACK,
                                                self.WHITE),
                              entry_color=(self.WHITE,
                                           self.THEME2_COLOR2),
                              entry_border_width=0,
                              entry_state=ctk.DISABLED,
                              label_side=ctk.LEFT,
                              label_anchor=ctk.W,
                              entry_side=ctk.RIGHT,
                              entry_anchor=ctk.E)

    def pack_summary_frame(self):
        self.summary_frame.pack(side=ctk.RIGHT,
                                fill=ctk.Y,
                                expand=False,
                                padx=(10, 20),
                                pady=(20, 20))

        self.summary_label.pack(side=ctk.TOP,
                                anchor=ctk.W,
                                padx=(20, 20),
                                pady=(20, 0))

        self.total_patients_summary_entry.pack(side=ctk.TOP,
                                               anchor=ctk.W,
                                               padx=(20, 20),
                                               pady=(0, 0))

        self.total_anesthesia_patients_summary_entry.pack(side=ctk.TOP,
                                                          anchor=ctk.W,
                                                          padx=(20, 20),
                                                          pady=(0, 0))

        self.total_infectious_patients_summary_entry.pack(side=ctk.TOP,
                                                          anchor=ctk.W,
                                                          padx=(20, 20),
                                                          pady=(0, 0))

        self.solver_summary_label.pack(side=ctk.TOP,
                                       anchor=ctk.W,
                                       padx=(20, 20),
                                       pady=(20, 0))

        self.gap_summary_label.pack(side=ctk.TOP,
                                    anchor=ctk.W,
                                    padx=(20, 20),
                                    pady=(0, 0))

        self.time_limit_summary_label.pack(side=ctk.TOP,
                                           anchor=ctk.W,
                                           padx=(20, 20),
                                           pady=(0, 0))
        
        self.robustness_summary_label.pack(side=ctk.TOP,
                                           anchor=ctk.W,
                                           padx=(20, 20),
                                           pady=(0, 0))
        
        self.solution_summary_label.pack(side=ctk.TOP,
                                       anchor=ctk.W,
                                       padx=(20, 20),
                                       pady=(20, 0))
        
        self.selected_patients_label.pack(side=ctk.TOP,
                                          anchor=ctk.W,
                                          padx=(20, 20),
                                          pady=(0, 0))
        
        self.anesthesia_selected_patients_label.pack(side=ctk.TOP,
                                                     anchor=ctk.W,
                                                     padx=(20, 20),
                                                     pady=(0, 0))
        
        self.infectious_selected_patients_label.pack(side=ctk.TOP,
                                                     anchor=ctk.W,
                                                     padx=(20, 20),
                                                     pady=(0, 0))

        self.delayed_selected_patients_label.pack(side=ctk.TOP,
                                                  anchor=ctk.W,
                                                  padx=(20, 20),
                                                  pady=(0, 0))

        self.average_OR1_utilization_label.pack(side=ctk.TOP,
                                                anchor=ctk.W,
                                                padx=(20, 20),
                                                pady=(0, 0))
        self.average_OR2_utilization_label.pack(side=ctk.TOP,
                                                anchor=ctk.W,
                                                padx=(20, 20),
                                                pady=(0, 0))
        self.average_OR3_utilization_label.pack(side=ctk.TOP,
                                                anchor=ctk.W,
                                                padx=(20, 20),
                                                pady=(0, 0))
        self.average_OR4_utilization_label.pack(side=ctk.TOP,
                                                anchor=ctk.W,
                                                padx=(20, 20),
                                                pady=(0, 0))

    def create_summary_frame(self):
        self.summary_frame = ctk.CTkFrame(master=self.right_frame,
                                          fg_color=(self.THEME1_COLOR2,
                                                    self.THEME2_COLOR2),
                                          corner_radius=3,
                                          width=self.summary_frame_width)

        self.summary_label = ctk.CTkLabel(master=self.summary_frame,
                                          fg_color=(self.THEME1_COLOR2,
                                                    self.THEME2_COLOR2),
                                          text="Riepilogo pazienti",
                                          font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)

        self.total_patients_summary_entry = self.create_summary_entry(label_text="Pazienti totali: ")
        self.total_anesthesia_patients_summary_entry = self.create_summary_entry(label_text="Pazienti con anestesia: ")
        self.total_infectious_patients_summary_entry = self.create_summary_entry(label_text="Pazienti con infezioni: ")

        self.solver_summary_label = ctk.CTkLabel(master=self.summary_frame,
                                                 fg_color=(self.THEME1_COLOR2,
                                                           self.THEME2_COLOR2),
                                                 text="Riepilogo impostazioni solver",
                                                 font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)

        self.gap_summary_label = self.create_summary_entry(label_text="Gap relativo tollerato (%): ")
        self.time_limit_summary_label = self.create_summary_entry(label_text="Timeout (s): ")
        self.robustness_summary_label = self.create_summary_entry(label_text="Parametro di robustezza: ")

        self.solution_summary_label = ctk.CTkLabel(master=self.summary_frame,
                                                 fg_color=(self.THEME1_COLOR2,
                                                           self.THEME2_COLOR2),
                                                 text="Riepilogo soluzione",
                                                 font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        
        self.selected_patients_label = self.create_summary_entry(label_text="Pazienti selezionati: ")
        self.anesthesia_selected_patients_label = self.create_summary_entry(label_text="Pazienti con anestesia selezionati: ")
        self.infectious_selected_patients_label = self.create_summary_entry(label_text="Pazienti con infezioni selezionati: ")
        self.delayed_selected_patients_label = self.create_summary_entry(label_text="Pazienti stimati in ritardo: ")
        self.average_OR1_utilization_label = self.create_summary_entry(label_text="Utilizzazione media Sala 1: ")
        self.average_OR2_utilization_label = self.create_summary_entry(label_text="Utilizzazione media Sala 2: ")
        self.average_OR3_utilization_label = self.create_summary_entry(label_text="Utilizzazione media Sala 3: ")
        self.average_OR4_utilization_label = self.create_summary_entry(label_text="Utilizzazione media Sala 4: ")

        self.pack_summary_frame()

    def create_toolbar(self):

        self.new_sheet_button = self.create_toolbar_button("resources/new.png",
                                                           "resources/new_w.png",
                                                           self.new_planning_callback,
                                                           "Nuova scheda"
                                                           )
        self.import_excel_button = self.create_toolbar_button("resources/xlsx.png",
                                                              "resources/xlsx_w.png",
                                                              self.import_callback,
                                                              text="Importa da file Excel",
                                                              )
        self.solver_config_button = self.create_toolbar_button("resources/solver_config.png",
                                                               "resources/solver_config_w.png",
                                                               self.config_solver,
                                                               text="Impostazioni solver"
                                                               )
        self.run_button = self.create_toolbar_button("resources/run.png",
                                                     "resources/run_w.png",
                                                     self.launch_solver,
                                                     text="Calcola pianificazione"
                                                     )
        self.stop_button = self.create_toolbar_button("resources/stop.png",
                                                      "resources/stop_w.png",
                                                      self.stop_solver,
                                                      text="Interrompi pianificazione"
                                                      )

        self.new_sheet_button.pack(side=ctk.TOP,
                                   expand=False,
                                   fill=ctk.X)
        self.import_excel_button.pack(side=ctk.TOP,
                                      expand=False,
                                      fill=ctk.X)
        self.solver_config_button.pack(side=ctk.TOP,
                                       expand=False,
                                       fill=ctk.X,
                                       pady=(50, 0))
        self.run_button.pack(side=ctk.TOP,
                             expand=False,
                             fill=ctk.X)
        self.stop_button.pack(side=ctk.TOP,
                              expand=False,
                              fill=ctk.X)

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
            for table in self.planning_tables.values():
                table.switch_theme("dark")
        else:
            self.theme = "light"
            ctk.set_appearance_mode("light")
            for table in self.tables.values():
                table.switch_theme("light")
            for table in self.planning_tables.values():
                table.switch_theme("light")

    def config_solver(self):
        pass

    def launch_solver(self):
        pass

    def stop_solver(self):
        pass

    def create_toolbar_button(self,
                              theme1_icon_path,
                              theme2_icon_path,
                              command,
                              text=None,
                              state=ctk.NORMAL
                              ):
        icon = ctk.CTkImage(Image.open(theme1_icon_path),
                            Image.open(theme2_icon_path))

        button = ctk.CTkButton(master=self.toolbar_frame,
                               image=icon,
                               command=command,
                               state=state,
                               fg_color=(self.THEME1_COLOR2,
                                         self.THEME2_COLOR2),
                               hover_color=(self.THEME1_COLOR1,
                                            self.THEME2_COLOR1),
                               corner_radius=0,
                               border_spacing=15,
                               text=text,
                               text_color=(self.BLACK, self.WHITE),
                               font=self.SOURCE_SANS_PRO_SMALL,
                               anchor=ctk.W
                               )
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
                                      checkboxes_color=self.CRAYON_BLUE,
                                      mode=DialogMode.EDIT)

    def close_active_tab(self):
        active_tab = self.notebook.get()
        self.notebook.delete(active_tab)

    def switch_view(self, button, label):
        selected_tab = self.notebook.get()
        table = self.tables[selected_tab]
        new_data_frame = None

        if label.cget("text") == "Lista pazienti":
            icon = ctk.CTkImage(Image.open("resources\patients_list.png"),
                                Image.open("resources\patients_list_w.png"))
            button.configure(text="Passa a lista pazienti", image=icon)
            label.configure(text="Pianificazione")

            data_dict = {"Colonna 1": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"],
                         "Colonna 2": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"],
                         "Colonna 3": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"],
                         "Colonna 4": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"],
                         "Colonna 5": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"],
                         "Colonna 6": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"],
                         "Colonna 7": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"], }

            new_data_frame = pd.DataFrame(data=data_dict)

        elif label.cget("text") == "Pianificazione":
            icon = ctk.CTkImage(Image.open("resources\\timetable.png"),
                                Image.open("resources\\timetable_w.png"))
            button.configure(text="Passa a pianificazione", image=icon)
            label.configure(text="Lista pazienti")
            new_data_frame = self.tables_dataframes[selected_tab][0]

        table.update_data_frame(new_data_frame)

    def show_interactive_planning(self):
        gantt_toplevel = ctk.CTkToplevel()
        main_browser_frame = MainBrowserFrame(gantt_toplevel)

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
                                       segmented_button_selected_hover_color=self.DARK_CRAYON_BLUE,
                                       corner_radius=3,
                                       width=self.notebook_width,
                                       height=self.notebook_height,
                                       command=self.update_patients_summary)
        self.notebook.pack(side=ctk.TOP,
                           expand=False,
                           fill=ctk.BOTH,
                           padx=(20, 10),
                           pady=(0, 20))

    def on_row_interaction(self, event):
        active_table_index = self.notebook.get()
        active_table = self.tables[active_table_index]
        selected_row_index = active_table.selected_row
        if selected_row_index is not None:
            self.tables_edit_buttons[active_table_index].configure(state=ctk.NORMAL)
        else:
            self.tables_edit_buttons[active_table_index].configure(state=ctk.DISABLED)

    def initialize_input_table(self, tab_name, data_frame):
        if data_frame is None:
            columns = self.PLANNING_HEADER
            data_frame = pandas.DataFrame(data=columns)

        tab = self.notebook.add(tab_name)
        table_upper_button_frame = ctk.CTkFrame(master=tab,
                                                fg_color=(self.WHITE, self.THEME2_COLOR2))

        close_tab_button = self.create_tabview_button(table_upper_button_frame,
                                                      "resources/delete.png",
                                                      "resources/delete_w.png",
                                                      self.close_active_tab,
                                                      text="Chiudi scheda"
                                                      )

        export_excel_button = self.create_tabview_button(table_upper_button_frame,
                                                         "resources/export.png",
                                                         "resources/export_w.png",
                                                         command=self.export_callback,
                                                         text="Esporta in file Excel"
                                                         )

        table_lower_button_frame = ctk.CTkFrame(master=tab,
                                                fg_color=(self.WHITE, self.THEME2_COLOR2))

        add_patient_button = self.create_tabview_button(table_lower_button_frame,
                                                        "resources/add-patient.png",
                                                        "resources/add-patient_w.png",
                                                        self.add_patient,
                                                        text="Aggiungi paziente"
                                                        )

        edit_patient_button = self.create_tabview_button(table_lower_button_frame,
                                                         "resources/edit.png",
                                                         "resources/edit_w.png",
                                                         self.edit_patient,
                                                         text="Modifica paziente",
                                                         state=ctk.DISABLED
                                                         )

        switch_view_button = self.create_tabview_button(table_lower_button_frame,
                                                        "resources/timetable.png",
                                                        "resources/timetable_w.png",
                                                        # self.switch_view,
                                                        text="Passa a pianificazione"
                                                        )

        interactive_planning_button = self.create_tabview_button(table_lower_button_frame,
                                                                 "resources/gantt.png",
                                                                 "resources/gantt_w.png",
                                                                 self.show_interactive_planning,
                                                                 text="Pianificazione interattiva"
                                                                 )

        patients_list_label = ctk.CTkLabel(master=table_lower_button_frame,
                                           text="Lista pazienti",
                                           font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)

        switch_view_button.configure(command=lambda button=switch_view_button,
                                     label=patients_list_label: self.switch_view(button, label))

        table = Table(master=tab,
                      on_select_command=self.on_row_interaction,
                      data_frame=data_frame,
                      row_height=40,
                      header_height=40,
                      fit_criterion=FitCriterion.FIT_HEADER_AND_COL_MAX_LENGTH,
                      row_separator_width=1,
                      pagination_size=20,
                      theme=self.theme,
                      even_row_colors=("#ffffff", self.THEME2_COLOR2),
                      height=100)

        self.tables[tab_name] = table
        self.tables_dataframes[tab_name] = (data_frame, None)

        self.tables_edit_buttons[tab_name] = edit_patient_button

        self.notebook.set(tab_name)
        self.update_patients_summary()

        # pack everything
        table_upper_button_frame.pack(side=ctk.TOP, fill=ctk.X)
        close_tab_button.pack(side=ctk.RIGHT,
                              expand=False,
                              padx=(2, 0))
        export_excel_button.pack(side=ctk.RIGHT,
                                 expand=False,
                                 padx=(2, 0))
        table_lower_button_frame.pack(side=ctk.TOP, fill=ctk.X)
        patients_list_label.pack(side=ctk.LEFT,
                                 expand=False,
                                 padx=(2, 0))
        add_patient_button.pack(side=ctk.RIGHT,
                                expand=False,
                                padx=(2, 0),
                                pady=(2, 2))
        edit_patient_button.pack(side=ctk.RIGHT,
                                 expand=False,
                                 padx=(2, 0),
                                 pady=(2, 2))
        interactive_planning_button.pack(side=ctk.RIGHT,
                                         expand=False,
                                         padx=(2, 0),
                                         pady=(2, 2))
        switch_view_button.pack(side=ctk.RIGHT,
                                expand=False,
                                padx=(2, 0),
                                pady=(2, 2))
        table.pack(side=ctk.TOP)

    def update_patients_summary(self):
        current_tab_name = self.notebook.get()
        current_data_frame = self.tables_dataframes[current_tab_name][0]

        total_patients = len(current_data_frame)
        anesthesia_patients = current_data_frame.query("Anestesia == True").shape[0]
        infectious_patients = current_data_frame.query("Infezioni == True").shape[0]

        self.total_patients_summary_entry.entry_variable.set(str(total_patients))
        self.total_anesthesia_patients_summary_entry.entry_variable.set(str(anesthesia_patients))
        self.total_infectious_patients_summary_entry.entry_variable.set(str(infectious_patients))

    def create_tabview_button(self,
                              table_button_frame,
                              theme1_icon_path,
                              theme2_icon_path,
                              command=None,
                              state=ctk.NORMAL,
                              text=""):
        icon = ctk.CTkImage(Image.open(theme1_icon_path),
                            Image.open(theme2_icon_path))

        button = ctk.CTkButton(master=table_button_frame,
                               image=icon,
                               command=command,
                               state=state,
                               fg_color=(self.WHITE, self.THEME2_COLOR2),
                               hover_color=(self.THEME1_COLOR1,
                                            self.THEME2_COLOR1),
                               corner_radius=3,
                               border_spacing=3,
                               border_color="gray50",
                               border_width=1,
                               text=text,
                               text_color=(self.BLACK, self.WHITE),
                               font=self.SOURCE_SANS_PRO_SMALL,
                               anchor=ctk.W,
                               width=170
                               )
        button.bind("<Enter>", command=self.hover_button, add="+")

        return button

    def create_log_text_box(self):
        self.text_box = ctk.CTkTextbox(master=self.right_frame,
                                       fg_color=(self.WHITE,
                                                 self.THEME2_COLOR2),
                                       text_color=(self.BLACK, self.WHITE),
                                       font=self.SOURCE_SANS_PRO_SMALL,
                                       corner_radius=3,
                                       height=self.textbox_height)
        self.text_box.pack(side=ctk.BOTTOM,
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
print((root.winfo_screenwidth(),
       root.winfo_screenheight()))
root.state("zoomed")

gui = GUI(root)
controller = Controller(model=None, view=gui)
gui.bind_controller(controller=controller)

# disable gpu in order to avoid the pesky scaling issue
cef.Initialize(settings={}, switches={'disable-gpu': ""})
root.mainloop()
cef.Shutdown()
