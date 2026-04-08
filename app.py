import streamlit as st
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from streamlit_cookies_controller import CookieController
from datetime import datetime, timedelta

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

/* FIX DOWNLOAD BUTTON - Match page background so it looks subtle */
.stDownloadButton > button {
    background-color: #828f7e !important;
    color: #FFFFFF !important;
    border: 1px solid #FFFFFF !important;
    font-weight: normal !important;
}
.stDownloadButton > button:hover {
    background-color: #6b7a67 !important;
    color: #FFFFFF !important;
}

/* 4. FIX THE DROPDOWN MENU */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    -webkit-appearance: none !important;
    appearance: none !important;
}

/* FORCE DROPDOWN ARROW ON iOS */
div[data-baseweb="select"] svg {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    fill: #000000 !important;
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

/* 6. FIX TEXT AREA - Force white background & black text */
textarea {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* 7. FIX ALL INPUT FIELDS */
input, select {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* 8. OVERRIDE iOS/Safari Dark Mode */
@media (prefers-color-scheme: dark) {
    textarea, input, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
}

/* 9. CAMOUFLAGE THE FOOTER */
footer {visibility: hidden !important;}
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important;}

div[class*="viewerBadge"] {
    background-color: #828f7e !important;
    color: #828f7e !important;
    display: none !important;
}

</style>
"""
st.markdown(page_bg_color, unsafe_allow_html=True)

# --- 🔒 SECURITY SECTION (7-DAY COOKIE) ---
controller = CookieController()

try:
    SECRET_PASSWORD = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Password missing in Secrets! Add APP_PASSWORD in Streamlit Settings -> Secrets.")
    st.stop()

# Read cookie
auth_cookie = controller.get("fifo_auth")

# Set session state based on cookie
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if auth_cookie == "authenticated":
    st.session_state.authenticated = True

# Show login screen if not authenticated
if not st.session_state.authenticated:
    st.title("🔒 FIFO Path Login")
    st.write("Please enter the access code to continue.")

    password_guess = st.text_input("Password:", type="password", placeholder="Enter code here...")

    if st.button("Login"):
        if password_guess == SECRET_PASSWORD:
            st.session_state.authenticated = True
            expiry = datetime.now() + timedelta(days=7)
            controller.set("fifo_auth", "authenticated", expires=expiry)
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    st.stop()

# --- IF LOGGED IN, SHOW THE APP ---

# Title: 1 line, no emoji
st.markdown("<h1 style='font-size: 2rem; white-space: nowrap;'>FIFO Interview Coach</h1>", unsafe_allow_html=True)
st.write("**Role:** Entry Level Utility")

# --- CUSTOM OLIVE GREEN BANNER ---
st.markdown("""
    <div style='background-color: #556B2F; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <p style='color: white; margin: 0; font-size: 16px;'>
        👋🏻 Hi! I will help you fix your English and give you 'Insider Tips' on what HR wants to hear.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- API CLIENTS ---
try:
    openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ OpenAI API Key is missing. Please set it in Streamlit Secrets.")
    st.stop()

try:
    eleven_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
except:
    st.error("⚠️ ElevenLabs API Key is missing. Please set it in Streamlit Secrets.")
    st.stop()

# --- THE QUESTION BANK (15 Questions) ---
questions = {
    "Logistics: 1. Why FIFO?": 
        "There are plenty of local jobs available right now. Why do you specifically want to start a FIFO career?",
    
    "Logistics: 2. Role Understanding": 
        "This is an entry-level position. What is your understanding of the actual daily duties involved in this specific role?",
    
    "Logistics: 3. Availability": 
        "If you were successful, how much notice do you need to give your current employer, and when would you be available to fly?",
    
    "Logistics: 4. Tickets & Licenses": 
        "Do you currently hold a valid Driver's License and a Construction White Card? Are there any other tickets you hold?",

    "Lifestyle: 5. Remote Experience": 
        "Have you ever lived or worked in a remote location with limited phone reception and amenities? How did you handle it?",
    
    "Lifestyle: 6. Night Shifts & Sleep": 
        "This roster requires 12-hour shifts, including rotating night shifts. Have you worked irregular hours before, and how do you manage your sleep?",
    
    "Lifestyle: 7. Family & Isolation": 
        "You will be away for weeks at a time, missing birthdays and weekends. Have you discussed this roster with your family or partner, and are they supportive?",
    
    "Lifestyle: 8. Camp Conflict (Dongas)": 
        "You will be living in close quarters with your colleagues. How would you handle a situation where a neighbor is being loud or messy?",

    "Safety: 9. Unsafe Orders": 
        "If a supervisor asked you to do a task you felt was unsafe or you weren't trained for, what would you do?",
    
    "Safety: 10. Hazard Identification": 
        "Tell me about a time in a previous job where you saw a safety hazard. Did you report it or fix it?",
    
    "Safety: 11. Drugs & Alcohol": 
        "We have a zero-tolerance policy for drugs and alcohol, including random testing on arrival. Is there any reason you would not pass a medical or drug screen next week?",
    
    "Safety: 12. Physical Fitness (Heat)": 
        "The work is physically demanding and often performed in extreme heat. How do you currently maintain your physical fitness?",

    "Work Ethic: 13. Repetitive Tasks": 
        "Entry-level roles often involve repetitive, dirty, or labor-intensive tasks like cleaning or digging. How do you stay motivated when the work gets boring?",
    
    "Work Ethic: 14. Reliability": 
        "Missing a flight affects the whole team. Can you give me an example of your reliability or punctuality in your last job?",
    
    "Work Ethic: 15. Following Procedures": 
        "In mining, following Standard Operating Procedures (SOPs) is critical. Can you describe a time you had to follow strict rules to complete a job?"
}

# --- CHOOSE YOUR HR VOICE ---
# ElevenLabs Voice IDs for each HR character
voice_map = {
    "Bruce — Senior HR ":        "JBFqnCBsd6RMkjVDRZzb",  # George
    "George — Site Manager  ":    "bIHbv24MWmeRgasZH58o",  # Charlie 
    "Charlie — General Recruiter ": "nPczCjzI2devNBz1zQrb", # Will
    "Charlotte — HR Coordinator ":   "XB0fDUnXU5powFXDhCwa",  # Charlotte
}

st.markdown("### Choose Your HR Voice")
selected_hr = st.selectbox(
    "",
    options=list(voice_map.keys()),
    index=0
)
voice_id = voice_map[selected_hr]

# --- SELECT AN INTERVIEW QUESTION ---
st.markdown("### 💬 Select an Interview Question")
selected_label = st.selectbox(
    "",
    list(questions.keys()),
    key="question_select"
)
question_text = questions[selected_label]

# --- QUESTION DISPLAY ---
st.markdown("### 💬 Question:")
st.write(f"**{question_text}**")

# --- AUDIO GENERATION (ELEVENLABS - Works on iPhone + Android) ---
if st.button(" ▶︎ Play to listen"):
    with st.spinner("Loading ..."):
        try:
            # Generate audio with ElevenLabs
            audio_generator = eleven_client.text_to_speech.convert(
                voice_id=voice_id,
                text=question_text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            # Convert generator to bytes
            audio_bytes = b"".join(audio_generator)

            # Play audio — works on iOS and Android
            st.audio(audio_bytes, format="audio/mp3")

            # Backup download button for any stubborn devices
            st.download_button(
                label="⬇️ Can't hear it? Download & Play",
                data=audio_bytes,
                file_name="question.mp3",
                mime="audio/mp3"
            )
        except Exception as e:
            st.warning(f"Could not generate audio: {e}")

# --- FEEDBACK LOGIC (OPENAI) ---
user_answer = st.text_area("Type your answer here:", height=150, key=f"answer_{selected_label}")

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
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question_text}. Candidate Answer: {user_answer}. Help them improve."}
                ]
            )
            st.success("📝 **Coach's Tips:**")
            st.markdown(response.choices[0].message.content)
