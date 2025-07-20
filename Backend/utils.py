import whisper
from moviepy.editor import VideoFileClip
import cv2
import openai
import base64



import os
from dotenv import load_dotenv

# Absolute path to .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
print("Loading .env from:", env_path)
load_dotenv(dotenv_path=env_path)

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")



def extract_audio(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec="pcm_s16le")
    return audio_path

def extract_frames(video_path, output_dir="frames", max_frames=3):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    saved = 0
    count = 0
    paths = []
    while cap.isOpened() and saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if count % (fps * 2) == 0:
            path = os.path.join(output_dir, f"frame_{saved}.jpg")
            cv2.imwrite(path, frame)
            paths.append(path)
            saved += 1
        count += 1
    cap.release()
    return paths

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def process_video_and_generate_report(video_path):
    audio_path = extract_audio(video_path)
    frames = extract_frames(video_path)
    transcript = transcribe_audio(audio_path)

    evaluation_prompt = f"""
You are a customer service evaluator. Analyze the representative's behavior based on facial expressions, tone of voice, and verbal content.

### Transcript:
{transcript}

Please consider:
- Emotional Intelligence
- Tone & Delivery
- Facial Expressions & Body Language
- Verbal Content Quality
- Overall Professionalism

Format your analysis in markdown as:

### Evaluation Summary

**1. Emotional Intelligence:**  
- ...

**2. Tone & Delivery:**  
- ...

**3. Facial Expressions & Body Language:**  
- ...

**4. Verbal Content Quality:**  
- ...

**5. Overall Impression & Rating (1–10):**  
- ...

**Suggestions for Improvement:**  
- ...
    """

    images = []
    for path in frames:
        with open(path, "rb") as img:
            img_b64 = base64.b64encode(img.read()).decode()
            images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in communication evaluation."},
            {"role": "user", "content": [{"type": "text", "text": evaluation_prompt}] + images}
        ]
    )

    return response.choices[0].message.content
