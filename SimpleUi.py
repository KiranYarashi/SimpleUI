import streamlit as st
import sqlite3
from datetime import datetime

# Database Setup
conn = sqlite3.connect('downloads.db', check_same_thread=False)
c = conn.cursor()

# Initialize tables
c.execute('''CREATE TABLE IF NOT EXISTS download_count 
            (id INTEGER PRIMARY KEY, count INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS feedback 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             user TEXT, feedback TEXT, rating INTEGER, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS downloads 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             user TEXT, date TEXT)''')

# Ensure the rating and date columns exist in the feedback table
c.execute('PRAGMA table_info(feedback)')
columns = [column[1] for column in c.fetchall()]
if 'rating' not in columns:
    c.execute('ALTER TABLE feedback ADD COLUMN rating INTEGER')
if 'date' not in columns:
    c.execute('ALTER TABLE feedback ADD COLUMN date TEXT')

# Ensure the date column exists in the downloads table
c.execute('PRAGMA table_info(downloads)')
columns = [column[1] for column in c.fetchall()]
if 'date' not in columns:
    c.execute('ALTER TABLE downloads ADD COLUMN date TEXT')

# Initialize download count
c.execute('INSERT OR IGNORE INTO download_count (id, count) VALUES (1, 0)')
conn.commit()

# Page Config
st.set_page_config(
    page_title="SimpleUi",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme Colors
theme_primary = "#4CAF50"
theme_secondary = "#2C3E50"

# Custom CSS
st.markdown(f"""
<style>
    /* Base Styles */
    body {{
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(180deg, {theme_secondary}, #1a1a1a) !important;
        color: white !important;
    }}
    
    /* Hero Section */
    .hero {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        border: 1px solid {theme_primary};
    }}
    
    /* Feature Cards */
    .feature-card {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {theme_primary};
        transition: transform 0.3s ease;
    }}
    .feature-card:hover {{
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.1);
    }}
    
    /* Form Elements */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid {theme_primary} !important;
        border-radius: 10px !important;
        color: white !important;
    }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {theme_primary}, {theme_secondary});
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .hero {{ padding: 1.5rem; }}
        .feature-card {{ margin: 0.5rem 0; }}
    }}
</style>
""", unsafe_allow_html=True)

# Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Helper Functions
def get_download_count():
    c.execute('SELECT count FROM download_count WHERE id = 1')
    return c.fetchone()[0]

def show_loader(message):
    return st.spinner(message)

# Pages
def home_page():
    # Hero Section
    st.markdown("""
    <div class="hero">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">🌟 SimpleUi</h1>
        <h3 style="opacity: 0.9;">A Minimalist Distraction Free App</h3>
    </div>
    """, unsafe_allow_html=True)

    # Features Grid
    features = [
        {"icon": "🚀", "title": "Instant Launch", "desc": "Near-zero loading times"},
        {"icon": "🔋", "title": "Low Resource Use", "desc": "Optimized for battery life"},
        {"icon": "🛡️", "title": "Privacy First", "desc": "No tracking, no ads"},
        {"icon": "🎯", "title": "Focus Mode", "desc": "Minimal distraction design"}
    ]
    
    cols = st.columns(2)
    for idx, feat in enumerate(features):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="feature-card">
                <h3>{feat['icon']} {feat['title']}</h3>
                <p>{feat['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Total Downloads Section
    total_downloads = get_download_count()
    st.markdown("---")
    st.subheader(f"� Total Downloads: {total_downloads}")

    # Download Section
    st.markdown("---")
    st.subheader("�🚀 Get Started")
    
    download_ready = False
    user_name = ""
    
    with st.form("download_form"):
        user_name = st.text_input("Your Name:", placeholder="Enter your name", 
                                help="We'll personalize your experience")
        
        if st.form_submit_button("📥 Download Now"):
            if len(user_name.strip()) >= 3:
                with show_loader("Preparing your download..."):
                    # Update download count
                    new_count = get_download_count() + 1
                    c.execute('UPDATE download_count SET count = ? WHERE id = 1', (new_count,))
                    c.execute('INSERT INTO downloads (user, date) VALUES (?, ?)',
                            (user_name.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    
                st.success(f"Thanks {user_name}! Your download is ready ✅")
                st.balloons()
                download_ready = True
            else:
                st.error("Please enter a valid name (min 3 characters)")

    if download_ready:
        with open("SimpleUiBeta.apk", "rb") as f:
            st.download_button(
                label="Save to Device",
                data=f,
                file_name="SimpleUiBeta.apk",
                mime="application/vnd.android.package-archive"
            )

    # Feedback Section
    st.markdown("---")
    st.subheader("💬 Share Feedback")
    
    with st.expander("We value your opinion", expanded=True):
        with st.form("feedback_form"):
            fb_name = st.text_input("Your Name:", placeholder="Optional")
            rating = st.slider("Rating (1-5 stars)", 1, 5, 5)
            feedback = st.text_area("Your Message:", placeholder="What can we improve?")
            
            if st.form_submit_button("Submit Feedback"):
                if feedback.strip():
                    c.execute('INSERT INTO feedback (user, feedback, rating, date) VALUES (?, ?, ?, ?)',
                            (fb_name.strip() or "Anonymous", feedback, rating, 
                             datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    st.success("🎉 Thank you for your feedback!")
                else:
                    st.warning("Please share your thoughts before submitting")
def feedback_page():
    st.title("📊 Feedback")
    c.execute('SELECT user, feedback, rating, date FROM feedback')
    feedbacks = c.fetchall()
    
    for fb in feedbacks:
        st.markdown(f"""
        **Name:** {fb[0]}  
        **Rating:** {fb[2]}  
        **Feedback:** {fb[1]}  
        **Date:** {fb[3]}  
        ---
        """)

def downloaders_page():
    st.title("📥 Downloads")
    
    # Total Downloads
    total_downloads = get_download_count()
    st.subheader(f"📈 Total Downloads: {total_downloads}")
    
    c.execute('SELECT user, date FROM downloads')
    downloads = c.fetchall()
    
    for dl in downloads:
        st.markdown(f"""
        **Name:** {dl[0]}  
        **Date:** {dl[1]}  
        ---
        """)
# Sidebar Navigation
with st.sidebar:
    st.title("🌐 Navigation")
    page = st.radio("Choose Section", [
        "🏠 Home",
        "📊 Feedback",
        "📥 Downloads"
    ])

# Page Routing
if page == "🏠 Home":
    home_page()
elif page == "📊 Feedback":
    feedback_page()
elif page == "📥 Downloads":
    downloaders_page()

# Close connection
conn.close()