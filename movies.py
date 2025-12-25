import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Persistence layer
USER_DIR = "users"

def save_to_db(username, library):
    """Saves the library dictionary to a JSON file."""
    if not os.path.exists(USER_DIR):
        os.makedirs(USER_DIR)
    file_path = os.path.join(USER_DIR, f"{username.lower()}.json")
    with open(file_path, "w") as f:
        json.dump(library, f, indent=4)

def load_from_db(username):
    """Loads the library from a JSON file."""
    file_path = os.path.join(USER_DIR, f"{username.lower()}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# Initializing API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "library" not in st.session_state:
    st.session_state.library = {}
if "last_recs" not in st.session_state:
    st.session_state.last_recs = []

if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("❌ API Key missing.")
    st.stop()

# Loading data
@st.cache_data
def load_movie_data():
    try:
        df = pd.read_csv("movies.csv")
        for col in ["mood", "genre", "title"]:
            df[col] = df[col].astype(str).str.strip()
        return df
    except FileNotFoundError:
        return None

# Page setup

def show_landing_page():
    st.markdown("<h1 style='text-align: center;'>🎬 Mood2Movie AI</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=1000", use_container_width=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Get Started 🚀", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

def show_login_page():
    st.markdown("## 👋 Account Login")
    st.info("Logging in with a username will reload your saved library.")
    with st.form("login_form"):
        name = st.text_input("Username").strip()
        st.text_input("Password", type="password", help="For this demo, any password works.")
        if st.form_submit_button("Login"):
            if name:
                st.session_state.user_name = name
                # Loading persistent data
                st.session_state.library = load_from_db(name)
                st.session_state.page = "app"
                st.rerun()
            else:
                st.error("Please enter a username.")

def show_app_page():
    with st.sidebar:
        st.title(f"Hi, {st.session_state.user_name}!")
        if st.button("Logout"):
            # Clear state on logout
            st.session_state.page = "landing"
            st.session_state.user_name = None
            st.session_state.library = {}
            st.session_state.last_recs = []
            st.rerun()

    tab1, tab2 = st.tabs(["🔍 Discover", "📚 My Library"])
    movies = load_movie_data()

    # Tab 1
    with tab1:
        moods = sorted(movies["mood"].unique())
        genres = ["All"] + sorted(movies["genre"].unique())
        
        c1, c2 = st.columns(2)
        selected_mood = c1.selectbox("Mood", moods)
        selected_genre = c2.selectbox("Genre", genres)

        if st.button("💫 Generate Recommendations"):
            filtered = movies[movies["mood"].str.lower() == selected_mood.lower()]
            if selected_genre != "All":
                filtered = filtered[filtered["genre"].str.lower() == selected_genre.lower()]

            if filtered.empty:
                st.warning("No matches found.")
            else:
                st.session_state.last_recs = []
                movie_titles = filtered["title"].tolist()[:5]
                
                with st.spinner("AI is analyzing..."):
                    for title in movie_titles:
                        try:
                            prompt = f"Explain why '{title}' fits a {selected_mood} mood in 15 words."
                            response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
                            st.session_state.last_recs.append({"title": title, "explanation": response.text, "mood": selected_mood})
                        except:
                            st.session_state.last_recs.append({"title": title, "explanation": "A great choice for you!", "mood": selected_mood})

        for rec in st.session_state.last_recs:
            with st.container(border=True):
                col_text, col_btn = st.columns([4, 1])
                with col_text:
                    st.subheader(f"🎥 {rec['title']}")
                    st.write(rec['explanation'])
                with col_btn:
                    if rec['title'] in st.session_state.library:
                        st.button("✅ Saved", key=f"btn_{rec['title']}", disabled=True)
                    else:
                        if st.button("⭐ Add", key=f"btn_{rec['title']}"):
                            # CREATE record
                            st.session_state.library[rec['title']] = {
                                "status": "Going to Watch",
                                "comments": "",
                                "mood_context": rec['mood'],
                                "added_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            # SAVE record to JSON
                            save_to_db(st.session_state.user_name, st.session_state.library)
                            st.toast(f"Added {rec['title']}!")
                            st.rerun()

    # Tab 2 - Library
    with tab2:
        st.header("Your Saved Library")
        if not st.session_state.library:
            st.info("You haven't saved any movies yet.")
        else:
            for title in list(st.session_state.library.keys()):
                data = st.session_state.library[title]
                with st.expander(f"🎬 {title} — {data['status']}"):
                    # UPDATE record
                    new_status = st.selectbox("Status", ["Going to Watch", "Watching", "Watched", "Not Watching"],
                                             index=["Going to Watch", "Watching", "Watched", "Not Watching"].index(data['status']),
                                             key=f"lib_stat_{title}")
                    
                    if new_status != data['status']:
                        st.session_state.library[title]["status"] = new_status
                        save_to_db(st.session_state.user_name, st.session_state.library)
                        st.rerun()

                    if new_status in ["Watched", "Not Watching"]:
                        comment = st.text_area("Notes", value=data['comments'], key=f"lib_note_{title}")
                        if comment != data['comments']:
                            st.session_state.library[title]["comments"] = comment
                            save_to_db(st.session_state.user_name, st.session_state.library)

                    # DELETE record
                    if st.button("🗑️ Remove", key=f"lib_del_{title}"):
                        del st.session_state.library[title]
                        save_to_db(st.session_state.user_name, st.session_state.library)
                        st.rerun()

# Router
if st.session_state.page == "landing":
    show_landing_page()
elif st.session_state.page == "login":
    show_login_page()
elif st.session_state.page == "app":
    show_app_page()
