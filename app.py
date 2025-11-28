import streamlit as st
from openai import OpenAI
import os

# 1. Page Configuration
st.set_page_config(page_title="FIFO Interview Coach", page_icon="🦺")

# --- DESIGN SECTION ---
page_bg_color = """
<style>
/* 1. Main Background Color (Sage Green) */
.stApp {
    background-color: #828f7e;
}

/* 2. Text Color (White for visibility) */
h1, h2, h3, p, .stMarkdown, label, li, .stTextInput > label {
    color: #FFFFFF !important;
}

/* 3. FIX THE BUTTONS (Dark Grey -> Light Grey on Hover) */
.stButton > button {
    background-color: #4A4A4A !important; 
    color: #FFFFFF !important;            
    border: 1px solid #FFFFFF !important; 
    font-weight: bold !important;         
}
.stButton > button:hover {
    background-color: #D3D3D3 !important; 
    color: #000000 !important;            
    border: 1px solid #000000 !important; 
}

/* 4. FIX THE DROPDOWN MENU */
div[data-baseweb="select"] > div {
    color: #000000 !important;
}
div[data-baseweb="popover"] li {
    color: #000000 !important;
    background-color: #FFFFFF !important;
}
div[data-baseweb="popover"] div {
    color: #000000 !important;
}

/* 5. FIX THE COACH TIPS BOX (Navy Blue) */
div[data-testid="stAlert"] {
    background-color: #2C3E50 !important; 
    color: #FFFFFF !important;
    border: 2px solid #D9EAF7 !important;
    border-radius: 10px;
}
div[data-testid="stAlert"] * {
    color: #FFFFFF !important;
}
div[data-testid="stAlert"] svg {
    fill: #FFFFFF !important;
}

</style>
"""
st.markdown(page_bg_color, unsafe_allow_html=True)
# ----------------------------------------

# --- 🔒 SECURITY SECTION (UPDATED FOR MOBILE) ---
SECRET_PASSWORD = "FIFO-2026-WITHJ" 

# Check if password is already correct in session state (so it remembers them)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 FIFO Path Login")
    st.write("Please enter the access code to continue.")
    
    # Password box in the MAIN CENTER (Better for mobile)
    password_guess = st.text_input("Password:", type="password", placeholder="Enter code here...")
    
    if st.button("Login"):
        if password_guess == SECRET_PASSWORD:
            st.session_state.authenticated = True
            st.rerun() # Refresh the page to show the app
        else:
            st.error("Incorrect password. Please try again.")
    
    st.stop() # Stop here if not logged in
# ------------------------------------------------

# IF LOGGED IN, SHOW THE APP:
st.title("🦺 FIFO Interview Coach")
st.write("**Role:** Entry Level Utility")

# --- CUSTOM OLIVE GREEN BANNER ---
st.markdown("""
    <div style='background-color: #556B2F; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <p style='color: white; margin: 0; font-size: 16px;'>
        👋🏻 Hi! I will help you fix your English and give you 'Insider Tips' on what HR wants to hear.
        </p>
    </div>
""", unsafe_allow_html=True)
# -------------------------------------------------------------

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ OpenAI API Key is missing. Please set it in Streamlit Secrets.")
    st.stop()

