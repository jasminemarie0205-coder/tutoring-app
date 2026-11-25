import streamlit as st
import matching as m

st.title("Tutoring staff dashboard")


# ----- Quick counts at the top -----
def count_status(status):
    return len(m.students[m.students["status"] == status])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pending", count_status("pending"))
col2.metric("Waitlisted", count_status("waitlisted"))
col3.metric("Matched", count_status("matched"))
col4.metric("Open tutor slots", m.total_open_slots())


# ----- Applications waiting for review -----
st.subheader("Pending applications")
pending = m.students[m.students["status"] == "pending"]

if len(pending) == 0:
    st.info("No applications to review. New ones will show up here.")

for _, student in pending.iterrows():
    student_id = student["student_id"]

    with st.container(border=True):
        st.write(f"**{student['name']}** (Section {student['section']})")
        st.write(f"Needs help with: {student['struggling_with'].replace(';', ', ')}")
        st.write(f"Classes missed: {student['classes_missed']}")

        approve_col, decline_col = st.columns(2)

        if approve_col.button("Approve", key=f"approve_{student_id}"):
            m.approve_student(student_id)
            m.save_all()
            st.rerun()

        if decline_col.button("Decline", key=f"decline_{student_id}"):
            m.reject_student(student_id)
            m.save_all()
            st.rerun()


# ----- Waitlist, in the order students will be matched -----
st.subheader("Waitlist")
waitlist = m.students[m.students["status"] == "waitlisted"].sort_values("applied_date")

if len(waitlist) == 0:
    st.info("Nobody is waiting. Every approved student has a tutor.")
else:
    st.dataframe(waitlist[["name", "section", "applied_date"]], hide_index=True)
