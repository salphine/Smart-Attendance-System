import streamlit as st

st.set_page_config(
    page_title="Student Portal",
    page_icon="👨‍🎓"
)

st.title("👨‍🎓 Student Portal")
st.write("Student portal is working!")

if st.button("Back to Home"):
    st.switch_page("Home.py")