# --- THE QUESTION BANK (15 Questions) ---
questions = {
    # Section 1: Motivation & Logistics
    "Logistics: 1. Why FIFO?": 
        "There are plenty of local jobs available right now. Why do you specifically want to start a FIFO career?",
    
    "Logistics: 2. Role Understanding": 
        "This is an entry-level position. What is your understanding of the actual daily duties involved in this specific role?",
    
    "Logistics: 3. Availability": 
        "If you were successful, how much notice do you need to give your current employer, and when would you be available to fly?",
    
    "Logistics: 4. Tickets & Licenses": 
        "Do you currently hold a valid Driver’s License and a Construction White Card? Are there any other tickets you hold?",

    # Section 2: The FIFO Lifestyle
    "Lifestyle: 5. Remote Experience": 
        "Have you ever lived or worked in a remote location with limited phone reception and amenities? How did you handle it?",
    
    "Lifestyle: 6. Night Shifts & Sleep": 
        "This roster requires 12-hour shifts, including rotating night shifts. Have you worked irregular hours before, and how do you manage your sleep?",
    
    "Lifestyle: 7. Family & Isolation": 
        "You will be away for weeks at a time, missing birthdays and weekends. Have you discussed this roster with your family or partner, and are they supportive?",
    
    "Lifestyle: 8. Camp Conflict (Dongas)": 
        "You will be living in close quarters with your colleagues. How would you handle a situation where a neighbor is being loud or messy?",

    # Section 3: Safety (Crucial)
    "Safety: 9. Unsafe Orders": 
        "If a supervisor asked you to do a task you felt was unsafe or you weren't trained for, what would you do?",
    
    "Safety: 10. Hazard Identification": 
        "Tell me about a time in a previous job where you saw a safety hazard. Did you report it or fix it?",
    
    "Safety: 11. Drugs & Alcohol": 
        "We have a zero-tolerance policy for drugs and alcohol, including random testing on arrival. Is there any reason you would not pass a medical or drug screen next week?",
    
    "Safety: 12. Physical Fitness (Heat)": 
        "The work is physically demanding and often performed in extreme heat. How do you currently maintain your physical fitness?",

    # Section 4: Work Ethic
    "Work Ethic: 13. Repetitive Tasks": 
        "Entry-level roles often involve repetitive, dirty, or labor-intensive tasks like cleaning or digging. How do you stay motivated when the work gets boring?",
    
    "Work Ethic: 14. Reliability": 
        "Missing a flight affects the whole team. Can you give me an example of your reliability or punctuality in your last job?",
    
    "Work Ethic: 15. Following Procedures": 
        "In mining, following Standard Operating Procedures (SOPs) is critical. Can you describe a time you had to follow strict rules to complete a job?"
}
# -------------------------

# Select the question
selected_label = st.selectbox("Select a Topic to Practice:", list(questions.keys()))
question_text = questions[selected_label]

# --- AUDIO GENERATION ---
st.markdown(f"### 💬 Question:")
st.write(f"**{question_text}**")

speech_file_path = "interview_question.mp3"

if st.button(" ▶︎ Play to listen"):
    with st.spinner("Loading ..."):
        try:
            response = client.audio.speech.create(
              model="tts-1",
              voice="onyx", 
              input=question_text
            )
            response.stream_to_file(speech_file_path)
            st.audio(speech_file_path, format="audio/mp3")
        except Exception as e:
            st.warning("Could not generate audio. Please read the text above.")

# --- FEEDBACK LOGIC (SUPPORTIVE + KEYWORDS) ---
user_answer = st.text_area("Type your answer here:", height=150)

if st.button("Get Helpful Feedback"):
    if not user_answer:
        st.warning("Please type your answer first!")
    else:
        system_prompt = """
        You are a supportive Job Interview Coach helping candidates who speak English as a Second Language (ESL).
        The candidates are Backpackers (WHV) applying for entry-level mining jobs in Australia.
        
        Your Goal:
        1. Be kind, encouraging, and clear.
        2. Keep the feedback simple (no big corporate words).
        3. Teach them the specific 'Keywords' that Australian Mining Recruiters look for.

        Output Structure (Use Markdown):
        **👍🏻 Feedback:** (Write 1 simple paragraph. Tell them what was good and fix any major English mistakes nicely.)

        **✨ Better ways to say it:**
        (Provide 2 simple, strong example sentences they can memorize. Use simple grammar but professional words.)

        **💡 Pro Tip (What HR wants to hear):**
        (Explain ONE key concept or buzzword they should use for this specific question. E.g., 'Take 5', 'Duty of Care', 'Reliability', 'Hydration', 'SOPs'. Explain WHY the recruiter likes this word.)
        """
        
        with st.spinner("Coach is writing some tips for you..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question_text}. Candidate Answer: {user_answer}. Help them improve."}
                ]
            )
            st.success("📝 **Coach's Tips:**")
            st.markdown(response.choices[0].message.content)
