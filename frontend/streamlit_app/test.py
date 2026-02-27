import streamlit as st

st.set_page_config(page_title="Test", page_icon="✅")
st.title("✅ Test Page")
st.write("If you see this, the app is working!")

st.button("Test Button", key="test_btn")
st.success("Success!")
