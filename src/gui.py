import sys
import tkinter as tk
from PIL import Image
from tkinter import filedialog
import pandas
import customtkinter as ctk
from bootstraptable import Table, FitCriterion
from controller import Controller


class StdoutRedirector(object):

    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert("end", string)
        self.text_space.see("end")

    def flush(self):
        pass


class EntryWithLabel(ctk.CTkFrame):

    def __init__(self, master, frame_color, label_text, label_color, label_text_color, entry_color, entry_width=200, label_width=10, font=("Source Sans Pro", 14)):
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
                                  text_color=label_text_color,
                                  fg_color=label_color,
                                  font=font)

        self.label.pack(side=tk.TOP, anchor=tk.W)
        self.entry.pack(side=tk.LEFT)


class GUI(object):

    # constants
    EXCEL_FILE = "File Excel"
    ODF_FILE = "ODF Spreadsheet (.odf)"

    WHITE = "#FFFFFF"
    BLACK = "#000000"
    CRAYON_BLUE = "#287CFA"
    DARK_CRAYON_BLUE = "#1265EA"
    THEME1_COLOR1 = "#F4F4F8"
    THEME1_COLOR2 = "#DBDBDB"

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
    PROCEDURES = {"PROC1": "Procedura 1",
                  "PROC2": "Procedura 2",
                  "PROC3": "Procedura 3",
                  "PROC4": "Procedura 4",
                  "PROC5": "Procedura 5",
                  "PROC6": "Procedura 6",
                  "PROC7": "Procedura 7",
                  "PROC8": "Procedura 8",
                  "PROC9": "Procedura 9",
                  "PROC10": "Procedura 10"
                  }

    class InsertionDialog():

        def __init__(self,
                     parent_view,
                     frame_color,
                     section_font,
                     elements_font,
                     labels_color,
                     labels_text_color,
                     entries_color,
                     checkboxes_color,
                     checkmarks_color):

            self.parent_view = parent_view
            self.procedure_variables = {}

            self.frame_color = frame_color
            self.section_font = section_font
            self.elements_font = elements_font
            self.labels_color = labels_color
            self.labels_text_color = labels_text_color
            self.entries_color = entries_color
            self.checkboxes_color = checkboxes_color
            self.checkmarks_color = checkmarks_color

            self.dialog = ctk.CTkToplevel(fg_color=frame_color)

            general_information_frame = ctk.CTkFrame(master=self.dialog,
                                                     width=100,
                                                     height=100,
                                                     fg_color=frame_color)

            self.procedures_frame = ctk.CTkFrame(master=self.dialog,
                                                 fg_color=frame_color)

            registry_label = ctk.CTkLabel(master=general_information_frame,
                                          text="Anagrafica",
                                          font=section_font,
                                          text_color=labels_text_color,
                                          width=10)
            name_entry = EntryWithLabel(general_information_frame,
                                        label_text="Nome",
                                        frame_color=frame_color,
                                        label_color=labels_color,
                                        label_text_color=labels_text_color,
                                        entry_color=entries_color)
            surname_entry = EntryWithLabel(general_information_frame,
                                           label_text="Cognome",
                                           frame_color=frame_color,
                                           label_color=labels_color,
                                           label_text_color=labels_text_color,
                                           entry_color=entries_color)

            planning_label = ctk.CTkLabel(master=general_information_frame,
                                          text="Pianificazione",
                                          font=section_font,
                                          text_color=labels_text_color,
                                          width=14)
            waiting_list_date_entry = EntryWithLabel(
                general_information_frame,
                frame_color=frame_color,
                label_text="Inserimento in lista d'attesa",
                label_width=24,
                label_color=labels_color,
                label_text_color=labels_text_color,
                entry_color=entries_color)

            anesthesia = tk.BooleanVar(False)
            infections = tk.BooleanVar(False)

            anesthesia_checkbox = ctk.CTkCheckBox(master=general_information_frame,
                                                  variable=anesthesia,
                                                  border_color="gray90",
                                                  border_width=1,
                                                  hover=False,
                                                  text="Anestesia",
                                                  text_color=labels_text_color,
                                                  font=elements_font,
                                                  checkmark_color=checkmarks_color,
                                                  fg_color=checkboxes_color)
            infections_checkbox = ctk.CTkCheckBox(master=general_information_frame,
                                                  variable=infections,
                                                  border_color="gray90",
                                                  border_width=1,
                                                  hover=False,
                                                  text="Infezioni in atto",
                                                  text_color=labels_text_color,
                                                  font=elements_font,
                                                  checkmark_color=checkmarks_color,
                                                  fg_color=checkboxes_color)

            confirm_button = ctk.CTkButton(master=general_information_frame,
                                           text="Conferma",
                                           fg_color=checkboxes_color,
                                           hover_color="#1265EA",
                                           font=elements_font,
                                           text_color="#FFFFFF",
                                           width=100,
                                           corner_radius=3,
                                           command=self.save_patient)

            self.create_procedure_panel()

            general_information_frame.pack(side=tk.LEFT)
            self.procedures_frame.pack(side=tk.RIGHT, fill=tk.Y)

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
            confirm_button.pack(side=tk.BOTTOM,
                                anchor=tk.E,
                                padx=(0, 20),
                                pady=(0, 20))

        def create_procedure_panel(self):
            procedures_label = ctk.CTkLabel(master=self.procedures_frame,
                                            text="Procedure",
                                            font=self.section_font,
                                            text_color=self.labels_text_color,
                                            width=10)

            procedures_label.pack(side=tk.TOP, anchor=tk.NW)

            checkboxes_per_row = 4
            total_checkboxes = 0
            row_frame = ctk.CTkFrame(master=self.procedures_frame,
                                     fg_color=self.frame_color)
            for procedure in self.parent_view.PROCEDURES.items():
                procedure_variable = tk.BooleanVar(False)
                self.procedure_variables[procedure[0]] = procedure_variable
                procedure_checkbox = ctk.CTkCheckBox(master=row_frame,
                                                     variable=procedure_variable,
                                                     border_color="gray90",
                                                     border_width=1,
                                                     hover=False,
                                                     text=procedure[1],
                                                     text_color=self.labels_text_color,
                                                     font=self.elements_font,
                                                     checkmark_color=self.checkmarks_color,
                                                     fg_color=self.checkboxes_color)
                procedure_checkbox.pack(
                    side=tk.LEFT, anchor=tk.W, padx=(0, 20))
                total_checkboxes += 1

                if total_checkboxes % checkboxes_per_row == 0:
                    row_frame.pack(side=tk.TOP, padx=(20, 0), pady=(20, 20))
                    row_frame = ctk.CTkFrame(master=self.procedures_frame,
                                             fg_color=self.frame_color)

            row_frame.pack(side=tk.TOP, padx=(20, 20), pady=(20, 20), fill=tk.X)

        def save_patient(self):
            print("save!")

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
        self.toolbar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        # log output and footer
        self.right_frame = ctk.CTkFrame(master=self.master,
                                        fg_color=(self.THEME1_COLOR1,
                                                  self.THEME2_COLOR1),
                                        corner_radius=0)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_toolbar()
        self.create_summary_frame()
        self.create_notebook()
        self.create_log_text_box()

        print(self.WELCOME_MESSAGE)

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
                                     fg_color=(self.THEME1_COLOR2,
                                               self.THEME2_COLOR2),
                                     text="Riepilogo pazienti",
                                     font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        summary_label.pack(side=tk.TOP,
                           anchor=tk.W,
                           padx=(20, right_x_pad),
                           pady=(20, 0))

        total_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                            fg_color=(self.THEME1_COLOR2,
                                                      self.THEME2_COLOR2),
                                            text="Pazienti totali: ",
                                            font=self.SOURCE_SANS_PRO_SMALL)
        total_patients_label.pack(side=tk.TOP,
                                  anchor=tk.W,
                                  padx=(20, right_x_pad),
                                  pady=(0, 0))

        total_anesthesia_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                                       fg_color=(self.THEME1_COLOR2,
                                                                 self.THEME2_COLOR2),
                                                       text="Pazienti con anestesia: ",
                                                       font=self.SOURCE_SANS_PRO_SMALL)
        total_anesthesia_patients_label.pack(side=tk.TOP,
                                             anchor=tk.W,
                                             padx=(20, right_x_pad),
                                             pady=(0, 0))

        total_infectious_patients_label = ctk.CTkLabel(master=self.summary_frame,
                                                       fg_color=(self.THEME1_COLOR2,
                                                                 self.THEME2_COLOR2),
                                                       text="Pazienti con infezioni in atto: ",
                                                       font=self.SOURCE_SANS_PRO_SMALL)
        total_infectious_patients_label.pack(side=tk.TOP,
                                             anchor=tk.W,
                                             padx=(20, right_x_pad),
                                             pady=(0, 0))

        solver_label = ctk.CTkLabel(master=self.summary_frame,
                                    fg_color=(self.THEME1_COLOR2,
                                              self.THEME2_COLOR2),
                                    text="Riepilogo impostazioni solver",
                                    font=self.SOURCE_SANS_PRO_MEDIUM_BOLD)
        solver_label.pack(side=tk.TOP,
                          anchor=tk.W,
                          padx=(20, right_x_pad),
                          pady=(20, 0))

        gap_label = ctk.CTkLabel(master=self.summary_frame,
                                 fg_color=(self.THEME1_COLOR2,
                                           self.THEME2_COLOR2),
                                 text="Gap (%): ",
                                 font=self.SOURCE_SANS_PRO_SMALL)
        gap_label.pack(side=tk.TOP,
                       anchor=tk.W,
                       padx=(20, right_x_pad),
                       pady=(0, 0))
        time_limit_label = ctk.CTkLabel(master=self.summary_frame,
                                        fg_color=(self.THEME1_COLOR2,
                                                  self.THEME2_COLOR2),
                                        text="Timeout (s): ",
                                        font=self.SOURCE_SANS_PRO_SMALL)
        time_limit_label.pack(side=tk.TOP,
                              anchor=tk.W,
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
                                                           state=tk.DISABLED,
                                                           )

        self.create_toolbar_button("resources/add-patient.png",
                                   "resources/add-patient_w.png",
                                   self.add_patient,
                                   text="Aggiungi paziente",
                                   state=tk.NORMAL,
                                   )

        self.create_toolbar_button("resources/edit.png",
                                   "resources/edit_w.png",
                                   self.edit_patient,
                                   text="Modifica paziente selezionato",
                                   state=tk.NORMAL,
                                   )

        self.create_toolbar_button("resources/run.png",
                                   "resources/run_w.png",
                                   self.launch_solver,
                                   text="Calcola pianificazione",
                                   state=tk.NORMAL,
                                   )

        self.create_toolbar_button("resources/stop.png",
                                   "resources/stop_w.png",
                                   self.stop_solver,
                                   text="Interrompi pianificazione",
                                   state=tk.NORMAL,
                                   )

        self.theme_mode_switch = ctk.CTkSwitch(master=self.toolbar_frame,
                                               text="Modalità notturna",
                                               font=self.SOURCE_SANS_PRO_SMALL,
                                               command=self.switch_theme_mode,
                                               progress_color=self.DARK_CRAYON_BLUE)
        self.theme_mode_switch.pack(side=tk.BOTTOM, pady=(0, 20))

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
                              state=tk.NORMAL,
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
            anchor=tk.W
        )
        button.pack(side=tk.TOP, anchor=tk.W, expand=False,
                    fill=tk.X, padx=padx, pady=pady)
        button.bind("<Enter>", command=self.hover_button, add="+")

        return button

    def hover_button(self, event):
        print(event.widget)

    def add_patient(self):
        dialog = self.InsertionDialog(parent_view=self,
                                      frame_color=(self.WHITE,
                                                   self.THEME2_COLOR2),
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
                                      frame_color=(self.WHITE,
                                                   self.THEME2_COLOR2),
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
            self.close_tab_button.configure(state=tk.DISABLED)

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
        selected_filetype = tk.StringVar()
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
        self.notebook.pack(side=tk.TOP,
                           expand=True,
                           fill=tk.BOTH,
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
        self.close_tab_button.configure(state=tk.NORMAL)

    def create_log_text_box(self):
        self.text_box = ctk.CTkTextbox(master=self.right_frame,
                                       fg_color=(self.WHITE,
                                                 self.THEME2_COLOR2),
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
controller = Controller(model=None, view=gui)
gui.bind_controller(controller=controller)

root.mainloop()
