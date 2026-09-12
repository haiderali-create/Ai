import streamlit as st
import os
import json
import datetime
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

# Page Config & Theme Setup
st.set_page_config(
    page_title="AI Social Scheduler", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Dark/Neon UI Layout
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00f2fe; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; margin-bottom: 30px; }
    .stButton>button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white; border: none; padding: 10px 24px;
        border-radius: 8px; font-weight: bold; width: 100%;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,114,255,0.4);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,198,255,0.6); }
    .card {
        background-color: #1e222b; padding: 20px;
        border-radius: 12px; border-left: 5px solid #00f2fe;
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sidebar-text { font-size: 14px; color: #a3a8b4; }
    </style>
""", unsafe_allow_html=True)

# Directories & Files Initialization
VIDEOS_DIR = "videos_to_post"
STATUS_FILE = "upload_status.json"
for d in [VIDEOS_DIR]: 
    if not os.path.exists(d): os.makedirs(d)

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f: return json.load(f)
    return []

def save_status(data):
    with open(STATUS_FILE, "w") as f: json.dump(data, f, indent=4)

# --- SIDEBAR: ACCOUNT INTEGRATION ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff007f;'>🔑 Platform Connections</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-text'>Apne accounts ko authenticate karein taake automation sahi chal sake.</p>", unsafe_allow_html=True)
    
    # YouTube Auth Section
    st.subheader("📺 YouTube Shorts")
    if os.path.exists("youtube_token.json"):
        st.success("Connected to YouTube!")
    else:
        st.warning("YouTube Not Connected")
        if st.button("Link YouTube Account", key="yt_btn"):
            st.info("OAuth setup initiation text goes here...")
            
    st.markdown("---")
    
    # TikTok Auth Section
    st.subheader("🎵 TikTok Studio")
    if os.path.exists("tiktok_cookies.pkl"):
        st.success("Connected to TikTok!")
    else:
        st.error("TikTok Login Required")
        if st.button("Link TikTok Account", key="tt_btn"):
            st.info("Browser window khulegi login karne ke liye...")

# --- MAIN DISPLAY ---
st.markdown("<h1>🚀 AI Multi-Platform Scheduler</h1>", unsafe_allow_html=True)

# Layout grid: Left for Input, Right for Analytics/Queue
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("<div class='card'><h3>📤 Nayi Video Schedule Karein</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Video Upload (.mp4)", type=["mp4"])
    
    title = st.text_input("Video Title (YouTube Shorts Headline)")
    caption = st.text_area("Description / Caption & Tags (#shorts #tiktok)", height=100)
    
    c_date, c_time = st.columns(2)
    with c_date:
        post_date = st.date_input("Publish Date", datetime.date.today())
    with c_time:
        post_time = st.time_input("Publish Time", datetime.time(12, 0))
        
    st.markdown("**Target Platforms:**")
    ch_yt = st.checkbox("YouTube Shorts ✅", value=True)
    ch_tt = st.checkbox("TikTok Video 🎵", value=True)
    
    if st.button("⚡ Post Queue Mein Shamil Karein"):
        if uploaded_file and title:
            video_path = os.path.join(VIDEOS_DIR, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Queue data dictionary
            current_queue = load_status()
            target_dt = datetime.datetime.combine(post_date, post_time).strftime("%Y-%m-%d %H:%M:%S")
            
            new_item = {
                "id": len(current_queue) + 1,
                "filename": uploaded_file.name,
                "title": title,
                "caption": caption,
                "schedule_time": target_dt,
                "youtube": "Pending" if ch_yt else "Skipped",
                "tiktok": "Pending" if ch_tt else "Skipped"
            }
            current_queue.append(new_item)
            save_status(current_queue)
            st.balloons()
            st.success("Mubarak ho! Video schedule list mein add ho gayi.")
        else:
            st.error("Meharbani karke Title aur Video file zaroor upload karein.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='card'><h3>📋 Active Scheduled Queue</h3>", unsafe_allow_html=True)
    
    queue_data = load_status()
    if queue_data:
        df = pd.DataFrame(queue_data)
        # Displaying grid neatly
        st.dataframe(df[["filename", "schedule_time", "youtube", "tiktok"]], use_container_width=True)
        
        if st.button("Clear Queue 🗑️", key="clear_q"):
            save_status([])
            st.rerun()
    else:
        st.info("Filhal koi video queue mein pending nahi hai. Left side se add karein!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System Health
    st.markdown("<div class='card'><h3>⚙️ Engine Status</h3>", unsafe_allow_html=True)
    st.text("Scheduler Status: Running 🟢")
    st.text(f"Total Videos in Folder: {len(os.listdir(VIDEOS_DIR))}")
    st.markdown("</div>", unsafe_allow_html=True)
