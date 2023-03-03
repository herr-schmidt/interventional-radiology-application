from enum import Enum


class IRConstants(Enum):
    SOLVER_GAP = "solver_gap",
    SOLVER_TIME_LIMIT = "solver_time_limit",
    SOLVER_ROBUSTNESS_PARAM = "solver_robustness_param",
    SOLVER_OPERATING_ROOM_TIME = "solver_operating_room_time",
    SOLVER_ANESTHETISTS = "solver_anesthetists",
    SOLVER_ANESTHETISTS_TIME = "solver_anesthetists_time"

    PATIENT_NAME = "Nome"
    PATIENT_SURNAME = "Cognome"
    PATIENT_SPECIALTY = "Specialità richiesta"
    PATIENT_WARD = "Reparto di provenienza"
    PATIENT_PROCEDURES = "Prestazioni"
    PATIENT_ANESTHESIA = "Anestesia"
    PATIENT_INFECTIONS = "Infezioni"
    PATIENT_INSERTION_DATE = "Data inserimento in lista"
    PATIENT_MTBT = "MTBT (giorni)"

    PATIENT_SURGERY_ROOM = "Sala"
    PATIENT_SURGERY_DAY = "Data operazione"
    PATIENT_SURGERY_TIME = "Orario inizio"
    PATIENT_DELAY = "Ritardo"
    PATIENT_ANESTHETIST = "Anestesista"

    TOTAL_PATIENTS = "total_patients"
    ANESTHESIA_PATIENTS = "anesthesia_patients"
    INFECTIOUS_PATIENTS = "infectious_patients"
    SELECTED_PATIENTS = "selected_patients"
    ANESTHESIA_SELECTED_PATIENTS = "anesthesia_selected_patients"
    INFECTIOUS_SELECTED_PATIENTS = "infectious_selected_patients"
    DELAYED_SELECTED_PATIENTS = "delayed_selected_patients"
    AVERAGE_OR1_OR2_UTILIZATION = "average_OR1_OR2_utilization"
    AVERAGE_OR3_OR4_UTILIZATION = "average_OR3_OR4_utilization"
    SPECIALTY_1_SELECTION_RATIO = "specialty_1_selected_ratio"
    SPECIALTY_2_SELECTION_RATIO = "specialty_2_selected_ratio"
