import os
import streamlit as st
from dotenv import load_dotenv
import whisper
import tempfile
import json
import datetime
from openai import OpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Load Whisper model once
whisper_model = whisper.load_model("base")

# Streamlit page config
st.set_page_config(page_title="AI Fitness Trainer", page_icon="🏋️‍♂️")
st.title("🏋️‍♂️ AI Fitness Trainer")
st.caption("Chat or speak to get your personalized fitness and diet plan")

def transcribe_audio(file_path):
    result = whisper_model.transcribe(file_path)
    return result["text"]

def ask_model(prompt):
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": "You are a helpful fitness and nutrition expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def generate_prompt(data):
    return f"""
You are a professional fitness and diet trainer.
Generate a 7-day fitness and diet plan based on:

Age: {data['age']}
Weight: {data['weight']} kg
Height: {data['height']} cm
Injuries: {data['injuries']}
Goal: {data['goal']}
Level: {data['level']}
Workout Days: {data['days']}
Dietary Restrictions: {data['diet']}

Return a:
1. Workout plan (7 days)
2. Diet plan (7 days: breakfast, lunch, dinner, snacks)
"""

def save_history(user_data, response):
    history = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user_data,
        "response": response
    }
    if not os.path.exists("history.json"):
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump([history], f, indent=2, ensure_ascii=False)
    else:
        with open("history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        data.append(history)
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def load_history():
    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- User Input Form ---
st.subheader("✍️ Enter Your Fitness Details")
with st.form("fitness_form"):
    user_data = {
        'age': st.number_input("Age", min_value=10, max_value=100, value=25),
        'weight': st.number_input("Weight (kg)", min_value=30, max_value=200, value=70),
        'height': st.number_input("Height (cm)", min_value=100, max_value=250, value=170),
        'injuries': st.text_input("Injuries or Conditions", "None"),
        'goal': st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"]),
        'level': st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"]),
        'days': st.slider("Workout Days per Week", 1, 7, 4),
        'diet': st.text_input("Dietary Restrictions", "None")
    }
    submit = st.form_submit_button("Generate Plan")

if submit:
    with st.spinner("Generating your personalized fitness plan..."):
        prompt = generate_prompt(user_data)
        response = ask_model(prompt)
        st.markdown("## 🏋️‍♂️ Your Personalized Fitness Plan")
        st.markdown(response)
        save_history(user_data, response)

# --- Voice Input Section ---
st.markdown("---")
st.subheader("🎤 Ask via Voice (upload a .wav file)")
audio_file = st.file_uploader("Upload .wav voice input", type=["wav"])
if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name
    st.audio(tmp_path)
    transcript = transcribe_audio(tmp_path)
    st.write("**Transcript:**", transcript)
    with st.spinner("Model is responding..."):
        voice_response = ask_model(transcript)
        st.markdown("## 🔊 Response")
        st.markdown(voice_response)

# --- Show History ---
st.markdown("---")
if st.checkbox("📄 Show Previous Plans"):
    history = load_history()
    for item in reversed(history[-5:]):
        st.markdown(f"### ⏰ {item['timestamp']}")
        st.json(item['user'])
        st.markdown(item['response'])
