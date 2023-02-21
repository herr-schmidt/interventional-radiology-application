import sys
import re
from PIL import Image
from tkinter import filedialog
import pandas
import customtkinter as ctk
from bootstraptable import Table, FitCriterion
from controller import Controller
from math import ceil, floor
from planners import HeuristicLBBDPlanner, SolutionVisualizer
from util import StdoutRedirector, DialogMode
import pandas as pd
from embedded_browser import MainBrowserFrame, cef
import data
from datetime import datetime, timedelta


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
                 label_position=ctk.LEFT,
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

        if label_position == ctk.TOP:
            self.label.grid(row=0, column=0, sticky=ctk.NSEW)
            self.entry.grid(row=1, column=0, sticky=ctk.NSEW)
        else:
            self.label.grid(row=0, column=0, sticky=ctk.NSEW)
            self.entry.grid(row=0, column=1, sticky=ctk.NSEW)

    def destroy(self):
        self.entry.destroy()
        self.label.destroy()
        super().destroy()

class SliderWithEntry(ctk.CTkFrame):
    def __init__(self,
                 master,
                 starting_value,
                 ending_value,
                 frame_color,
                 entry_color,
                 slider_color,
                 slider_hover_color,
                 label_text,
                 label_color,
                 label_text_color,
                 label_text_font,
                 entry_border_width=0,
                 default_var_value=None,
                 measure_unit_suffix="",
                 entry_state=ctk.DISABLED,
                 var_type=ctk.DoubleVar,
                 **kwargs):
        super(SliderWithEntry, self).__init__(master=master,
                                             fg_color=frame_color,
                                             **kwargs)
        if not default_var_value:
            default_var_value = starting_value

        if measure_unit_suffix != "":
            self.measure_unit_suffix = " " + measure_unit_suffix
        else:
            self.measure_unit_suffix = measure_unit_suffix

        self.label = ctk.CTkLabel(master=self,
                                  text=label_text,
                                  text_color=label_text_color,
                                  fg_color=label_color,
                                  font=label_text_font)

        if var_type is ctk.IntVar:
            self.slider_var = ctk.IntVar()
        else:
            self.slider_var = ctk.DoubleVar()

        self.slider_var.set(default_var_value)
        self.slider = ctk.CTkSlider(master=self,
                                    from_=starting_value,
                                    to=ending_value,
                                    variable=self.slider_var,
                                    progress_color=slider_color,
                                    button_color=slider_color,
                                    button_hover_color=slider_hover_color,
                                    fg_color="gray80",
                                    command=self.update_entry)

        self.entry_var = ctk.StringVar()
        self.entry_var.set(str(self.slider_var.get()) + self.measure_unit_suffix)
        self.entry = ctk.CTkEntry(master=self,
                                  state=entry_state,
                                  textvariable=self.entry_var,
                                  border_width=entry_border_width,
                                  fg_color=entry_color,
                                  font=label_text_font,
                                  width=90)

        self.label.grid(row=0, column=0, sticky=ctk.W, padx=(10, 0), pady=(10, 0))
        self.slider.grid(row=1, column=0, padx=(10, 0), pady=(5, 5))
        self.entry.grid(row=1, column=1, padx=(10, 0), pady=(5, 5))
        
    def update_entry(self, event):
        new_value = self.slider_var.get()
        if type(self.slider_var) is ctk.DoubleVar:
            new_value = round(new_value, 2)
        
        self.entry_var.set(str(new_value) + self.measure_unit_suffix)

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
                       "Specialità richiesta": [],
                       "Reparto di provenienza": [],
                       "Prestazioni": [],
                       "Anestesia": [],
                       "Infezioni": [],
                       "Data inserimento in lista": [],
                       "MTBT (giorni)": []
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
    
    class Dialog():

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

    class OptimizationProgressDialog(Dialog):
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
            super().__init__(parent_view,
                             frame_color_1,
                             frame_color_2,
                             section_font,
                             elements_font,
                             labels_color,
                             labels_text_color,
                             entries_color,
                             checkboxes_color,
                             checkmarks_color)
            
            self.dialog.grab_set()
            progress_bar = ctk.CTkProgressBar(master=self.dialog, fg_color="gray90", progress_color=checkboxes_color, mode="indeterminate")
            progress_bar.pack()
            progress_bar.start()

        def destroy(self):
            self.dialog.destroy()


    class SolverOptionsDialog(Dialog):

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
            
            super().__init__(parent_view,
                             frame_color_1,
                             frame_color_2,
                             section_font,
                             elements_font,
                             labels_color,
                             labels_text_color,
                             entries_color,
                             checkboxes_color,
                             checkmarks_color)
            
            self.dialog.grab_set()
            self.create_frame()
            
        def create_frame(self):

            self.frame = ctk.CTkFrame(master=self.dialog, fg_color=self.frame_color_1, border_width=1, border_color="gray80")

            self.title_label = ctk.CTkLabel(master=self.frame, text="Impostazioni solver", font=self.parent_view.SOURCE_SANS_PRO_MEDIUM, fg_color=self.labels_color, text_color=self.labels_text_color)
            
            self.gap_slider = SliderWithEntry(master=self.frame,
                                              starting_value=0,
                                              ending_value=5,
                                              frame_color=self.frame_color_1,
                                              entry_color=self.frame_color_1,
                                              slider_color=self.parent_view.CRAYON_BLUE,
                                              slider_hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                              label_text="Gap relativo",
                                              label_color=self.labels_color,
                                              label_text_color=self.labels_text_color,
                                              label_text_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                              measure_unit_suffix="(%)")
            
            self.time_limit_slider = SliderWithEntry(master=self.frame,
                                              starting_value=600,
                                              ending_value=3600,
                                              frame_color=self.frame_color_1,
                                              entry_color=self.frame_color_1,
                                              slider_color=self.parent_view.CRAYON_BLUE,
                                              slider_hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                              label_text="Tempo limite",
                                              label_color=self.labels_color,
                                              label_text_color=self.labels_text_color,
                                              label_text_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                              measure_unit_suffix="(s)",
                                              var_type=ctk.IntVar)

            self.robustness_param_slider = SliderWithEntry(master=self.frame,
                                              starting_value=0,
                                              ending_value=10,
                                              frame_color=self.frame_color_1,
                                              entry_color=self.frame_color_1,
                                              slider_color=self.parent_view.CRAYON_BLUE,
                                              slider_hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                              label_text="Parametro di robustezza",
                                              label_color=self.labels_color,
                                              label_text_color=self.labels_text_color,
                                              label_text_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                              measure_unit_suffix="(pz./sala)",
                                              var_type=ctk.IntVar)

            self.operating_room_time_slider = SliderWithEntry(master=self.frame,
                                              starting_value=0,
                                              ending_value=480,
                                              frame_color=self.frame_color_1,
                                              entry_color=self.frame_color_1,
                                              slider_color=self.parent_view.CRAYON_BLUE,
                                              slider_hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                              label_text="Disponibilità sala operatoria",
                                              label_color=self.labels_color,
                                              label_text_color=self.labels_text_color,
                                              label_text_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                              measure_unit_suffix="(min/giorno)",
                                              var_type=ctk.IntVar)
            
            self.anesthetists_slider = SliderWithEntry(master=self.frame,
                                              starting_value=0,
                                              ending_value=5,
                                              frame_color=self.frame_color_1,
                                              entry_color=self.frame_color_1,
                                              slider_color=self.parent_view.CRAYON_BLUE,
                                              slider_hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                              label_text="Anestesisti disponibili",
                                              label_color=self.labels_color,
                                              label_text_color=self.labels_text_color,
                                              label_text_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                              measure_unit_suffix="(al giorno)",
                                              var_type=ctk.IntVar)
            
            self.anesthetists_time_slider = SliderWithEntry(master=self.frame,
                                              starting_value=0,
                                              ending_value=480,
                                              frame_color=self.frame_color_1,
                                              entry_color=self.frame_color_1,
                                              slider_color=self.parent_view.CRAYON_BLUE,
                                              slider_hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                              label_text="Disponibilità anestesista",
                                              label_color=self.labels_color,
                                              label_text_color=self.labels_text_color,
                                              label_text_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                              measure_unit_suffix="(min/giorno)",
                                              var_type=ctk.IntVar)
            
            self.confirm_button = ctk.CTkButton(master=self.dialog,
                                                text="Salva",
                                                font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                                fg_color=self.parent_view.CRAYON_BLUE,
                                                hover_color=self.parent_view.DARK_CRAYON_BLUE,
                                                text_color=self.parent_view.WHITE,
                                                command=self.save_solver_setup
                                                )

            self.frame.pack(side=ctk.TOP, padx=(20, 20), pady=(20, 20))
            self.title_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(10, 10), pady=(10, 0))
            self.gap_slider.pack(side=ctk.TOP, padx=(10, 10), pady=(0, 0))
            self.time_limit_slider.pack(side=ctk.TOP, padx=(10, 10), pady=(0, 0))
            self.robustness_param_slider.pack(side=ctk.TOP, padx=(10, 10), pady=(0, 0))
            self.operating_room_time_slider.pack(side=ctk.TOP, padx=(10, 10), pady=(0, 0))
            self.anesthetists_slider.pack(side=ctk.TOP, padx=(10, 10), pady=(0, 0))
            self.anesthetists_time_slider.pack(side=ctk.TOP, padx=(10, 10), pady=(0, 10))
            self.confirm_button.pack(side=ctk.TOP, anchor=ctk.E, padx=(0, 20), pady=(0, 20))
        
        def save_solver_setup(self):
            new_gap = self.gap_slider.slider_var.get()
            new_timelimit = self.time_limit_slider.slider_var.get()
            new_robustness_parameter = self.robustness_param_slider.slider_var.get()
            new_operating_room_time = self.operating_room_time_slider.slider_var.get()
            new_anesthetists = self.anesthetists_slider.slider_var.get()
            new_anesthetists_time = self.anesthetists_time_slider.slider_var.get()

            self.parent_view.solver_gap = round(float(new_gap), 2)
            self.parent_view.solver_time_limit = int(new_timelimit)
            self.parent_view.solver_robustness_param = int(new_robustness_parameter)
            self.parent_view.solver_operating_room_time = int(new_operating_room_time)
            self.parent_view.solver_anesthetists = int(new_anesthetists)
            self.parent_view.solver_anesthetists_time = int(new_anesthetists_time)

            self.parent_view.update_solver_summary()

            self.dialog.destroy()


    class InsertionDialog(Dialog):

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
            
            super().__init__(parent_view,
                             frame_color_1,
                             frame_color_2,
                             section_font,
                             elements_font,
                             labels_color,
                             labels_text_color,
                             entries_color,
                             checkboxes_color,
                             checkmarks_color)

            self.procedure_variables = {}
            self.procedure_checkboxes = []
            self.checkbox_frames = []
            self.checkboxes_per_row = 6
            self.checkbox_frames_number = ceil(len(self.parent_view.PROCEDURES.items()) / self.checkboxes_per_row)

            self.mode = mode

            self.summary_procedures_labels = {}
            self.procedure_label_row = 1

            self.dialog.grab_set()
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
            self.button_frame.grid(row=2, column=1, sticky=ctk.E, padx=(10, 10), pady=(0, 10))
            self.confirm_button.pack(side=ctk.RIGHT, anchor=ctk.E, padx=(5, 0))
            self.cancel_button.pack(side=ctk.RIGHT, anchor=ctk.E)

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
            self.registry_frame.grid(row=0, column=0, sticky=ctk.NSEW, padx=(10, 5), pady=(10, 10))

            self.registry_label.grid(row=0, column=0, sticky=ctk.NW, padx=(5, 10), pady=(5, 0))
            self.name_entry.grid(row=1, column=0, sticky=ctk.NSEW, padx=(10, 10), pady=(0, 0))
            self.surname_entry.grid(row=2, column=0, sticky=ctk.NSEW, padx=(10, 10), pady=(5, 0))
            self.waiting_list_date_entry.grid(row=3, column=0, sticky=ctk.NSEW, padx=(10, 10), pady=(5, 0))
            self.anesthesia_checkbox.grid(row=4, column=0, sticky=ctk.NSEW, padx=(10, 10), pady=(5, 0))
            self.infections_checkbox.grid(row=5, column=0, sticky=ctk.NSEW, padx=(10, 10), pady=(5, 5))

        def create_registry_entry(self, label_text):
            return EntryWithLabel(self.registry_frame,
                                  label_text=label_text,
                                  frame_color=self.frame_color_1,
                                  label_color=self.labels_color,
                                  label_text_color=self.labels_text_color,
                                  entry_color=self.frame_color_1,
                                  label_position=ctk.TOP)

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
            self.summary_frame.grid_columnconfigure(0, weight=1)
            self.summary_frame.grid(row=1, column=0, columnspan=2, sticky=ctk.NSEW, padx=(10, 10), pady=(0, 10))

            self.summary_label.grid(row=0, column=0, sticky=ctk.NSEW, padx=(5, 5), pady=(5, 5))

            self.summary_entries_frame.grid(row=1, column=0, sticky=ctk.NSEW, padx=(5, 5), pady=(5, 5))

            self.summary_name_entry.grid(row=1, column=0, sticky=ctk.W, padx=(5, 5))
            self.summary_surname_entry.grid(row=2, column=0, sticky=ctk.W, padx=(5, 5))
            self.summary_date_entry.grid(row=3, column=0, sticky=ctk.W, padx=(5, 5))
            self.summary_anesthesia_entry.grid(row=4, column=0, sticky=ctk.W, padx=(5, 5))
            self.summary_infections_entry.grid(row=5, column=0, sticky=ctk.W, padx=(5, 5), pady=(0, 5))

            self.summary_procedures_label.grid(row=1, column=1, sticky=ctk.W, padx=(10, 0))

        def create_summary_frame(self):
            self.summary_frame = ctk.CTkFrame(master=self.dialog,
                                              fg_color=self.frame_color_2)
            
            self.summary_label = ctk.CTkLabel(master=self.summary_frame,
                                              fg_color=self.frame_color_2,
                                              # corner_radius=0,
                                              text="Riepilogo paziente",
                                              font=self.parent_view.SOURCE_SANS_PRO_MEDIUM_BOLD)
            
            self.summary_entries_frame = ctk.CTkFrame(master=self.summary_frame,
                                                                fg_color=self.frame_color_2)

            self.summary_name_entry = self.create_summary_entry("Nome: ")
            self.summary_surname_entry = self.create_summary_entry("Cognome: ")
            self.summary_date_entry = self.create_summary_entry("Inserimento in lista: ")
            self.summary_anesthesia_entry = self.create_summary_entry("Anestesia: ", entry_text="No")
            self.summary_infections_entry = self.create_summary_entry("Infezioni in atto: ", entry_text="No")

            self.summary_procedures_label = ctk.CTkLabel(master=self.summary_entries_frame,
                                                         text="Procedure:",
                                                         font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                                         text_color=self.labels_text_color)

        def create_summary_entry(self, label_text, entry_text=""):
            return EntryWithLabel(master=self.summary_entries_frame,
                                  label_text=label_text,
                                  entry_default_text=entry_text,
                                  label_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                  entry_font=self.parent_view.SOURCE_SANS_PRO_SMALL,
                                  frame_color=self.frame_color_2,
                                  label_color=self.frame_color_2,
                                  label_text_color=self.labels_text_color,
                                  entry_color=self.frame_color_2,
                                  entry_border_width=0,
                                  entry_state=ctk.DISABLED)

        def pack_procedure_frame(self):
            self.procedures_frame.grid_columnconfigure(1, weight=1)
            self.procedures_frame.grid(row=0, column=1, sticky=ctk.NSEW, padx=(5, 10), pady=(10, 10))

            self.procedures_label.grid(row=0, column=0, sticky=ctk.NW, padx=(5, 5), pady=(5, 0))
            self.procedures_label_searchbox.grid(row=1, column=0, sticky=ctk.NSEW, padx=(5, 5), pady=(5, 0))

            self.procedures_checkboxes_frame.grid(row=4, column=0, sticky=ctk.NSEW, padx=(5, 5), pady=(5, 5))

            row = 0
            column = 0

            for checkbox in self.procedure_checkboxes:
                checkbox.grid(row=row, column=column % self.checkboxes_per_row, sticky=ctk.NSEW)
                column += 1
                if column % self.checkboxes_per_row == 0:
                    row += 1

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

            self.procedures_checkboxes_frame = ctk.CTkFrame(master=self.procedures_frame,
                                                            fg_color=self.frame_color_1,
                                                            border_width=0)

            self.initialize_procedure_checkboxes()

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
            if pattern == "":
                for procedure_checkbox in self.procedure_checkboxes:
                    procedure_checkbox.configure(bg_color="transparent")
            else:
                for procedure_checkbox in self.procedure_checkboxes:
                    checkbox_text = procedure_checkbox.cget("text")
                    if re.search(pattern.lower(), checkbox_text.lower()) is not None:
                        procedure_checkbox.configure(bg_color="#BBF2D3")
                    else:
                        procedure_checkbox.configure(bg_color="transparent")
        def pack_procedure_checkboxes(self):
            for checkbox in self.procedure_checkboxes:
                checkbox.pack(side=ctk.LEFT,
                              anchor=ctk.W,
                              padx=(0, 20))

        def initialize_procedure_checkboxes(self):
            procedures = list(self.parent_view.PROCEDURES.items())
            for procedure in procedures:
                procedure_variable = ctk.BooleanVar(False)
                self.procedure_variables[procedure[0]] = procedure_variable

                procedure_variable = self.procedure_variables[procedure[0]]
                procedure_checkbox = ctk.CTkCheckBox(master=self.procedures_checkboxes_frame,
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
                                                        command=lambda *_,
                                                        procedure_code=procedure[0],
                                                        procedure_variable=procedure_variable: self.update_summary_procedures(procedure_code, procedure_variable))
                self.procedure_checkboxes.append(procedure_checkbox)

        def update_summary_procedures(self, procedure_code, procedure_variable):
            if procedure_variable.get():
                text = "￮ " + procedure_code + " " + self.parent_view.PROCEDURES[procedure_code]
                summary_label = ctk.CTkLabel(master=self.summary_entries_frame,
                                             text=text)
                self.summary_procedures_labels[procedure_code] = summary_label
                row = len(self.summary_procedures_labels)
                summary_label.grid(row=row, column=2, sticky=ctk.W, padx=(5, 0))
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
        self.tables_dataframes = dict() # dict of length 2 lists: 0 -> patients list; 1 -> selected patients list
        self.runs_statistics = dict() # dict 

        self.tables_edit_buttons = dict() # keep track of "Edit patient" buttons (which we may wat to enable/disable)
        self.tables_switch_buttons = dict() # keep track of "Switch to planning" buttons (which we may wat to enable/disable)
        self.interactive_planning_buttons = dict() # keep track of "Switch to planning" buttons (which we may wat to enable/disable)

        self.solver_gap = 0
        self.solver_time_limit = 600
        self.solver_robustness_param = 2
        self.solver_anesthetists = 1
        self.solver_anesthetists_time = 270
        self.solver_operating_room_time = 270

        self.controller: Controller = None

        self.initializeUI()

    def bind_controller(self, controller):
        self.controller = controller

    def initializeUI(self):
        self.theme = "light"

        # expand all content vertically
        self.master.grid_rowconfigure(0, weight=1)

        # expand notebook horizontally column: take 1 of each free pixel
        self.master.grid_columnconfigure(1, weight=1)

        # left toolbar frame
        self.toolbar_frame = ctk.CTkFrame(master=self.master,
                                          fg_color=(self.THEME1_COLOR2,
                                                    self.THEME2_COLOR2),
                                          corner_radius=0,
                                          width=self.toolbar_width)
        
        self.toolbar_frame.grid(row=0, column=0, sticky=ctk.NSEW)

        self.create_toolbar()
        self.create_summary_frame()
        self.create_notebook()

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
                              entry_state=ctk.DISABLED)

    def pack_summary_frame(self):
        self.summary_frame.grid(row=0, column=2, sticky=ctk.NSEW, padx=(10, 10), pady=(18, 10))

        self.summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(20, 20), pady=(10, 0))
        self.total_patients_summary_entry.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.total_anesthesia_patients_summary_entry.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.total_infectious_patients_summary_entry.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))

        self.solver_summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(20, 20), pady=(10, 0))
        self.gap_summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.time_limit_summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.robustness_summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.operating_room_time_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.anesthetists_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.anesthetists_time_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))

        self.solution_summary_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(20, 20), pady=(10, 0))
        self.selected_patients_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.anesthesia_selected_patients_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.infectious_selected_patients_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.delayed_selected_patients_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.average_OR1_OR2_utilization_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.average_OR3_OR4_utilization_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.specialty_1_selected_ratio_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))
        self.specialty_2_selected_ratio_label.pack(side=ctk.TOP, anchor=ctk.W, padx=(30, 20), pady=(0, 0))


    def create_summary_frame(self):
        self.summary_frame = ctk.CTkFrame(master=self.master,
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

        self.gap_summary_label = self.create_summary_entry(label_text="Gap relativo tollerato: ", entry_text=str(self.solver_gap) + " (%)")
        self.time_limit_summary_label = self.create_summary_entry(label_text="Timeout: ", entry_text=str(self.solver_time_limit) + " (s)")
        self.robustness_summary_label = self.create_summary_entry(label_text="Parametro di robustezza: ", entry_text=str(self.solver_robustness_param) + " (pz./sala)")
        self.operating_room_time_label = self.create_summary_entry(label_text="Disponibilità sala operatoria: ", entry_text=str(self.solver_operating_room_time) + " (min/giorno)")
        self.anesthetists_label = self.create_summary_entry(label_text="Anestesisti disponibili: ", entry_text=str(self.solver_anesthetists) + " (per giorno)")
        self.anesthetists_time_label = self.create_summary_entry(label_text="Disponibilità anestesista: ", entry_text=str(self.solver_anesthetists_time) + " (min/giorno)")

        self.solution_summary_label = ctk.CTkLabel(master=self.summary_frame,
                                                 fg_color=(self.THEME1_COLOR2,
                                                           self.THEME2_COLOR2),
                                                 text="Riepilogo soluzione",
                                                 font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        
        self.selected_patients_label = self.create_summary_entry(label_text="Pazienti selezionati: ")
        self.anesthesia_selected_patients_label = self.create_summary_entry(label_text="Pazienti con anestesia selezionati: ")
        self.infectious_selected_patients_label = self.create_summary_entry(label_text="Pazienti con infezioni selezionati: ")
        self.delayed_selected_patients_label = self.create_summary_entry(label_text="Pazienti stimati in ritardo: ")
        self.average_OR1_OR2_utilization_label = self.create_summary_entry(label_text="Utilizzazione media Sale 1 e 2: ")
        self.average_OR3_OR4_utilization_label = self.create_summary_entry(label_text="Utilizzazione media Sale 3 e 4: ")
        self.specialty_1_selected_ratio_label = self.create_summary_entry(label_text="Pazienti di R.I. vascolare selezionati: ")
        self.specialty_2_selected_ratio_label = self.create_summary_entry(label_text="Pazienti di radiodiagnostica selezionati: ")

        self.pack_summary_frame()

    def create_toolbar(self):
        self.new_sheet_button = self.create_toolbar_button("resources/new.png",
                                                           "resources/new_w.png",
                                                           self.new_planning_callback,
                                                           "Nuova scheda"
                                                           )
        self.import_excel_button = self.create_toolbar_button("resources/import_excel.png",
                                                              "resources/import_excel_w.png",
                                                              self.import_callback,
                                                              text="Importa da file Excel",
                                                              )
        self.solver_config_button = self.create_toolbar_button("resources/solver_config.png",
                                                               "resources/solver_config_w.png",
                                                               self.config_solver,
                                                               text="Impostazioni solver"
                                                               )

        self.theme_mode_switch = ctk.CTkSwitch(master=self.toolbar_frame,
                                               text="Tema scuro",
                                               font=self.SOURCE_SANS_PRO_SMALL,
                                               command=self.switch_theme_mode,
                                               progress_color=self.DARK_CRAYON_BLUE)

        self.new_sheet_button.grid(row=0, column=0, sticky=ctk.NSEW)
        self.import_excel_button.grid(row=1, column=0, sticky=ctk.NSEW)
        self.solver_config_button.grid(row=2, column=0, sticky=ctk.NSEW)

        self.toolbar_frame.grid_rowconfigure(3, weight=1)
        self.theme_mode_switch.grid(row=3, column=0, sticky=ctk.S, pady=(0, 20))

    def switch_theme_mode(self):
        if self.theme == "light":
            self.theme = "dark"
            ctk.set_appearance_mode("dark")
            for table in self.tables.values():
                table.switch_theme("dark")
            self.theme_mode_switch.configure(text="Tema chiaro")
        else:
            self.theme = "light"
            ctk.set_appearance_mode("light")
            for table in self.tables.values():
                table.switch_theme("light")
            self.theme_mode_switch.configure(text="Tema scuro")

    def config_solver(self):
        dialog = self.SolverOptionsDialog(parent_view=self,
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
        return button

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
        
    def update_solver_summary(self):
        self.gap_summary_label.entry_variable.set(str(self.solver_gap) + " (%)")
        self.time_limit_summary_label.entry_variable.set(str(self.solver_time_limit) + " (s)")
        self.robustness_summary_label.entry_variable.set(str(self.solver_robustness_param) + " (pz./sala)")
        self.operating_room_time_label.entry_variable.set(str(self.solver_operating_room_time) + " (min/giorno)")
        self.anesthetists_label.entry_variable.set(str(self.solver_anesthetists) + " (al giorno)")
        self.anesthetists_time_label.entry_variable.set(str(self.solver_anesthetists_time) + " (min/giorno)")

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

            new_data_frame = self.tables_dataframes[selected_tab][1]

        elif label.cget("text") == "Pianificazione":
            icon = ctk.CTkImage(Image.open("resources\\timetable.png"),
                                Image.open("resources\\timetable_w.png"))
            button.configure(text="Passa a pianificazione", image=icon)
            label.configure(text="Lista pazienti")
            new_data_frame = self.tables_dataframes[selected_tab][0]

        table.update_data_frame(new_data_frame)

    def show_interactive_planning(self):
        gantt_toplevel = ctk.CTkToplevel()
        main_browser_frame = MainBrowserFrame(gantt_toplevel, "src/ex_load_files/" + self.notebook.get() + ".html")

    def solve(self):
        pass

    def import_callback(self):
        selected_file = filedialog.askopenfile(
            filetypes=[(self.EXCEL_FILE,
                        ["*.xlsx", "*.xls"]), ("Tutti i file", "*.*")])
        if selected_file is None:
            return

        controller.import_sheet(selected_file=selected_file)

    def launch_optimization(self):
        parameter_dict = self.initialize_data_from_table()
        optimization_dialog = self.OptimizationProgressDialog(parent_view=self,
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
        
        planner = HeuristicLBBDPlanner(timeLimit=self.solver_time_limit, gap=self.solver_gap, iterations_cap=10, solver="cbc")
        planner.solve_model(parameter_dict)
        run_info = planner.extract_run_info()
        solution = planner.extract_solution()
        if solution:
            sv = SolutionVisualizer()
            sv.plot_graph(solution, file_name=self.notebook.get())

        optimization_dialog.destroy()

        planning_dataframe = {"Nome": [],
                              "Cognome": [],
                              "Sala": [],
                              "Data operazione": [],
                              "Orario inizio": [],
                              "Ritardo": [],
                              "Anestesista": []
                              }

        if solution:
            for key in solution.keys():
                for patient in solution[key]:
                    planning_dataframe["Nome"].append(patient.id)
                    planning_dataframe["Cognome"].append(patient.id)
                    planning_dataframe["Sala"].append("S" + str(key[0]))

                    today = datetime.now().weekday()
                    days_to_monday = 7 - today
                    next_monday = datetime.now() + timedelta(days=days_to_monday)
                    target_date = next_monday + timedelta(days=key[1] - 1) # minus one since t = {1, 2, 3, 4, 5}
                    planning_dataframe["Data operazione"].append(target_date.date()) 

                    target_time = datetime(year=1970, month=1, day=1, hour=8, minute=0) + timedelta(minutes=patient.order)

                    planning_dataframe["Orario inizio"].append(target_time.time())

                    get_delay = lambda delay: "Sì" if delay else "No"
                    planning_dataframe["Ritardo"].append(get_delay(patient.delay))

                    get_anesthetist = lambda anesthetist: "A" + str(anesthetist) if anesthetist > 0 else ""
                    planning_dataframe["Anestesista"].append(get_anesthetist(patient.anesthetist))

        current_tab_name = self.notebook.get()
        self.tables_dataframes[current_tab_name][1] = pd.DataFrame(data=planning_dataframe)
        self.runs_statistics[current_tab_name] = run_info

        self.tables_switch_buttons[current_tab_name].configure(state=ctk.NORMAL)
        self.interactive_planning_buttons[current_tab_name].configure(state=ctk.NORMAL)

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
        self.notebook = ctk.CTkTabview(self.master,
                                       fg_color=(self.WHITE,
                                                 self.THEME2_COLOR2),
                                       segmented_button_selected_color=self.CRAYON_BLUE,
                                       segmented_button_selected_hover_color=self.DARK_CRAYON_BLUE,
                                       corner_radius=3,
                                       # width=self.notebook_width,
                                       # height=400,
                                       command=self.update_patients_summary)
        
        self.notebook.grid(row=0, column=1, sticky=ctk.NSEW, padx=(10, 0), pady=(0, 10))

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
        
        launch_optimization = self.create_tabview_button(table_upper_button_frame,
                                                         "resources/run.png",
                                                         "resources/run_w.png",
                                                         command=self.launch_optimization,
                                                         text="Calcola pianificazione"
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
                                                        text="Passa a pianificazione",
                                                        state=ctk.DISABLED
                                                        )

        interactive_planning_button = self.create_tabview_button(table_lower_button_frame,
                                                                 "resources/gantt.png",
                                                                 "resources/gantt_w.png",
                                                                 self.show_interactive_planning,
                                                                 text="Pianificazione interattiva",
                                                                 state=ctk.DISABLED
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
                      pagination_size=30,
                      theme=self.theme,
                      even_row_colors=("#ffffff", self.THEME2_COLOR2),
                      height=100)

        self.tables[tab_name] = table
        self.tables_dataframes[tab_name] = [data_frame, None]

        self.tables_edit_buttons[tab_name] = edit_patient_button
        self.tables_switch_buttons[tab_name] = switch_view_button
        self.interactive_planning_buttons[tab_name] = interactive_planning_button

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
        launch_optimization.pack(side=ctk.RIGHT,
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
        switch_view_button.pack(side=ctk.RIGHT,
                                expand=False,
                                padx=(2, 0),
                                pady=(2, 2))
        interactive_planning_button.pack(side=ctk.RIGHT,
                                         expand=False,
                                         padx=(2, 1),
                                         pady=(2, 2))
        table.pack(side=ctk.TOP)

    def list_to_dict(self, list):
        items = len(list)
        return {key: value for (key, value) in zip([i for i in range(1, items + 1)], list)}
    
    # we assume the same timespan for each room, on each day
    def generate_room_availability_table(self, operating_rooms, time_horizon, operating_room_time):
        return {(k, t): operating_room_time for k in range(1, operating_rooms + 1) for t in range(1, time_horizon + 1)}
    
    # we assume same availability for each anesthetist
    def generate_anesthetists_availability_table(self, anesthetists, time_horizon, anesthetists_availability):
        return {(a, t): anesthetists_availability for a in range(1, anesthetists + 1) for t in range(1, time_horizon + 1)}
    
    def generate_room_specialty_mapping(self, specialties, operating_rooms, time_horizon):
        table = {(j, k, t): 0 for j in range(1, specialties + 1) for k in range(1, operating_rooms + 1) for t in range(1, time_horizon + 1)}
        for key in table.keys():
            if key[0] == 1 and (key[1] in [1, 2]):
                table[key] = 1
            if key[0] == 2 and (key[1] in [3, 4]):
                table[key] = 1
        return table
    
    def generate_procedures_durations(self, procedures):
        procedures_durations = {}
        for item in procedures.items():
            services = item[1] # is a string of the form "69-8847|69-88495"
            services_key = frozenset(services.split("|"))
            procedures_durations[item[0]] = data.surgery_room_occupancy_mapping[services_key]

        return procedures_durations
    
    def generate_procedures_delays(self, origin_wards):
        procedures_delays = {}
        for item in origin_wards.items():
            origin_ward = item[1] # is a string, for now. Better translate such strings to some code
            procedures_delays[(1, item[0])] = data.ward_arrival_delay_mapping[origin_ward]

        return procedures_delays
    
    def compute_precedences(self, procedures, infection_flags):
        precedences = {}
        for item in procedures.items():
            services = item[1] # is a string of the form "69-8847|69-88495"
            services_key = frozenset(services.split("|"))
            if data.dirty_surgery_mapping[services_key] == 0 and infection_flags[item[0]] == 0:
                precedences[item[0]] = 1
            if data.dirty_surgery_mapping[services_key] == 1 and infection_flags[item[0]] == 0:
                precedences[item[0]] = 3
            if data.dirty_surgery_mapping[services_key] == 0 and infection_flags[item[0]] == 1:
                precedences[item[0]] = 5
            if data.dirty_surgery_mapping[services_key] == 1 and infection_flags[item[0]] == 1:
                precedences[item[0]] = 5 # for now...
        
        return precedences
    
    def compute_u_parameters(self, patients, precedences):
        u = {}
        for i1 in range(1, patients + 1):
            for i2 in range(1, patients + 1):
                u[(i1, i2)] = 0
                u[(i2, i1)] = 0

                if i1 == i2:
                    continue
                if precedences[i1] < precedences[i2]:
                    u[(i1, i2)] = 1
                if precedences[i2] < precedences[i1]:
                    u[(i2, i1)] = 1
        return u
    
    # compute priorities (r_i) with respect to planning day
    def compute_priorities(self, waiting_list_insertion_dates, MTBTs):
        today = pd.Timestamp(datetime.now())
        priorities = []

        for (insertion_date, mtbt) in zip(waiting_list_insertion_dates.values(), MTBTs.values()):
            delta = (today - insertion_date).days
            priorities.append(100 * delta / mtbt)

        return self.list_to_dict(priorities)

    # assume same robustness_parameter value for each (k, t) slot (single delay type q = 1)
    def compute_robustness_table(self, operating_rooms, time_horizon, robustness_parameter):
        return {(1, k, t): robustness_parameter for k in range(1, operating_rooms + 1) for t in range(1, time_horizon + 1)}

    # compute a dict containing parameters for the model, needed by the solver
    def initialize_data_from_table(self):
        active_tab_name = self.notebook.get()
        data_frame = self.tables_dataframes[active_tab_name][0]

        patients = len(data_frame)
        specialties_number = 2
        operating_rooms = 4
        time_horizon = 5
        max_operating_room_time = self.solver_operating_room_time

        patient_ids = self.list_to_dict([i for i in range(1, patients + 1)])
        anesthesia_flags = self.list_to_dict(data_frame.loc[:,"Anestesia"])
        infection_flags = self.list_to_dict(data_frame.loc[:,"Infezioni"])
        specialties = self.list_to_dict(data_frame.loc[:,"Specialità richiesta"])
        origin_wards = self.list_to_dict(data_frame.loc[:,"Reparto di provenienza"])
        procedures = self.list_to_dict(data_frame.loc[:,"Prestazioni"])
        waiting_list_insertion_dates = self.list_to_dict(data_frame.loc[:,"Data inserimento in lista"])
        MTBTs = self.list_to_dict(data_frame.loc[:,"MTBT (giorni)"])
        priorities = self.compute_priorities(waiting_list_insertion_dates, MTBTs)
        procedures_durations = self.generate_procedures_durations(procedures)
        procedures_delays = self.generate_procedures_delays(origin_wards)
        precedences = self.compute_precedences(procedures, infection_flags)
        robustness_parameters = self.compute_robustness_table(operating_rooms, time_horizon, self.solver_robustness_param)

        return {
            None: {
                'I': {None: patients},
                'J': {None: specialties_number},
                'K': {None: operating_rooms},
                'T': {None: time_horizon},
                'A': {None: self.solver_anesthetists},
                'M': {None: 7},
                'Q': {None: 1},
                's': self.generate_room_availability_table(operating_rooms, time_horizon, self.solver_operating_room_time),
                'An': self.generate_anesthetists_availability_table(self.solver_anesthetists, time_horizon, self.solver_anesthetists_time),
                'Gamma': robustness_parameters,
                'tau': self.generate_room_specialty_mapping(specialties_number, operating_rooms, time_horizon),
                'p': procedures_durations,
                'd': procedures_delays,
                'r': priorities,
                'a': anesthesia_flags,
                'c': infection_flags,
                'u': self.compute_u_parameters(patients, precedences),
                'patientId': patient_ids,
                'specialty': specialties,
                'precedence': precedences,
                'bigM': {
                    1: floor(max_operating_room_time/min([operating_time for operating_time in procedures_durations.values()])),
                    2: max_operating_room_time,
                    3: max_operating_room_time,
                    4: max_operating_room_time,
                    5: max_operating_room_time,
                    6: patients
                }
            }
        }

    def update_patients_summary(self):
        current_tab_name = self.notebook.get()
        current_data_frame = self.tables_dataframes[current_tab_name][0]

        total_patients = len(current_data_frame)
        anesthesia_patients = current_data_frame.query("Anestesia == True").shape[0]
        infectious_patients = current_data_frame.query("Infezioni == True").shape[0]

        self.total_patients_summary_entry.entry_variable.set(str(total_patients))
        self.total_anesthesia_patients_summary_entry.entry_variable.set(str(anesthesia_patients))
        self.total_infectious_patients_summary_entry.entry_variable.set(str(infectious_patients))

        planning_dataframe = self.tables_dataframes[current_tab_name][1]

        if planning_dataframe is not None:
            self.selected_patients_label.entry_variable.set(str(len(planning_dataframe)) + "(" + str(round(len(planning_dataframe) / len(current_data_frame), 2)) + "%)")
            anesthesia_selected_patients = len(planning_dataframe.query("Anestesista != ''"))

            run_info = self.runs_statistics[current_tab_name]
            self.average_OR1_OR2_utilization_label.entry_variable.set(str(round(run_info["specialty_1_OR_utilization"] * 100, 2)) + "%")
            self.average_OR3_OR4_utilization_label.entry_variable.set(str(round(run_info["specialty_2_OR_utilization"] * 100, 2)) + "%")
            self.specialty_1_selected_ratio_label.entry_variable.set(str(round(run_info["specialty_1_selection_ratio"] * 100, 2)) + "%")
            self.specialty_2_selected_ratio_label.entry_variable.set(str(round(run_info["specialty_2_selection_ratio"] * 100, 2)) + "%")

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

        return button


root = ctk.CTk()
ctk.set_appearance_mode("light")
root.title("Interventional Radiology Planner & Scheduler")
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),
              root.winfo_screenheight()))
root.state("zoomed")

gui = GUI(root)
controller = Controller(model=None, view=gui)
gui.bind_controller(controller=controller)

# disable gpu in order to avoid the pesky scaling issue
cef.Initialize(settings={}, switches={'disable-gpu': ""})
root.mainloop()
cef.Shutdown()
