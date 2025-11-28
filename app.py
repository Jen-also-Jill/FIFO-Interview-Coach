import streamlit as st
from openai import OpenAI
import os

# 1. Page Configuration
st.set_page_config(page_title="FIFO Interview Coach", page_icon="🦺")

# 2. Main Title and Introduction
st.title("🦺 FIFO Job Interview Simulator")
st.write("**Role:** Entry Level Utility / Leasehand")
st.info("👋 G'day! Turn your volume up. I'm going to READ the questions to you now.")

# 3. Securely access the API key
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ OpenAI API Key is missing. Please set it in Streamlit Secrets.")
    st.stop()

# 4. The Interview Logic (The Brain)
system_prompt = """
You are a tough but fair Australian Mining HR Recruiter named Bluey. 
You are interviewing a candidate for an entry-level FIFO role (Utility/Leasehand).
Your feedback must be based on: 
1. SAFETY (Stop Work Authority is king).
2. RESILIENCE (Can they handle 12hr shifts/heat/flies?).
3. TEAM FIT (No drama, 'camp etiquette').
Tone: Use light Australian slang (mate, swing, crib room), but be deadly serious about safety.
"""

# 5. Question Selection
category = st.selectbox(
    "Select a Topic to Practice:",
    ["The 'Safety' Question (Crucial)", "The 'Lifestyle' Question (Resilience)", "The 'Camp Life' Question (Conflict)"]
)

# Define the questions
if category == "The 'Safety' Question (Crucial)":
    question = "Safety is our number one priority. Tell me about a time you saw a hazard or something unsafe at work. What did you do?"
elif category == "The 'Lifestyle' Question (Resilience)":
    question = "The roster is two weeks on, one week off. You will miss birthdays and it is 40 degrees in the shade. Why do you think you can handle the FIFO lifestyle?"
else:
    question = "You are tired, it is day 13, and a crew mate is being difficult in the mess hall. How do you handle the conflict without causing drama?"

# --- NEW: AUDIO GENERATION PART ---
st.markdown(f"### 🗣️ Question:")
st.write(f"**{question}**")

# This creates the audio file from the text
speech_file_path = "interview_question.mp3"
with st.spinner("Bluey is clearing his throat..."):
    response = client.audio.speech.create(
      model="tts-1",
      voice="onyx", # Options: alloy, echo, fable, onyx, nova, and shimmer
      input=question
    )
    response.stream_to_file(speech_file_path)

# This plays the audio
st.audio(speech_file_path, format="audio/mp3")
# ----------------------------------

# 6. User Answer Input
user_answer = st.text_area("Type your answer here:", height=150, placeholder="Example: 'In my last job, I noticed...'")

# 7. The Feedback Button
if st.button("Get Feedback from Bluey"):
    if not user_answer:
        st.warning("Please type an answer first, mate!")
    else:
        with st.spinner("Reviewing your answer against site safety protocols..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"The Question: {question}. Candidate Answer: {user_answer}. Critique this answer."}
                    ]
                )
                feedback = response.choices[0].message.content
                st.success("✅ **Feedback:**")
                st.markdown(feedback)
            except Exception as e:
                st.error(f"An error occurred: {e}")
