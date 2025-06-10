import os
import streamlit as st
from dotenv import load_dotenv
import json
import datetime
import google.generativeai as genai  # Gemini

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# Streamlit config
st.set_page_config(page_title="AI Fitness Trainer", page_icon="🏋️‍♂️", layout="wide")

# --- CSS Styling ---
st.markdown("""
<style>
.stApp {
    background: url('https://images.unsplash.com/photo-1584467735871-bfb7a1a38d66?auto=format&fit=crop&w=1470&q=80') no-repeat center center fixed;
    background-size: cover;
}
h1, h2, h3 {
    color: #FF7043;
    text-shadow: 1px 1px 2px black;
}
.boxed {
    background-color: rgba(33,33,33,0.8);
    padding: 20px;
    border-radius: 10px;
    color: #f1f1f1;
    margin-bottom: 20px;
    font-family: 'Segoe UI', sans-serif;
}
.chat-container {
    background: #212121;
    border-radius: 8px;
    padding: 15px;
    max-height: 300px;
    overflow-y: auto;
    color: #e0e0e0;
}
.chat-user { color: #4caf50; font-weight: bold; }
.chat-bot { color: #ff7043; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏋️‍♂️ AI Fitness Trainer")
st.caption("Get personalized fitness & diet plans with exercise demos and AI chat.")

# --- Functions ---
def ask_model(prompt):
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

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
            json.dump([history], f, indent=2)
    else:
        with open("history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        data.append(history)
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

def load_history():
    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- User Form ---
st.subheader("✍️ Enter Your Fitness Details")
with st.form("fitness_form"):
    user_data = {
        'age': st.number_input("Age", 10, 100, 25),
        'weight': st.number_input("Weight (kg)", 30, 200, 70),
        'height': st.number_input("Height (cm)", 100, 250, 170),
        'injuries': st.text_input("Injuries or Conditions", "None"),
        'goal': st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"]),
        'level': st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"]),
        'days': st.slider("Workout Days per Week", 1, 7, 4),
        'diet': st.text_input("Dietary Restrictions", "None")
    }
    submit = st.form_submit_button("Generate Plan")

plan_text = ""
if submit:
    with st.spinner("Generating your personalized fitness plan..."):
        prompt = generate_prompt(user_data)
        plan_text = ask_model(prompt)
        save_history(user_data, plan_text)

        # Display workout and diet plan in boxes
        if "2. Diet plan" in plan_text:
            workout, diet = plan_text.split("2. Diet plan", 1)
            st.markdown("## 🏋️ Workout Plan")
            st.markdown(f'<div class="boxed">{workout.strip()}</div>', unsafe_allow_html=True)
            st.markdown("## 🥗 Diet Plan")
            st.markdown(f'<div class="boxed">{diet.strip()}</div>', unsafe_allow_html=True)
        else:
            st.markdown("## 📝 Full Plan")
            st.markdown(f'<div class="boxed">{plan_text.strip()}</div>', unsafe_allow_html=True)

# --- Chatbot ---
st.markdown("---")
st.subheader("💬 Chat with your AI Fitness Trainer")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def chat_send():
    user_msg = st.session_state.chat_input.strip()
    if user_msg:
        st.session_state.chat_history.append(("You", user_msg))
        bot_msg = ask_model(user_msg)
        st.session_state.chat_history.append(("Trainer", bot_msg))
        st.session_state.chat_input = ""

st.text_input("Your question:", key="chat_input", on_change=chat_send)

chat_html = '<div class="chat-container">'
for speaker, msg in st.session_state.chat_history:
    css_class = "chat-user" if speaker == "You" else "chat-bot"
    chat_html += f'<p><span class="{css_class}">{speaker}:</span> {msg}</p>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# --- Exercise Videos ---
st.markdown("---")
st.subheader("🎥 Exercise Demo Videos Based on Your Plan")

exercise_videos = {
    "push-up": "https://www.youtube.com/embed/IODxDxX7oi4",
    "pushups": "https://www.youtube.com/embed/IODxDxX7oi4",
    "squat": "https://www.youtube.com/embed/aclHkVaku9U",
    "plank": "https://www.youtube.com/embed/pSHjTRCQxIw",
    "jumping jack": "https://www.youtube.com/embed/c4DAnQ6DtF8",
    "burpee": "https://www.youtube.com/embed/dZgVxmf6jkA",
    "lunge": "https://www.youtube.com/embed/QOVaHwm-Q6U",
    "mountain climber": "https://www.youtube.com/embed/cnyTQDSE884"
}

def find_exercises(text):
    found = set()
    if text:
        text_lower = text.lower()
        for ex in exercise_videos:
            if ex in text_lower:
                found.add(ex)
    return found

if plan_text:
    found_exercises = find_exercises(plan_text)
    if found_exercises:
        cols = st.columns(2)
        for i, ex in enumerate(found_exercises):
            with cols[i % 2]:
                st.markdown(f"**{ex.title()}**")
                st.video(exercise_videos[ex])
    else:
        st.info("No known exercises found to show demos.")
else:
    st.info("Generate a plan to see demo videos.")

# --- Plan History ---
st.markdown("---")
if st.checkbox("📄 Show Previous Plans"):
    history = load_history()
    for item in reversed(history[-5:]):
        st.markdown(f"### ⏰ {item['timestamp']}")
        st.json(item['user'])
        st.markdown(f'<div class="boxed">{item["response"]}</div>', unsafe_allow_html=True)
