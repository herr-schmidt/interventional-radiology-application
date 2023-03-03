from pandas import read_excel, Timestamp, DataFrame, ExcelWriter, Series
from datetime import datetime, timedelta
from math import floor
from planners import HeuristicLBBDPlanner, SolutionVisualizer
from const import IRConstants
import data


class Patient:

    def __init__(self, name, surname, services, anesthesia, infectious, list_insertion_date):
        self.name = name
        self.surname = surname
        self.services = services
        self.anesthesia = anesthesia
        self.infectious = infectious
        self.list_insertion_date = list_insertion_date


class InterventionalRadiologyModel():

    PATIENTS_LIST_HEADER = {IRConstants.PATIENT_NAME.value: [],
                            IRConstants.PATIENT_SURNAME.value: [],
                            IRConstants.PATIENT_SPECIALTY.value: [],
                            IRConstants.PATIENT_WARD.value: [],
                            IRConstants.PATIENT_PROCEDURES.value: [],
                            IRConstants.PATIENT_ANESTHESIA.value: [],
                            IRConstants.PATIENT_INFECTIONS.value: [],
                            IRConstants.PATIENT_INSERTION_DATE.value: [],
                            IRConstants.PATIENT_MTBT.value: []
                            }

    PLANNING_HEADER = {IRConstants.PATIENT_NAME.value: [],
                       IRConstants.PATIENT_SURNAME.value: [],
                       IRConstants.PATIENT_SURGERY_ROOM.value: [],
                       IRConstants.PATIENT_SURGERY_DAY.value: [],
                       IRConstants.PATIENT_SURGERY_TIME.value: [],
                       IRConstants.PATIENT_DELAY.value: [],
                       IRConstants.PATIENT_ANESTHETIST.value: [],
                       IRConstants.PATIENT_INFECTIONS.value: []
                       }

    DEFAULT_TAB_NAME = "Scheda "

    def __init__(self):
        self.solver_parameters = {IRConstants.SOLVER_GAP: 0.0,
                                  IRConstants.SOLVER_TIME_LIMIT: 600,
                                  IRConstants.SOLVER_ROBUSTNESS_PARAM: 2,
                                  IRConstants.SOLVER_OPERATING_ROOM_TIME: 270,
                                  IRConstants.SOLVER_ANESTHETISTS: 1,
                                  IRConstants.SOLVER_ANESTHETISTS_TIME: 270
                                  }

        self.patients_dataframes = dict()  # dict of length 2 lists: 0 -> patients list; 1 -> selected patients list
        self.runs_statistics = dict()

        self.planning_number = 0

    def update_solver_parameters(self, new_solver_parameters):
        self.solver_parameters = new_solver_parameters

    def get_new_tab_name(self):
        tab_name = self.DEFAULT_TAB_NAME + str(self.planning_number)
        self.planning_number += 1
        return tab_name

    def import_from_excel(self, tab_name, selected_file):
        patients_list_dataframe = read_excel(selected_file.name)
        planning_empty_dataframe = DataFrame(data=self.PLANNING_HEADER)
        self.patients_dataframes[tab_name] = [patients_list_dataframe, planning_empty_dataframe]

        # needed for display
        return patients_list_dataframe

    def compute_solution(self, tab_name):
        parameter_dict = self.initialize_solver_data(tab_name)
        planner = HeuristicLBBDPlanner(timeLimit=self.solver_parameters[IRConstants.SOLVER_TIME_LIMIT],
                                       gap=self.solver_parameters[IRConstants.SOLVER_GAP] / 100, iterations_cap=10, solver="cplex")
        planner.solve_model(parameter_dict)
        run_info = planner.extract_run_info()
        solution = planner.extract_solution()

        self.save_planning_graph(tab_name, solution)
        self.store_solution_as_dataframe(tab_name, solution, run_info)

    def save_planning_graph(self, tab_name, solution):
        if solution:
            sv = SolutionVisualizer()
            sv.plot_graph(solution, file_name=tab_name)

    def store_solution_as_dataframe(self, tab_name, solution, run_info):
        if solution:
            names = []
            surnames = []
            operating_rooms = []
            surgery_dates = []
            surgery_times = []
            delays = []
            anesthetists = []
            infections = []

            for key in solution.keys():
                for patient in solution[key]:
                    names.append(patient.id)
                    surnames.append(patient.id)
                    operating_rooms.append("S" + str(key[0]))

                    today = datetime.now().weekday()
                    days_to_monday = 7 - today
                    next_monday = datetime.now() + timedelta(days=days_to_monday)
                    target_date = next_monday + timedelta(days=key[1] - 1)  # minus one since t = {1, 2, 3, 4, 5}
                    surgery_dates.append(target_date.date())

                    target_time = datetime(year=1970, month=1, day=1, hour=8, minute=0) + timedelta(minutes=patient.order)
                    surgery_times.append(target_time.time())

                    def get_delay(delay): return "Sì" if delay else "No"
                    delays.append(get_delay(patient.delay))

                    def get_anesthetist(anesthetist): return "A" + str(anesthetist) if anesthetist > 0 else ""
                    anesthetists.append(get_anesthetist(patient.anesthetist))

                    def get_infection_info(infection): return "Sì" if infection else "No"
                    infections.append(get_infection_info(patient.infection))

            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_NAME.value] = Series(names)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_SURNAME.value] = Series(surnames)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_SURGERY_ROOM.value] = Series(operating_rooms)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_SURGERY_DAY.value] = Series(surgery_dates)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_SURGERY_TIME.value] = Series(surgery_times)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_DELAY.value] = Series(delays)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_ANESTHETIST.value] = Series(anesthetists)
            self.patients_dataframes[tab_name][1][IRConstants.PATIENT_INFECTIONS.value] = Series(infections)

            self.runs_statistics[tab_name] = run_info

    def initialize_solver_data(self, tab_name):
        data_frame = self.patients_dataframes[tab_name][0]

        patients = len(data_frame)
        specialties_number = 2
        operating_rooms = 4
        time_horizon = 5
        max_operating_room_time = self.solver_parameters[IRConstants.SOLVER_OPERATING_ROOM_TIME]

        patient_ids = self.list_to_dict([i for i in range(1, patients + 1)])
        anesthesia_flags = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_ANESTHESIA.value])
        infection_flags = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_INFECTIONS.value])
        specialties = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_SPECIALTY.value])
        origin_wards = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_WARD.value])
        procedures = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_PROCEDURES.value])
        waiting_list_insertion_dates = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_INSERTION_DATE.value])
        mtbt_list = self.list_to_dict(data_frame.loc[:, IRConstants.PATIENT_MTBT.value])
        priorities = self.compute_priorities(waiting_list_insertion_dates, mtbt_list)
        procedures_durations = self.generate_procedures_durations(procedures)
        procedures_delays = self.generate_procedures_delays(origin_wards)
        precedences = self.compute_precedences(procedures, infection_flags)
        robustness_parameters = self.compute_robustness_table(operating_rooms, time_horizon)

        return {
            None: {
                'I': {None: patients},
                'J': {None: specialties_number},
                'K': {None: operating_rooms},
                'T': {None: time_horizon},
                'A': {None: self.solver_parameters[IRConstants.SOLVER_ANESTHETISTS]},
                'M': {None: 7},
                'Q': {None: 1},
                's': self.generate_room_availability_table(operating_rooms, time_horizon),
                'An': self.generate_anesthetists_availability_table(time_horizon),
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
                    1: floor(max_operating_room_time / min([operating_time for operating_time in procedures_durations.values()])),
                    2: max_operating_room_time,
                    3: max_operating_room_time,
                    4: max_operating_room_time,
                    5: max_operating_room_time,
                    6: patients
                }
            }
        }

    def list_to_dict(self, list):
        items = len(list)
        return {key: value for (key, value) in zip([i for i in range(1, items + 1)], list)}

    # we assume the same timespan for each room, on each day
    def generate_room_availability_table(self, operating_rooms, time_horizon):
        return {(k, t): self.solver_parameters[IRConstants.SOLVER_OPERATING_ROOM_TIME] for k in range(1, operating_rooms + 1) for t in range(1, time_horizon + 1)}

    # we assume same availability for each anesthetist
    def generate_anesthetists_availability_table(self, time_horizon):
        return {(a, t): self.solver_parameters[IRConstants.SOLVER_ANESTHETISTS_TIME] for a in range(1, self.solver_parameters[IRConstants.SOLVER_ANESTHETISTS] + 1) for t in range(1, time_horizon + 1)}

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
            services = item[1]  # is a string of the form "69-8847|69-88495"
            services_key = frozenset(services.split("|"))
            procedures_durations[item[0]] = data.surgery_room_occupancy_mapping[services_key]

        return procedures_durations

    def generate_procedures_delays(self, origin_wards):
        procedures_delays = {}
        for item in origin_wards.items():
            origin_ward = item[1]  # is a string, for now. Better translate such strings to some code
            procedures_delays[(1, item[0])] = data.ward_arrival_delay_mapping[origin_ward]

        return procedures_delays

    def compute_precedences(self, procedures, infection_flags):
        precedences = {}
        for item in procedures.items():
            services = item[1]  # is a string of the form "69-8847|69-88495"
            services_key = frozenset(services.split("|"))
            if data.dirty_surgery_mapping[services_key] == 0 and infection_flags[item[0]] == 0:
                precedences[item[0]] = 1
            if data.dirty_surgery_mapping[services_key] == 1 and infection_flags[item[0]] == 0:
                precedences[item[0]] = 3
            if data.dirty_surgery_mapping[services_key] == 0 and infection_flags[item[0]] == 1:
                precedences[item[0]] = 5
            if data.dirty_surgery_mapping[services_key] == 1 and infection_flags[item[0]] == 1:
                precedences[item[0]] = 5  # for now...

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
    def compute_priorities(self, waiting_list_insertion_dates, mtbt_list):
        today = Timestamp(datetime.now())
        priorities = []

        for (insertion_date, mtbt) in zip(waiting_list_insertion_dates.values(), mtbt_list.values()):
            delta = (today - insertion_date).days
            priorities.append(100 * delta / mtbt)

        return self.list_to_dict(priorities)

    # assume same robustness_parameter value for each (k, t) slot (single delay type q = 1)
    def compute_robustness_table(self, operating_rooms, time_horizon):
        return {(1, k, t): self.solver_parameters[IRConstants.SOLVER_ROBUSTNESS_PARAM] for k in range(1, operating_rooms + 1) for t in range(1, time_horizon + 1)}

    def compute_solution_summary(self, tab_name):
        current_data_frame = self.patients_dataframes[tab_name][0]

        total_patients = len(current_data_frame)
        anesthesia_patients = current_data_frame.query(str(IRConstants.PATIENT_ANESTHESIA.value) + " == True").shape[0]
        infectious_patients = current_data_frame.query(str(IRConstants.PATIENT_INFECTIONS.value) + " == True").shape[0]

        planning_dataframe = self.patients_dataframes[tab_name][1]

        selected_patients = "N/A"
        anesthesia_selected_patients = "N/A"
        infectious_selected_patients = "N/A"
        delayed_selected_patients = "N/A"
        average_OR1_OR2_utilization = "N/A"
        average_OR3_OR4_utilization = "N/A"
        specialty_1_selected_ratio = "N/A"
        specialty_2_selected_ratio = "N/A"

        if not planning_dataframe.empty:
            selected_patients = (str(len(planning_dataframe))
                                 + " ("
                                 + str(round(len(planning_dataframe) / len(current_data_frame) * 100, 2))
                                 + "%)"
                                 )

            anesthesia_selected_patients = str(len(planning_dataframe.query(IRConstants.PATIENT_ANESTHETIST.value + " != ''")))
            infectious_selected_patients = str(len(planning_dataframe.query(IRConstants.PATIENT_INFECTIONS.value + " == 'Sì'")))
            delayed_selected_patients = str(len(planning_dataframe.query(IRConstants.PATIENT_DELAY.value + " == 'Sì'")))

            run_info = self.runs_statistics[tab_name]
            average_OR1_OR2_utilization = str(round(run_info["specialty_1_OR_utilization"] * 100, 2)) + "%"
            average_OR3_OR4_utilization = str(round(run_info["specialty_2_OR_utilization"] * 100, 2)) + "%"
            specialty_1_selected_ratio = str(round(run_info["specialty_1_selection_ratio"] * 100, 2)) + "%"
            specialty_2_selected_ratio = str(round(run_info["specialty_2_selection_ratio"] * 100, 2)) + "%"

        return {IRConstants.TOTAL_PATIENTS: total_patients,
                IRConstants.ANESTHESIA_PATIENTS: anesthesia_patients,
                IRConstants.INFECTIOUS_PATIENTS: infectious_patients,
                IRConstants.SELECTED_PATIENTS: selected_patients,
                IRConstants.ANESTHESIA_SELECTED_PATIENTS: anesthesia_selected_patients,
                IRConstants.INFECTIOUS_SELECTED_PATIENTS: infectious_selected_patients,
                IRConstants.DELAYED_SELECTED_PATIENTS: delayed_selected_patients,
                IRConstants.AVERAGE_OR1_OR2_UTILIZATION: average_OR1_OR2_utilization,
                IRConstants.AVERAGE_OR3_OR4_UTILIZATION: average_OR3_OR4_utilization,
                IRConstants.SPECIALTY_1_SELECTION_RATIO: specialty_1_selected_ratio,
                IRConstants.SPECIALTY_2_SELECTION_RATIO: specialty_2_selected_ratio
                }

    def create_empty_dataframe(self, tab_name):
        empty_patients_list_dataframe = DataFrame(data=self.PATIENTS_LIST_HEADER)
        empty_planning_dataframe = DataFrame(data=self.PLANNING_HEADER)
        self.patients_dataframes[tab_name] = [empty_patients_list_dataframe, empty_planning_dataframe]

        # needed for display
        return empty_patients_list_dataframe

    def get_patients_dataframe(self, tab_name):
        return self.patients_dataframes[tab_name][0]

    def get_planning_dataframe(self, tab_name):
        return self.patients_dataframes[tab_name][1]

    def get_solver_parameters(self):
        return self.solver_parameters

    def export_to_excel(self, tab_name, file_name):
        writer = ExcelWriter(file_name, engine="xlsxwriter")

        dataframe = self.patients_dataframes[tab_name]

        dataframe[0].to_excel(writer,
                              sheet_name="Lista pazienti",
                              header=list(dataframe[0].columns),
                              index=False)  # avoid writing a column of indices)
        dataframe[1].to_excel(writer,
                              sheet_name="Pianificazione",
                              header=list(dataframe[1].columns),
                              index=False)  # avoid writing a column of indices)

        writer.close()
