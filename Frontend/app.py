import streamlit as st
import requests
import os

st.title("🎥 Customer Service Evaluation App")

uploaded_file = st.file_uploader("Upload a video (.mp4)", type=["mp4"])

if uploaded_file:
    st.video(uploaded_file)

    if st.button("Evaluate"):
        with st.spinner("Sending video to evaluation server..."):
            files = {"file": uploaded_file.getvalue()}
            response = requests.post("http://localhost:8000/evaluate/", files={"file": uploaded_file})
            if response.status_code == 200:
                report = response.json()["report"]
                st.markdown(report)
            else:
                st.error("Evaluation failed.")
