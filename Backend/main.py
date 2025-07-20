from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils import process_video_and_generate_report
import shutil
import os
import uuid

app = FastAPI()

# Allow Streamlit frontend to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to localhost or domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/evaluate/")
async def evaluate(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4().hex}.mp4"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    report = process_video_and_generate_report(temp_filename)

    os.remove(temp_filename)
    return {"report": report}
