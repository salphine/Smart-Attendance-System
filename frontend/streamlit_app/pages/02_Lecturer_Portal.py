import streamlit as st

st.set_page_config(
    page_title="Lecturer Portal",
    page_icon="👨‍🏫"
)

st.title("👨‍🏫 Lecturer Portal")
st.write("Lecturer portal is working!")

if st.button("Back to Home"):
    st.switch_page("Home.py")
