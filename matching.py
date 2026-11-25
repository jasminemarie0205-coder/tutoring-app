import pandas as pd
from datetime import date

MAX_STUDENTS = 2
MAX_SESSIONS = 4

students = pd.read_csv("data/students.csv")
tutors = pd.read_csv("data/tutors.csv")
matches = pd.read_csv("data/matches.csv")
sessions = pd.read_csv("data/sessions.csv")

def count_active_students(tutor_id):
    active = matches[(matches["tutor_id"] == tutor_id) & (matches["status"] == "active")]
    return len(active)


def tutor_has_open_slot(tutor_id):
    return count_active_students(tutor_id) < MAX_STUDENTS
    

def sessions_used(student_id):
    student_matches = matches[matches["student_id"] == student_id]

    match_ids = student_matches["match_id"]

    student_sessions = sessions[sessions["match_id"].isin(match_ids)]

    return len(student_sessions)



def sessions_left(student_id):
    return MAX_SESSIONS - sessions_used(student_id)

def blocked_tutors(student_id):
    switched = matches[(matches["student_id"] == student_id) & (matches["end_reason"] == "changed")]
    return switched["tutor_id"].tolist()




def find_tutor(student_id):
    if sessions_left(student_id) <= 0:
        return None
    blocked = blocked_tutors(student_id)
    for tutor_id in tutors["tutor_id"]:
        if tutor_has_open_slot(tutor_id) and tutor_id not in blocked:
            return tutor_id
    return None



def set_status(student_id, status):
    students.loc[students["student_id"] == student_id, "status"] = status

def make_match(student_id, tutor_id):
    new_id = f"M{len(matches) + 1}"
    today = str(date.today())
    matches.loc[len(matches)] = [new_id, student_id, tutor_id, "active", "", today]
    set_status(student_id, "matched")

def assign_student(student_id):
    tutor_id = find_tutor(student_id)
    if tutor_id is None:
        set_status(student_id, "waitlisted")
    else:
        make_match(student_id, tutor_id)
    return tutor_id


def fill_waitlist():
    waiting = students[students["status"] == "waitlisted"].sort_values("applied_date")
    for student_id in waiting["student_id"]:
        assign_student(student_id)
        
def end_match(student_id, reason):
    active = (matches["student_id"] == student_id) & (matches["status"] == "active")
    matches.loc[active, "status"] = "ended"
    matches.loc[active, "end_reason"] = reason
    
def request_new_tutor(student_id):
    end_match(student_id, "changed")
    assign_student(student_id)
    fill_waitlist()
    

def log_session(student_id):
    active = (matches["student_id"] == student_id) & (matches["status"] == "active")
    match_id = matches.loc[active, "match_id"].iloc[0]
    sessions.loc[len(sessions)] = [f"X{len(sessions) + 1}", match_id, str(date.today())]
    if sessions_left(student_id) == 0:
        end_match(student_id, "completed")
        set_status(student_id, "done")
        fill_waitlist()
        


def reject_student(student_id):
    set_status(student_id, "not_approved")
    

def save_all():
    students.to_csv("data/students.csv", index=False)
    tutors.to_csv("data/tutors.csv", index=False)
    matches.to_csv("data/matches.csv", index=False)
    sessions.to_csv("data/sessions.csv", index=False)

def total_open_slots():
    total = 0
    for tutor_id in tutors["tutor_id"]:
        total += MAX_STUDENTS - count_active_students(tutor_id)
    return total

def approve_student(student_id):
    fill_waitlist()
    assign_student(student_id)
    
    
if __name__ == "__main__":

    # Part 1: checks that don't change any data
    print(count_active_students("T1"))   # 2
    print(tutor_has_open_slot("T1"))     # False
    print(tutor_has_open_slot("T2"))     # True
    print(sessions_used("S1"))           # 2
    print(sessions_left("S4"))           # 0
    print(blocked_tutors("S5"))          # ['T4']
    print(find_tutor("S5"))              # T2
    print(find_tutor("S4"))              # None
    
        # Part 2: changes, in order (each step builds on the last)
    fill_waitlist()
    approve_student("S7")
    print(matches.tail(3))       # M6: S5 with T2, M7: S6 with T3, M8: S7 with T3
    request_new_tutor("S1")
    print(blocked_tutors("S1"))  # ['T1']
    print(sessions_left("S1"))   # 2
    print(matches.tail(1))       # M9: S1 with T4
    log_session("S1")
    log_session("S1")
    print(students[["student_id", "status"]])  # S1 and S4 done, S8 not_approved, rest matched