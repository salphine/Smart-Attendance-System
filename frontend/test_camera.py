import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Camera Test", page_icon="??")
st.title("?? Camera Test")

st.markdown("This will test if your camera is working properly.")

# Test camera
img_file = st.camera_input("Take a test photo")

if img_file is not None:
    st.success("? Camera is working!")
    st.image(img_file, caption="Test Photo", use_column_width=True)
    
    # Convert to array
    bytes_data = img_file.getvalue()
    st.info(f"Image size: {len(bytes_data)} bytes")
else:
    st.info("Click 'Take a photo' to test your camera")

# Camera troubleshooting
with st.expander("Camera Troubleshooting"):
    st.markdown("""
    If camera doesn't work:
    1. Make sure no other app is using the camera
    2. Check Windows camera privacy settings
    3. Allow browser to access camera
    4. Update camera drivers
    """)

