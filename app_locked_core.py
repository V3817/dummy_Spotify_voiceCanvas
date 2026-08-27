# LOCKED CORE FUNCTIONALITY - DO NOT MODIFY
import streamlit as st
import re
import tempfile
import os
import time
import json
import random
import shutil
from datetime import datetime
import pandas as pd
from pydub import AudioSegment
from openai import OpenAI
import groq
import requests
from io import BytesIO
import base64

# Define enhanced CSS
enhanced_css = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');
    
    /* Global Theme */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, #f8f9ff 0%, #edf1f9 100%);
        border-radius: 1.2rem;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.06);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif;
    }
    
    .main-header {
        font-size: 3.4rem;
        font-weight: 800;
        background: linear-gradient(120deg, #6C63FF 0%, #FF6584 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        animation: fadeIn 1.2s ease-in-out;
    }
    
    .sub-header {
        font-size: 1.6rem;
        background: linear-gradient(120deg, #4F46E5 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2.5rem;
        text-align: center;
        font-weight: 500;
        animation: slideUp 1s ease-in-out;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(120deg, #6C63FF 0%, #8B5CF6 100%);
        color: white;
        border: none;
        border-radius: 0.6rem;
        padding: 0.7rem 1.4rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25);
        font-family: 'Montserrat', sans-serif;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(108, 99, 255, 0.3);
        background: linear-gradient(120deg, #7C73FF 0%, #9B6CF6 100%);
    }
    
    .stButton>button:active {
        transform: translateY(1px);
    }
    
    /* Input Fields */
    .api-input {
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        padding: 1.5rem;
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 0.8rem;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #6C63FF;
        transition: all 0.3s ease;
    }
    
    .api-input:hover {
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.08);
        background-color: rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
    }
    
    /* Section Styling */
    .css-1r6slb0, .css-1inwz65 {
        border-radius: 0.9rem;
        border: 1px solid rgba(108, 99, 255, 0.15);
        background-color: rgba(255, 255, 255, 0.85);
        padding: 1.4rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    /* Sidebar Styling */
    .css-1d391kg, .css-163ttbj {
        background: linear-gradient(180deg, #f5f7ff 0%, #e8ecff 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.15);
    }
    
    /* Audio Player */
    audio {
        width: 100%;
        border-radius: 10px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.12);
        background: linear-gradient(90deg, #6C63FF 0%, #8B5CF6 100%);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { 
            opacity: 0;
            transform: translateY(25px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    /* Expanders and Selectboxes */
    .streamlit-expanderHeader, .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 0.7rem;
        border: 1px solid rgba(108, 99, 255, 0.2);
        transition: all 0.3s ease;
        font-family: 'Montserrat', sans-serif;
    }
    
    .streamlit-expanderHeader:hover, .stSelectbox > div > div:hover {
        background-color: rgba(255, 255, 255, 0.95);
        border-color: rgba(108, 99, 255, 0.4);
        transform: translateY(-1px);
    }
    
    /* Text Area */
    .stTextArea > div > div {
        border-radius: 0.7rem;
        border: 1px solid rgba(108, 99, 255, 0.25);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div:focus-within {
        border-color: #6C63FF;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.25);
        transform: translateY(-2px);
    }
    
    /* Dataframe/Table Styling */
    .dataframe {
        border-radius: 0.7rem;
        overflow: hidden;
        border: none !important;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.07);
        font-family: 'Poppins', sans-serif;
    }
    
    .dataframe th {
        background: linear-gradient(90deg, #6C63FF 0%, #8B5CF6 100%) !important;
        color: white !important;
        font-weight: 600;
        padding: 0.8rem 1.2rem !important;
    }
    
    .dataframe td {
        padding: 0.7rem 1.2rem !important;
        border-bottom: 1px solid #f0f2f6;
        background-color: white;
    }
    
    .dataframe tr:nth-child(even) td {
        background-color: #f9fafc;
    }
    
    /* Tooltips */
    .stTooltipIcon {
        color: #6C63FF !important;
    }
    
    /* Audio Container */
    .audio-container {
        background: linear-gradient(135deg, #f9f9ff 0%, #f0f3ff 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border-left: 5px solid #6C63FF;
        transition: all 0.3s ease;
    }
    
    .audio-container:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transform: translateY(-4px);
        background: linear-gradient(135deg, #f9f9ff 0%, #f5f8ff 100%);
    }
    
    /* Story Text Container */
    .story-text-container {
        background: linear-gradient(135deg, #f0f3ff 0%, #e8ecff 100%);
        border-radius: 10px;
        padding: 16px 20px;
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 20px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.04);
        font-family: 'Poppins', sans-serif;
    }
    
    .story-text-container p {
        border-bottom: 1px solid rgba(108, 99, 255, 0.1);
        padding-bottom: 12px;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    
    .story-text-container p:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .story-text-container strong {
        color: #6C63FF;
        font-weight: 600;
    }
    
    .story-text-container em {
        color: #8B5CF6;
        font-style: italic;
        font-weight: 500;
    }
    
    /* Progress Steps */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        position: relative;
    }
    
    .step {
        background: #f0f3ff;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: #6C63FF;
        position: relative;
        z-index: 2;
        transition: all 0.3s ease;
        border: 2px solid #6C63FF;
    }
    
    .step.active {
        background: #6C63FF;
        color: white;
        box-shadow: 0 0 0 5px rgba(108, 99, 255, 0.2);
        animation: pulse 2s infinite;
    }
    
    .step-line {
        position: absolute;
        top: 20px;
        left: 40px;
        right: 40px;
        height: 2px;
        background: #e0e4f5;
        z-index: 1;
    }
    
    /* File Uploader */
    .stFileUploader > div:first-child {
        background: linear-gradient(135deg, #f9f9ff 0%, #f0f3ff 100%);
        border-radius: 12px;
        padding: 16px;
        border: 2px dashed #6C63FF;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .stFileUploader > div:first-child:hover {
        background: linear-gradient(135deg, #f0f3ff 0%, #e7ecff 100%);
        transform: translateY(-2px);
        border-color: #FF6584;
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }
    
    /* Special Effects */
    .shimmer-effect {
        background: linear-gradient(90deg, 
                   rgba(255,255,255,0) 0%, 
                   rgba(255,255,255,0.8) 50%, 
                   rgba(255,255,255,0) 100%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
    }
    
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Feature Card */
    .feature-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #FF6584;
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        background: rgba(255, 255, 255, 0.9);
    }
</style>
"""

# Configure pydub to use the correct ffmpeg path
if os.name == 'nt':  # Windows
    AudioSegment.converter = r"C:\path\to\ffmpeg.exe"
    AudioSegment.ffprobe = r"C:\path\to\ffprobe.exe"
else:  # Linux/MacOS
    AudioSegment.converter = "ffmpeg"
    AudioSegment.ffprobe = "ffprobe"

# Royalty-free background tracks metadata
BACKGROUND_TRACKS = {
    "ambient": {
        "peaceful": [
            {"name": "Gentle Piano", "category": "Ambient", "mood": "Peaceful", "duration": "3:25", "url": "https://freesound.org/data/previews/612/612095_5674468-lq.mp3"},
            {"name": "Forest Ambience", "category": "Ambient", "mood": "Peaceful", "duration": "2:50", "url": "https://freesound.org/data/previews/459/459493_9552187-lq.mp3"},
            {"name": "Soft Waves", "category": "Ambient", "mood": "Peaceful", "duration": "2:10", "url": "https://freesound.org/data/previews/462/462530_8386243-lq.mp3"},
        ],
        "mysterious": [
            {"name": "Dark Ambient", "category": "Ambient", "mood": "Mysterious", "duration": "3:05", "url": "https://freesound.org/data/previews/435/435414_3954364-lq.mp3"},
            {"name": "Distant Echoes", "category": "Ambient", "mood": "Mysterious", "duration": "2:35", "url": "https://freesound.org/data/previews/436/436127_8977358-lq.mp3"},
        ]
    },
    "music": {
        "upbeat": [
            {"name": "Happy Ukulele", "category": "Music", "mood": "Upbeat", "duration": "2:45", "url": "https://freesound.org/data/previews/384/384187_7218762-lq.mp3"},
            {"name": "Cheerful Folk", "category": "Music", "mood": "Upbeat", "duration": "1:55", "url": "https://freesound.org/data/previews/414/414360_8075558-lq.mp3"},
        ],
        "dramatic": [
            {"name": "Epic Orchestral", "category": "Music", "mood": "Dramatic", "duration": "3:15", "url": "https://freesound.org/data/previews/408/408740_5121075-lq.mp3"},
            {"name": "Suspense Strings", "category": "Music", "mood": "Dramatic", "duration": "2:25", "url": "https://freesound.org/data/previews/413/413203_8552661-lq.mp3"},
        ]
    },
    "sound_effects": {
        "nature": [
            {"name": "Birds Chirping", "category": "Sound Effects", "mood": "Nature", "duration": "1:15", "url": "https://freesound.org/data/previews/363/363126_5495244-lq.mp3"},
            {"name": "Rain Sounds", "category": "Sound Effects", "mood": "Nature", "duration": "1:40", "url": "https://freesound.org/data/previews/459/459971_4625050-lq.mp3"},
        ],
        "urban": [
            {"name": "City Ambience", "category": "Sound Effects", "mood": "Urban", "duration": "2:05", "url": "https://freesound.org/data/previews/462/462087_8853730-lq.mp3"},
            {"name": "Coffee Shop", "category": "Sound Effects", "mood": "Urban", "duration": "1:35", "url": "https://freesound.org/data/previews/328/328120_5121236-lq.mp3"},
        ]
    }
}

# Set page configuration
st.set_page_config(
    page_title="VoiceCanvas",
    page_icon="🎙️",
    layout="wide"
)
# Apply enhanced CSS
st.markdown(enhanced_css, unsafe_allow_html=True)

# Initialize session state variables
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = []
if 'character_voices' not in st.session_state:
    st.session_state.character_voices = {}
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'final_audio' not in st.session_state:
    st.session_state.final_audio = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get("OPENAI_API_KEY")
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = "openai"
if 'custom_voice_id' not in st.session_state:
    st.session_state.custom_voice_id = None
if 'voice_clone_status' not in st.session_state:
    st.session_state.voice_clone_status = ""
if 'voice_settings' not in st.session_state:
    st.session_state.voice_settings = {}
if 'background_track' not in st.session_state:
    st.session_state.background_track = "None"
if 'bg_volume' not in st.session_state:
    st.session_state.bg_volume = 0.3
if 'elevenlabs_key' not in st.session_state:
    st.session_state.elevenlabs_key = ""  # Initialize as empty, user will provide
if 'elevenlabs_voice_models' not in st.session_state:
    st.session_state.elevenlabs_voice_models = {}  # Initialize as an empty dictionary
if 'elevenlabs_voice_name' not in st.session_state:
    st.session_state.elevenlabs_voice_name = ""  # Will be set when voices are fetched
if 'openai_key' not in st.session_state:
    st.session_state.openai_key = os.environ.get("OPENAI_API_KEY", "")  # Get from env or empty
if 'groq_key' not in st.session_state:
    st.session_state.groq_key = os.environ.get("GROQ_API_KEY", "")  # Get from env or empty
if 'deepdub_key' not in st.session_state:
    st.session_state.deepdub_key = ""  # Initialize as empty, user will provide
if 'deepdub_email' not in st.session_state:
    st.session_state.deepdub_email = ""  # Initialize as empty, user will provide
if 'openai_voice' not in st.session_state:
    st.session_state.openai_voice = "alloy"
if 'dubbed_audio' not in st.session_state:
    st.session_state.dubbed_audio = None
if 'deepdub_voice_models' not in st.session_state:
    st.session_state.deepdub_voice_models = {}
if 'uploaded_audio' not in st.session_state:
    st.session_state.uploaded_audio = None
if 'story_text' not in st.session_state:
    st.session_state.story_text = None
if 'selected_background_tracks' not in st.session_state:
    st.session_state.selected_background_tracks = []
if 'projects' not in st.session_state:
    st.session_state.projects = {}
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None
if 'project_analytics' not in st.session_state:
    st.session_state.project_analytics = {}
if 'saved_audio_table' not in st.session_state:
    st.session_state.saved_audio_table = []
if 'background_volume_automation' not in st.session_state:
    st.session_state.background_volume_automation = []

# Define voice models
openai_voice_models = {
    "Alloy (Neutral)": "alloy",
    "Echo (Male)": "echo",
    "Fable (Male)": "fable",
    "Onyx (Male)": "onyx",
    "Nova (Female)": "nova",
    "Shimmer (Female)": "shimmer"
}

# Define ElevenLabs constants
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"
DEEPDUB_API_BASE = "https://api.deepdub.ai/v1"

# Function to initialize OpenAI client
def get_openai_client():
    if 'openai_key' in st.session_state and st.session_state.openai_key:
        return OpenAI(api_key=st.session_state.openai_key)
    elif 'api_key' in st.session_state and st.session_state.api_key:
        return OpenAI(api_key=st.session_state.api_key)
    return None
    
# Function to initialize Groq client
def get_groq_client():
    # First check session state for the API key
    if 'groq_key' in st.session_state and st.session_state.groq_key:
        return groq.Client(api_key=st.session_state.groq_key)
    # Then check environment variables
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        # Store in session state for future use
        st.session_state.groq_key = groq_api_key
        return groq.Client(api_key=groq_api_key)
    return None
    
# Function to convert paragraph to dialogue format using Groq
def convert_paragraph_to_dialogue(text):
    """Convert paragraph text to dialogue format using Groq API."""
    try:
        client = get_groq_client()
        if not client:
            st.error("Groq API key not set. Please provide a valid API key.")
            return text
            
        # Create prompt for dialogue conversion
        prompt = f"""
        Convert the following paragraph into a dialogue format with character names, 
        emotions in parentheses, and spoken lines. Format each line as "Character (emotion): Dialogue".
        Ensure the dialogue is natural and flows well between characters.
        
        Paragraph: {text}
        
        Please return only the dialogue without any additional explanation.
        """
        
        # Generate dialogue using Groq API
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a skilled dialogue writer that converts paragraphs into natural dialogue format."},
                {"role": "user", "content": prompt}
            ]
        )
        
        dialogue_text = completion.choices[0].message.content.strip()
        return dialogue_text
        
    except Exception as e:
        st.error(f"Error converting text to dialogue format: {str(e)}")
        return text  # Return original text if conversion fails

# Function to parse text from string
def parse_text_from_string(text):
    """Parse text into structured dialogue data."""
    lines = text.strip().split('\n')
    parsed_data = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Check if line follows the format "Character (emotion): Dialogue"
        match = re.match(r"(.*?)(?:\s*\((.*?)\))?\s*:\s*(.*)", line)
        
        if match:
            character = match.group(1).strip()
            emotion = match.group(2).strip() if match.group(2) else None
            dialogue = match.group(3).strip()
            
            parsed_data.append({
                "character": character,
                "emotion": emotion,
                "dialogue": dialogue
            })
        else:
            # If line doesn't match the format, treat it as narration
            parsed_data.append({
                "character": "Narrator",
                "emotion": None,
                "dialogue": line.strip()
            })
    
    return parsed_data

# Function to parse text from uploaded file
def parse_text_from_file(file):
    """Parse text from uploaded file."""
    try:
        # Read file content based on file type
        file_content = file.getvalue().decode("utf-8")
        return parse_text_from_string(file_content)
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return []

# Function to generate voice using OpenAI TTS
def generate_voice_openai(text, voice_model, speed=1.0, pitch=0, emotion=None):
    """Generate voice audio from text using OpenAI's TTS API."""
    try:
        client = get_openai_client()
        if not client:
            st.error("OpenAI API key not set. Please provide a valid API key.")
            return None
            
        # Extract text without emotion tags
        text_without_emotion = text
        
        # Create temporary file to store audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            # Generate speech using OpenAI API
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice=voice_model,
                input=text_without_emotion,
                speed=speed
            )
            
            # Write response to temporary file
            response.stream_to_file(temp_file.name)
            
            return temp_file.name
            
    except Exception as e:
        st.error(f"Error generating voice with OpenAI: {str(e)}")
        return None

# Function to fetch available voice models from ElevenLabs
def fetch_elevenlabs_voices():
    """Fetch available voice models from ElevenLabs API."""
    try:
        # Check if API key is set
        if not st.session_state.elevenlabs_key:
            st.error("ElevenLabs API key not set. Please provide a valid API key.")
            return {}
            
        # Set up headers with API key
        headers = {
            "xi-api-key": st.session_state.elevenlabs_key,
            "Content-Type": "application/json"
        }
        
        # Make API request to fetch voices
        response = requests.get(f"{ELEVENLABS_API_BASE}/voices", headers=headers)
        
        if response.status_code == 200:
            voices_data = response.json()
            
            # Extract voices and their IDs and store them as a dictionary
            voices = {voice['name']: voice['voice_id'] for voice in voices_data['voices']}
            
            # Create a DataFrame with voice information for display
            voices_info = []
            for voice in voices_data['voices']:
                voices_info.append({
                    "Name": voice['name'],
                    "Voice ID": voice['voice_id'],
                    "Category": voice.get('category', 'N/A'),
                    "Labels": ", ".join([f"{k}: {v}" for k, v in voice.get('labels', {}).items()])
                })
                
            voices_df = pd.DataFrame(voices_info)
            
            # Return voices dictionary
            return voices
        else:
            st.error(f"Failed to fetch ElevenLabs voices. Status code: {response.status_code}")
            st.error(f"Response: {response.text}")
            return {}
            
    except Exception as e:
        st.error(f"Error fetching ElevenLabs voices: {str(e)}")
        return {}

# Function to generate voice using ElevenLabs
def generate_voice_elevenlabs(text, voice_id, stability=0.5, similarity_boost=0.75, emotion=None):
    """Generate voice audio from text using ElevenLabs API."""
    try:
        # Check if API key is set
        if not st.session_state.elevenlabs_key:
            st.error("ElevenLabs API key not set. Please provide a valid API key.")
            return None
            
        # Set up headers with API key
        headers = {
            "xi-api-key": st.session_state.elevenlabs_key,
            "Content-Type": "application/json"
        }
        
        # Extract text without emotion tags
        text_without_emotion = text
        
        # Prepare request data
        data = {
            "text": text_without_emotion,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        # Make API request
        response = requests.post(
            f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}/stream",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.content)
                return temp_file.name
        else:
            st.error(f"Failed to generate audio with ElevenLabs. Status code: {response.status_code}")
            st.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error generating voice with ElevenLabs: {str(e)}")
        return None

# Function to concatenate audio files
def concatenate_audio_files(audio_files, output_path, background_track=None, bg_volume=0.3):
    """Concatenate multiple audio files into a single audio file."""
    try:
        if not audio_files:
            return None
            
        # Load the first audio file
        combined = AudioSegment.from_file(audio_files[0])
        
        # Add a short pause between utterances
        pause = AudioSegment.silent(duration=1000)  # 1-second pause
        
        # Concatenate remaining audio files
        for audio_file in audio_files[1:]:
            next_segment = AudioSegment.from_file(audio_file)
            combined += pause + next_segment
        
        # Add background tracks if available
        if st.session_state.selected_background_tracks:
            # Process each selected background track
            for track in st.session_state.selected_background_tracks:
                # Download the track if it's a URL
                if 'url' in track:
                    bg_track_path = download_background_track(track['url'], track['name'])
                    if not bg_track_path:
                        continue  # Skip if download failed
                else:
                    # If it's a local file path
                    bg_track_path = track.get('path')
                    if not bg_track_path or not os.path.exists(bg_track_path):
                        continue  # Skip if file doesn't exist
                
                # Load background audio
                bg_audio = AudioSegment.from_file(bg_track_path)
                
                # Loop background audio to match the length of narration
                while len(bg_audio) < len(combined):
                    bg_audio += bg_audio
                    
                # Trim background audio to match narration length
                bg_audio = bg_audio[:len(combined)]
                
                # Apply volume automation if enabled
                if st.session_state.background_volume_automation and len(st.session_state.background_volume_automation) >= 2:
                    bg_audio = apply_volume_automation(bg_audio, st.session_state.background_volume_automation)
                else:
                    # Use standard volume adjustment
                    volume = bg_volume
                    if hasattr(track, 'volume'):  # Use track-specific volume if available
                        volume = track.get('volume', bg_volume)
                    bg_audio = bg_audio - (20 - (volume * 20))  # Convert 0-1 scale to dB reduction
                
                # Mix narration with background audio
                combined = combined.overlay(bg_audio)
                
                # Clean up temporary file
                if 'url' in track and bg_track_path:
                    try:
                        os.remove(bg_track_path)
                    except:
                        pass
        
        # For backward compatibility, support direct background_track parameter
        elif background_track and background_track != "None":
            bg_audio = AudioSegment.from_file(background_track)
            
            # Loop background audio to match the length of narration
            while len(bg_audio) < len(combined):
                bg_audio += bg_audio
                
            # Trim background audio to match narration length
            bg_audio = bg_audio[:len(combined)]
            
            # Adjust volume of background audio
            bg_audio = bg_audio - (20 - (bg_volume * 20))  # Adjust volume based on bg_volume (0.1-1.0)
            
            # Mix narration with background audio
            combined = combined.overlay(bg_audio)
            
        # Export the combined audio
        combined.export(output_path, format="mp3")
        return output_path
        
    except Exception as e:
        st.error(f"Error concatenating audio files: {str(e)}")
        return None

# Function to clean up temporary files
def cleanup_temp_files(file_list):
    """Delete temporary files to clean up."""
    for file_path in file_list:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            st.warning(f"Could not remove temporary file {file_path}: {str(e)}")

# OpenAI dubbing function
def openai_dubbing(audio_file_path, target_language="en", voice="alloy"):
    """Dub audio content to a different language using OpenAI."""
    try:
        client = get_openai_client()
        if not client:
            st.error("OpenAI API key not set. Please provide a valid API key.")
            return None
        
        # First, transcribe the audio to text using Whisper
        with open(audio_file_path, "rb") as audio_file:
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        transcribed_text = transcription_response
        
        # Now translate the transcribed text to the target language
        translation_prompt = f"Translate the following text to {target_language}. Maintain the tone and meaning:\n\n{transcribed_text}"
        
        translation_response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for high-quality translation
            messages=[
                {"role": "system", "content": f"You are a professional translator for {target_language}."},
                {"role": "user", "content": translation_prompt}
            ]
        )
        
        translated_text = translation_response.choices[0].message.content.strip()
        
        # Finally, convert the translated text to speech in the target language
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            speech_response = client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=translated_text
            )
            
            speech_response.stream_to_file(temp_file.name)
            return temp_file.name
            
    except Exception as e:
        st.error(f"Error during OpenAI dubbing: {str(e)}")
        return None

# ElevenLabs dubbing function
def elevenlabs_dubbing(audio_file_path, target_language="en", voice_id=None):
    """Dub audio content to a different language using ElevenLabs."""
    try:
        client = get_openai_client()  # For transcription and translation
        if not client or not st.session_state.elevenlabs_key:
            st.error("OpenAI and ElevenLabs API keys are required for this operation.")
            return None
        
        # First, transcribe the audio to text using Whisper
        with open(audio_file_path, "rb") as audio_file:
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        transcribed_text = transcription_response
        
        # Now translate the transcribed text to the target language
        translation_prompt = f"Translate the following text to {target_language}. Maintain the tone and meaning:\n\n{transcribed_text}"
        
        translation_response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for high-quality translation
            messages=[
                {"role": "system", "content": f"You are a professional translator for {target_language}."},
                {"role": "user", "content": translation_prompt}
            ]
        )
        
        translated_text = translation_response.choices[0].message.content.strip()
        
        # Finally, convert the translated text to speech using ElevenLabs
        # Set up headers with API key
        headers = {
            "xi-api-key": st.session_state.elevenlabs_key,
            "Content-Type": "application/json"
        }
        
        # Prepare request data
        data = {
            "text": translated_text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Make API request
        response = requests.post(
            f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}/stream",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.content)
                return temp_file.name
        else:
            st.error(f"Failed to generate dubbed audio with ElevenLabs. Status code: {response.status_code}")
            st.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error during ElevenLabs dubbing: {str(e)}")
        return None

# Generate voice with DeepDub (commented out as it's not working)
def generate_voice_deepdub(text, voice_id=None, language="en"):
    """Generate voice audio from text using DeepDub API."""
    # This function is currently commented out as DeepDub API is not working properly
    pass

# DeepDub dubbing function (commented out as it's not working)
def deepdub_dubbing(audio_file_path, target_language="en", voice_id=None):
    """Dub audio content to a different language using DeepDub."""
    # This function is currently commented out as DeepDub API is not working properly
    pass

# Fetch DeepDub voices function (commented out as it's not working)
def fetch_deepdub_voices():
    """Fetch available voice models from DeepDub API."""
    # This function is currently commented out as DeepDub API is not working properly
    pass

# Function to download background track from URL
def download_background_track(track_url, track_name):
    """Download background track from URL and save to temporary file."""
    try:
        # Use a custom User-Agent header to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # If URL is from Pixabay, update to direct MP3 URL if needed
        if "pixabay.com" in track_url and not track_url.endswith(".mp3"):
            # This is a fallback for demo purposes since some pixabay links have access restrictions
            # In a production app, we would use proper licensed audio files
            st.info(f"Using local demo track instead of remote URL due to access restrictions")
            # Return a simple silent audio for demonstration
            return create_demo_audio_file(track_name)
            
        response = requests.get(track_url, headers=headers)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.content)
                return temp_file.name
        else:
            st.warning(f"Could not download track directly. Using demo audio instead.")
            return create_demo_audio_file(track_name)
    except Exception as e:
        st.warning(f"Using demo audio instead. Error: {str(e)}")
        return create_demo_audio_file(track_name)

# Helper function to create a demo audio file with minimal sound
def create_demo_audio_file(track_name):
    """Create a demo audio file when direct download fails."""
    try:
        # Create a silent audio segment (1 sec) with very soft tone for demo
        from pydub.generators import Sine
        
        # Generate different tones based on track type for demo
        if "bird" in track_name.lower():
            # High pitched gentle tone for birds
            demo_audio = Sine(440).to_audio_segment(duration=3000).fade_in(300).fade_out(500)
            demo_audio = demo_audio - 25  # Lower volume
        elif "ocean" in track_name.lower() or "wave" in track_name.lower():
            # Low frequency for water sounds
            demo_audio = Sine(180).to_audio_segment(duration=3000).fade_in(500).fade_out(500)
            demo_audio = demo_audio - 20
        elif "piano" in track_name.lower():
            # Piano-like tone
            demo_audio = Sine(262).to_audio_segment(duration=500)
            demo_audio += Sine(330).to_audio_segment(duration=500)
            demo_audio += Sine(392).to_audio_segment(duration=500)
            demo_audio = demo_audio.fade_in(100).fade_out(300)
            demo_audio = demo_audio - 15
        else:
            # Generic soft tone
            demo_audio = Sine(220).to_audio_segment(duration=3000).fade_in(300).fade_out(500)
            demo_audio = demo_audio - 20
            
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        demo_audio.export(temp_file.name, format="mp3")
        return temp_file.name
    except Exception as e:
        st.error(f"Error creating demo audio: {str(e)}")
        # Create an empty audio file as last resort
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        with open(temp_file.name, "wb") as f:
            # Write minimal MP3 header for an empty file
            f.write(b"\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        return temp_file.name

# Function to apply volume automation to background audio
def apply_volume_automation(audio_segment, automation_points):
    """Apply volume automation to an audio segment based on automation points."""
    try:
        if not automation_points or len(automation_points) < 2:
            return audio_segment
            
        # Sort automation points by time
        automation_points.sort(key=lambda x: x["time"])
        
        # Create segments based on automation points
        result_audio = AudioSegment.empty()
        audio_length_ms = len(audio_segment)
        
        for i in range(len(automation_points) - 1):
            start_point = automation_points[i]
            end_point = automation_points[i+1]
            
            start_time_ms = int(start_point["time"] * 1000)  # Convert to milliseconds
            end_time_ms = int(end_point["time"] * 1000)
            
            if start_time_ms >= audio_length_ms:
                break
                
            if end_time_ms > audio_length_ms:
                end_time_ms = audio_length_ms
                
            # Extract segment
            segment = audio_segment[start_time_ms:end_time_ms]
            
            # Apply volume gradient across segment
            start_volume = start_point["volume"]
            end_volume = end_point["volume"]
            
            if start_volume == end_volume:
                # Constant volume
                segment = segment - (20 - (start_volume * 20))  # Convert 0-1 scale to dB reduction
            else:
                # Apply gradual volume change
                segment_length_ms = end_time_ms - start_time_ms
                
                # Create a new segment with gradient volume
                result_segment = AudioSegment.empty()
                step_size_ms = 100  # Process in 100ms chunks
                
                for j in range(0, segment_length_ms, step_size_ms):
                    # Calculate volume for this chunk based on position within gradient
                    position_ratio = j / segment_length_ms
                    current_volume = start_volume + (end_volume - start_volume) * position_ratio
                    
                    # Extract and adjust volume of this chunk
                    chunk_end = min(j + step_size_ms, segment_length_ms)
                    chunk = segment[j:chunk_end]
                    chunk = chunk - (20 - (current_volume * 20))  # Convert 0-1 scale to dB reduction
                    
                    # Add to result segment
                    result_segment += chunk
                    
                segment = result_segment
                
            # Add segment to result
            result_audio += segment
            
        # Add any remaining audio
        last_point_time_ms = int(automation_points[-1]["time"] * 1000)
        if last_point_time_ms < audio_length_ms:
            last_segment = audio_segment[last_point_time_ms:]
            last_volume = automation_points[-1]["volume"]
            last_segment = last_segment - (20 - (last_volume * 20))
            result_audio += last_segment
            
        return result_audio
        
    except Exception as e:
        st.error(f"Error applying volume automation: {str(e)}")
        return audio_segment

# Function to save project
def save_project(project_name, include_audio=True):
    """Save the current project state."""
    try:
        if not project_name:
            st.error("Please enter a project name")
            return False
            
        # Generate a unique project ID if new project
        if st.session_state.current_project_id is None:
            project_id = f"project_{int(time.time())}_{random.randint(1000, 9999)}"
            st.session_state.current_project_id = project_id
        else:
            project_id = st.session_state.current_project_id
            
        # Create project data
        project_data = {
            "id": project_id,
            "name": project_name,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text_data": st.session_state.story_text,
            "parsed_data": st.session_state.parsed_data,
            "character_voices": st.session_state.character_voices,
            "api_provider": st.session_state.api_provider,
            "voice_settings": st.session_state.voice_settings,
            "background_tracks": st.session_state.selected_background_tracks,
            "background_volume": st.session_state.bg_volume,
            "background_automation": st.session_state.background_volume_automation
        }
        
        # Save audio files if requested
        if include_audio and st.session_state.final_audio:
            # Create a project directory
            project_dir = os.path.join(tempfile.gettempdir(), project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Copy final audio
            audio_path = os.path.join(project_dir, "final_audio.mp3")
            shutil.copy2(st.session_state.final_audio, audio_path)
            project_data["final_audio_path"] = audio_path
            
            # Copy individual audio files
            individual_audio_paths = []
            for i, audio_file in enumerate(st.session_state.audio_files):
                if os.path.exists(audio_file):
                    file_path = os.path.join(project_dir, f"audio_{i}.mp3")
                    shutil.copy2(audio_file, file_path)
                    individual_audio_paths.append(file_path)
            
            project_data["individual_audio_paths"] = individual_audio_paths
            
        # Store project in session state
        st.session_state.projects[project_id] = project_data
        
        # Initialize analytics if not exists
        if project_id not in st.session_state.project_analytics:
            st.session_state.project_analytics[project_id] = {
                "plays": 0,
                "downloads": 0,
                "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_accessed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engagement_score": 0,
                "ab_test_results": [],
                "version_history": [{
                    "version": 1,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "changes": "Initial creation"
                }]
            }
        
        return True
        
    except Exception as e:
        st.error(f"Error saving project: {str(e)}")
        return False

# Function to load project
def load_project(project_id):
    """Load a project from saved projects."""
    try:
        if project_id not in st.session_state.projects:
            st.error("Project not found")
            return False
            
        project_data = st.session_state.projects[project_id]
        
        # Load project data into session state
        st.session_state.current_project_id = project_id
        st.session_state.story_text = project_data.get("text_data")
        st.session_state.parsed_data = project_data.get("parsed_data", [])
        st.session_state.character_voices = project_data.get("character_voices", {})
        st.session_state.api_provider = project_data.get("api_provider", "openai")
        st.session_state.voice_settings = project_data.get("voice_settings", {})
        st.session_state.selected_background_tracks = project_data.get("background_tracks", [])
        st.session_state.bg_volume = project_data.get("background_volume", 0.3)
        st.session_state.background_volume_automation = project_data.get("background_automation", [])
        
        # Load audio files if available
        if "final_audio_path" in project_data and os.path.exists(project_data["final_audio_path"]):
            st.session_state.final_audio = project_data["final_audio_path"]
            
        if "individual_audio_paths" in project_data:
            individual_paths = project_data["individual_audio_paths"]
            valid_paths = [p for p in individual_paths if os.path.exists(p)]
            if valid_paths:
                st.session_state.audio_files = valid_paths
                
        # Update analytics
        if project_id in st.session_state.project_analytics:
            analytics = st.session_state.project_analytics[project_id]
            analytics["last_accessed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        # Set current step to appropriate value based on loaded data
        if st.session_state.final_audio:
            st.session_state.current_step = 4
        elif st.session_state.audio_files:
            st.session_state.current_step = 3
        elif st.session_state.character_voices:
            st.session_state.current_step = 2
        else:
            st.session_state.current_step = 1
            
        return True
        
    except Exception as e:
        st.error(f"Error loading project: {str(e)}")
        return False

# Function to record analytics event
def record_analytics_event(project_id, event_type, data=None):
    """Record an analytics event for a project."""
    if project_id not in st.session_state.project_analytics:
        return
        
    analytics = st.session_state.project_analytics[project_id]
    
    if event_type == "play":
        analytics["plays"] += 1
    elif event_type == "download":
        analytics["downloads"] += 1
    elif event_type == "ab_test":
        if data and isinstance(data, dict):
            analytics["ab_test_results"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "test_name": data.get("test_name", "Unnamed Test"),
                "variant_a": data.get("variant_a"),
                "variant_b": data.get("variant_b"),
                "winner": data.get("winner"),
                "metrics": data.get("metrics", {})
            })
    elif event_type == "version":
        if data and isinstance(data, dict):
            analytics["version_history"].append({
                "version": len(analytics["version_history"]) + 1,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "changes": data.get("changes", "")
            })
            
    # Update engagement score - a simple calculation based on plays and downloads
    analytics["engagement_score"] = (analytics["plays"] * 1) + (analytics["downloads"] * 3)
    analytics["last_accessed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to perform A/B testing
def perform_ab_test(project_id, test_name, variant_a_data, variant_b_data):
    """Perform an A/B test between two variants of audio."""
    try:
        # Generate audio for both variants
        variant_a_audio = None
        variant_b_audio = None
        
        # Logic to generate test audio would go here
        # This is just a placeholder implementation
        
        # Record test results
        record_analytics_event(project_id, "ab_test", {
            "test_name": test_name,
            "variant_a": variant_a_data,
            "variant_b": variant_b_data,
            "winner": "A",  # Placeholder, would be determined based on user feedback
            "metrics": {
                "completion_rate_a": 0.75,
                "completion_rate_b": 0.65,
                "user_rating_a": 4.2,
                "user_rating_b": 3.8
            }
        })
        
        return True
        
    except Exception as e:
        st.error(f"Error performing A/B test: {str(e)}")
        return False

# Helper function to get ElevenLabs voice ID by name
def get_elevenlabs_voice_id_by_name(voice_name, voices_dict):
    """Get voice ID from voice name."""
    return voices_dict.get(voice_name)

# Main function
def main():
    # App header and subheader
    st.markdown('<h1 class="main-header">🎨 VoiceCanvas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create expressive voice narrations from your text</p>', unsafe_allow_html=True)
    
    # Initialize session state variables if they don't exist
    if 'background_volume_automation' not in st.session_state:
        st.session_state.background_volume_automation = []
        
    if 'project_analytics' not in st.session_state:
        st.session_state.project_analytics = {}
        
    if 'projects' not in st.session_state:
        st.session_state.projects = {}
        
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = None
        
    if 'selected_background_tracks' not in st.session_state:
        st.session_state.selected_background_tracks = []
        
    if 'bg_volume' not in st.session_state:
        st.session_state.bg_volume = 0.3
    
    # Tab selection with emoji-enhanced radio buttons
    tab = st.radio(
        "Choose functionality:",
        ["✨ Voice Generation", "🌍 Voice Dubbing", "ℹ️ About"],
        horizontal=True,
        key="main_tab_selector"
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Voice Generation tab
    if tab == "✨ Voice Generation":
        # API Setup section
        with st.expander("🔑 API Setup", expanded=False):
            st.markdown("""
            <div class="feature-card">
                <h3 style="margin-top:0; color:#6C63FF;">🔐 API Configuration</h3>
                <p>Set up your voice provider API keys to enable voice generation.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # API provider selection
            api_provider = st.selectbox(
                "Select API Provider",
                ["OpenAI TTS", "ElevenLabs", "Groq", "DeepDub"]
            )
            
            # API key input
            if api_provider == "OpenAI TTS":
                openai_key = st.text_input(
                    "Enter your OpenAI API key",
                    value=st.session_state.openai_key if st.session_state.openai_key else "",
                    type="password"
                )
                if openai_key:
                    st.session_state.openai_key = openai_key
                    st.success("OpenAI API key set successfully!")
                
            elif api_provider == "ElevenLabs":
                elevenlabs_key = st.text_input(
                    "Enter your ElevenLabs API key",
                    value=st.session_state.elevenlabs_key if st.session_state.elevenlabs_key else "",
                    type="password"
                )
                if elevenlabs_key:
                    st.session_state.elevenlabs_key = elevenlabs_key
                    st.success("ElevenLabs API key set successfully!")
                
                # Fetch ElevenLabs voices
                if st.button("Fetch ElevenLabs Voices"):
                    with st.spinner("Fetching voices from ElevenLabs..."):
                        voices = fetch_elevenlabs_voices()
                        if voices:
                            st.session_state.elevenlabs_voice_models = voices
                            st.success(f"Successfully fetched {len(voices)} voices from ElevenLabs!")
                        else:
                            st.error("Failed to fetch voices from ElevenLabs.")
                    
            elif api_provider == "Groq":
                groq_key = st.text_input(
                    "Enter your Groq API key",
                    value=st.session_state.groq_key if st.session_state.groq_key else "",
                    type="password",
                    help="Groq API key is used for text-to-dialogue conversion functionality."
                )
                if groq_key:
                    st.session_state.groq_key = groq_key
                    st.success("Groq API key set successfully!")
                    
            elif api_provider == "DeepDub":
                col1, col2 = st.columns(2)
                with col1:
                    deepdub_key = st.text_input(
                        "Enter your DeepDub API key",
                        value=st.session_state.deepdub_key if st.session_state.deepdub_key else "",
                        type="password"
                    )
                with col2:
                    deepdub_email = st.text_input(
                        "Enter your DeepDub email",
                        value=st.session_state.deepdub_email if st.session_state.deepdub_email else ""
                    )
                if deepdub_key and deepdub_email:
                    st.session_state.deepdub_key = deepdub_key
                    st.session_state.deepdub_email = deepdub_email
                    st.success("DeepDub credentials set successfully!")
            
        # Progress steps display
        st.markdown("""
        <div class="step-container">
            <div class="step-line"></div>
            <div class="step active">1</div>
            <div class="step">2</div>
            <div class="step">3</div>
            <div class="step">4</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Step 1: Enter Your Text
        st.subheader("Step 1: Enter Your Text")
        
        # Example format expander
        with st.expander("📝 Example Format", expanded=False):
            st.write("""
            Format your dialogue like this:
            ```
            Arjun (excited): I love to fold paper planes!
            Teacher (curious): Why do you enjoy it so much?
            Arjun (enthusiastic): Because they can fly so high!
            ```
            
            Character names followed by optional emotion in parentheses, then a colon, then the dialogue.
            """)
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Enter text", "Upload file", "Use template"],
            horizontal=True
        )
        
        # Handle different input methods
        if input_method == "Enter text":
            text_input = st.text_area(
                "Enter your text:",
                height=300,
                placeholder="Enter your story or dialogue here..."
            )
            
            if text_input:
                # Check if the text is in paragraph format and offer conversion
                if ":" not in text_input:
                    is_paragraph = st.checkbox("Convert paragraph to dialogue format using Groq API")
                    
                    if is_paragraph:
                        if st.button("Convert to Dialogue"):
                            with st.spinner("Converting text to dialogue format..."):
                                dialogue_text = convert_paragraph_to_dialogue(text_input)
                                st.markdown("""
                                <div style="padding: 15px; background-color: rgba(255, 255, 255, 0.7); 
                                            border-radius: 10px; margin: 20px 0; 
                                            border-left: 5px solid #4F46E5; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                                    <h3 style="margin-top:0; color:#4F46E5;">Converted to dialogue format:</h3>
                                """, unsafe_allow_html=True)
                                
                                # Display converted dialogue
                                st.write(dialogue_text)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                # Save story text for later display
                                st.session_state.story_text = dialogue_text
                                
                                # Parse the dialogue text into structured data
                                parsed_data = parse_text_from_string(dialogue_text)
                                st.session_state.parsed_data = parsed_data
                                st.success(f"Successfully parsed {len(parsed_data)} lines of dialogue.")
                    else:
                        # Save story text for later display
                        st.session_state.story_text = text_input
                        
                        # Parse the text into structured data
                        parsed_data = parse_text_from_string(text_input)
                        st.session_state.parsed_data = parsed_data
                        st.success(f"Successfully parsed {len(parsed_data)} lines of dialogue.")
                else:
                    # Save story text for later display
                    st.session_state.story_text = text_input
                    
                    # Parse the text into structured data
                    parsed_data = parse_text_from_string(text_input)
                    st.session_state.parsed_data = parsed_data
                    st.success(f"Successfully parsed {len(parsed_data)} lines of dialogue.")
                
        elif input_method == "Upload file":
            uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
            
            if uploaded_file:
                # Parse the uploaded file
                parsed_data = parse_text_from_file(uploaded_file)
                
                if parsed_data:
                    st.session_state.parsed_data = parsed_data
                    st.success(f"Successfully parsed {len(parsed_data)} lines of dialogue.")
                    
                    # Save story text for later display
                    file_content = uploaded_file.getvalue().decode("utf-8")
                    st.session_state.story_text = file_content
                    
        elif input_method == "Use template":
            template_options = [
                "Children's Story",
                "Interview",
                "Drama Scene",
                "Podcast Excerpt"
            ]
            
            selected_template = st.selectbox("Select a template", template_options)
            
            # Load template based on selection
            if selected_template == "Children's Story":
                template_text = """Narrator: Once upon a time, in a magical forest, there lived a little squirrel named Sam.
Sam (excited): I'm going to collect so many acorns today!
Owl (wise): Just be careful not to wander too far, young one.
Sam (curious): But what's beyond the ancient oak tree?
Owl (cautious): The unknown can be both wonderful and dangerous.
Narrator: Sam's whiskers twitched with anticipation as he scampered towards adventure."""
                
            elif selected_template == "Interview":
                template_text = """Host (professional): Welcome to tonight's interview with renowned scientist Dr. Jane Maxwell.
Jane (confident): Thank you for having me. I'm excited to share our latest findings.
Host (curious): Your recent discovery has been called revolutionary. How did it all begin?
Jane (reflective): It started with a simple question that nobody had thought to ask before.
Host (intrigued): And what was that question?
Jane (passionate): What if everything we thought we knew about quantum physics was just the beginning?"""
                
            elif selected_template == "Drama Scene":
                template_text = """David (angry): I can't believe you would do this to me, after everything we've been through!
Sarah (defensive): You're not being fair! You never even gave me a chance to explain.
David (hurt): What is there to explain? I saw the messages, Sarah.
Sarah (tearful): It's not what you think, I promise. Please, just listen to me.
David (conflicted): I want to believe you, but how can I trust you now?
Sarah (determined): Because in fifteen years, have I ever given you a reason not to?"""
                
            elif selected_template == "Podcast Excerpt":
                template_text = """Mike (enthusiastic): Hey everyone, welcome back to Tech Talk! I'm your host Mike.
Julie (cheerful): And I'm Julie! Today we're discussing the latest smartphone releases.
Mike (inquisitive): Julie, what did you think of the new features announced this week?
Julie (thoughtful): Honestly, I'm not as impressed as I expected to be. It feels incremental rather than innovative.
Mike (agreeing): I felt the same way. It seems like companies are playing it safe these days.
Julie (optimistic): Though that new camera system might be a game-changer for mobile photography."""
                
            # Display the template
            st.text_area("Template", value=template_text, height=300, key="template_area")
            
            if st.button("Use This Template"):
                # Parse the template text
                parsed_data = parse_text_from_string(template_text)
                
                if parsed_data:
                    st.session_state.parsed_data = parsed_data
                    st.success(f"Successfully parsed {len(parsed_data)} lines of dialogue.")
                    
                    # Save story text for later display
                    st.session_state.story_text = template_text
        
        # Continue to next step
        if st.session_state.parsed_data:
            if st.button("Continue to Voice Setup ➡️"):
                st.session_state.current_step = 2
                st.rerun()
                
        # Step 2: Voice Setup
        if st.session_state.current_step >= 2:
            # Update progress steps
            st.markdown("""
            <div class="step-container">
                <div class="step-line"></div>
                <div class="step">1</div>
                <div class="step active">2</div>
                <div class="step">3</div>
                <div class="step">4</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Step 2: Voice Setup")
            
            # Extract unique characters
            characters = list(set([item["character"] for item in st.session_state.parsed_data]))
            
            # Voice model selection based on provider
            if api_provider == "OpenAI TTS":
                # OpenAI voice selection
                st.markdown("""
                <div class="feature-card">
                    <h3 style="margin-top:0; color:#6C63FF;">🗣️ Assign Voices to Characters</h3>
                    <p>Select an OpenAI voice for each character in your dialogue.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Initialize character_voices if not already set
                if not st.session_state.character_voices:
                    st.session_state.character_voices = {}
                
                # Voice settings (speed, pitch)
                col1, col2 = st.columns(2)
                with col1:
                    speed = st.slider("Speech Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
                    st.session_state.voice_settings["speed"] = speed
                    
                # Assign voices to characters
                for character in characters:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        selected_voice = st.selectbox(
                            f"Voice for {character}",
                            list(openai_voice_models.keys()),
                            key=f"voice_{character}"
                        )
                    
                    voice_id = openai_voice_models[selected_voice]
                    st.session_state.character_voices[character] = {
                        "provider": "openai",
                        "voice_id": voice_id,
                        "voice_name": selected_voice
                    }
                
            elif api_provider == "ElevenLabs":
                # ElevenLabs voice selection
                st.markdown("""
                <div class="feature-card">
                    <h3 style="margin-top:0; color:#6C63FF;">🗣️ Assign Voices to Characters</h3>
                    <p>Select an ElevenLabs voice for each character in your dialogue.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Check if voices have been fetched
                if not st.session_state.elevenlabs_voice_models:
                    st.warning("Please fetch ElevenLabs voices first using the button in the API Setup section.")
                else:
                    # Initialize character_voices if not already set
                    if not st.session_state.character_voices:
                        st.session_state.character_voices = {}
                    
                    # Voice settings (stability, similarity boost)
                    col1, col2 = st.columns(2)
                    with col1:
                        stability = st.slider("Stability", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
                        st.session_state.voice_settings["stability"] = stability
                    with col2:
                        similarity_boost = st.slider("Similarity Boost", min_value=0.0, max_value=1.0, value=0.75, step=0.1)
                        st.session_state.voice_settings["similarity_boost"] = similarity_boost
                    
                    # Assign voices to characters
                    for character in characters:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            selected_voice = st.selectbox(
                                f"Voice for {character}",
                                list(st.session_state.elevenlabs_voice_models.keys()),
                                key=f"voice_{character}"
                            )
                        
                        voice_id = st.session_state.elevenlabs_voice_models[selected_voice]
                        st.session_state.character_voices[character] = {
                            "provider": "elevenlabs",
                            "voice_id": voice_id,
                            "voice_name": selected_voice
                        }
            
            # Enhanced Background Music Section
            st.markdown("""
            <div class="feature-card">
                <h3 style="margin-top:0; color:#FF6584;">🎵 Enhanced Background Audio</h3>
                <p>Add ambient music, sound effects, and dynamic volume control to enhance your audio narration.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Background Track Selection
            track_category = st.radio(
                "Select background track category:",
                ["None", "Ambient", "Music", "Sound Effects", "Multiple Tracks"],
                horizontal=True
            )
            
            # Initialize BACKGROUND_TRACKS if not already defined
            if 'BACKGROUND_TRACKS' not in st.session_state:
                # Define background track categories
                st.session_state.BACKGROUND_TRACKS = {
                    "ambient": {
                        "calm": [
                            {"name": "Forest Morning", "duration": "2:30", "category": "ambient", "mood": "calm", "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_270f8b3ef8.mp3"},
                            {"name": "Ocean Waves", "duration": "3:12", "category": "ambient", "mood": "calm", "url": "https://cdn.pixabay.com/download/audio/2021/08/09/audio_c741830750.mp3"}
                        ],
                        "dramatic": [
                            {"name": "Storm Approaching", "duration": "2:47", "category": "ambient", "mood": "dramatic", "url": "https://cdn.pixabay.com/download/audio/2022/01/27/audio_d1f8f68c89.mp3"},
                            {"name": "Mystery Atmosphere", "duration": "1:55", "category": "ambient", "mood": "dramatic", "url": "https://cdn.pixabay.com/download/audio/2021/12/16/audio_a49a19a1d6.mp3"}
                        ]
                    },
                    "music": {
                        "uplifting": [
                            {"name": "Piano Dreams", "duration": "2:18", "category": "music", "mood": "uplifting", "url": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_ba43077db4.mp3"},
                            {"name": "Happy Guitar", "duration": "1:49", "category": "music", "mood": "uplifting", "url": "https://cdn.pixabay.com/download/audio/2022/09/04/audio_ea766c5efd.mp3"}
                        ],
                        "melancholic": [
                            {"name": "Sad Violin", "duration": "3:22", "category": "music", "mood": "melancholic", "url": "https://cdn.pixabay.com/download/audio/2021/11/25/audio_cb31fa4a8e.mp3"},
                            {"name": "Reflective Piano", "duration": "2:36", "category": "music", "mood": "melancholic", "url": "https://cdn.pixabay.com/download/audio/2022/04/27/audio_aac1f31da1.mp3"}
                        ]
                    },
                    "sound_effects": {
                        "nature": [
                            {"name": "Birds Chirping", "duration": "0:42", "category": "sound_effects", "mood": "nature", "url": "https://cdn.pixabay.com/download/audio/2021/09/06/audio_28e3fb4bb3.mp3"},
                            {"name": "Waterfall", "duration": "0:56", "category": "sound_effects", "mood": "nature", "url": "https://cdn.pixabay.com/download/audio/2021/08/09/audio_d1a14c149c.mp3"}
                        ],
                        "urban": [
                            {"name": "City Traffic", "duration": "1:10", "category": "sound_effects", "mood": "urban", "url": "https://cdn.pixabay.com/download/audio/2021/08/09/audio_cf394491c7.mp3"},
                            {"name": "Cafe Ambience", "duration": "1:22", "category": "sound_effects", "mood": "urban", "url": "https://cdn.pixabay.com/download/audio/2022/02/07/audio_bd3cf39d23.mp3"}
                        ]
                    }
                }
            
            # Create a local reference to the background tracks
            BACKGROUND_TRACKS = st.session_state.BACKGROUND_TRACKS
            
            selected_tracks = []
            
            if track_category != "None":
                if track_category == "Multiple Tracks":
                    # Multi-track selection
                    with st.expander("Ambient Tracks"):
                        for mood in BACKGROUND_TRACKS["ambient"]:
                            st.markdown(f"**{mood.title()} Ambient**")
                            for i, track in enumerate(BACKGROUND_TRACKS["ambient"][mood]):
                                track_selected = st.checkbox(
                                    f"{track['name']} ({track['duration']})",
                                    key=f"track_ambient_{mood}_{i}"
                                )
                                if track_selected:
                                    selected_tracks.append(track)
                    
                    with st.expander("Music Tracks"):
                        for mood in BACKGROUND_TRACKS["music"]:
                            st.markdown(f"**{mood.title()} Music**")
                            for i, track in enumerate(BACKGROUND_TRACKS["music"][mood]):
                                track_selected = st.checkbox(
                                    f"{track['name']} ({track['duration']})",
                                    key=f"track_music_{mood}_{i}"
                                )
                                if track_selected:
                                    selected_tracks.append(track)
                    
                    with st.expander("Sound Effects"):
                        for mood in BACKGROUND_TRACKS["sound_effects"]:
                            st.markdown(f"**{mood.title()} Sounds**")
                            for i, track in enumerate(BACKGROUND_TRACKS["sound_effects"][mood]):
                                track_selected = st.checkbox(
                                    f"{track['name']} ({track['duration']})",
                                    key=f"track_sfx_{mood}_{i}"
                                )
                                if track_selected:
                                    selected_tracks.append(track)
                else:
                    # Single category selection
                    # Convert "Sound Effects" to "sound_effects" to match the dictionary key
                    category_key = track_category.lower().replace(" ", "_")
                    moods = list(BACKGROUND_TRACKS[category_key].keys())
                    selected_mood = st.selectbox(f"Select {track_category} mood:", moods)
                    
                    # Use the category_key variable we created above
                    tracks = BACKGROUND_TRACKS[category_key][selected_mood]
                    selected_track_name = st.selectbox(
                        f"Select {selected_mood} {track_category}:",
                        [f"{t['name']} ({t['duration']})" for t in tracks]
                    )
                    
                    # Find the selected track
                    selected_track = next(
                        (t for t in tracks if f"{t['name']} ({t['duration']})" == selected_track_name),
                        None
                    )
                    
                    if selected_track:
                        selected_tracks.append(selected_track)
                        
                        # Preview button
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            if st.button("Preview", key=f"preview_{selected_track['name']}"):
                                with st.spinner(f"Loading {selected_track['name']}..."):
                                    # Download and play the selected track
                                    track_path = download_background_track(
                                        selected_track['url'],
                                        selected_track['name']
                                    )
                                    if track_path:
                                        st.audio(track_path)
                
                # Volume settings
                st.markdown("#### Volume Settings")
                
                if track_category == "Multiple Tracks":
                    # Individual track volume settings
                    if selected_tracks:
                        st.markdown("**Individual Track Volumes**")
                        track_volumes = {}
                        
                        for i, track in enumerate(selected_tracks):
                            track_volumes[track['name']] = st.slider(
                                f"{track['name']} volume", 
                                min_value=0.0, 
                                max_value=1.0, 
                                value=0.3,
                                step=0.05,
                                key=f"vol_{i}"
                            )
                    
                    # Volume automation
                    use_volume_automation = st.checkbox("Enable dynamic volume automation")
                    if use_volume_automation:
                        st.markdown("**Volume Automation Points**")
                        st.info("Define how the background volume changes over time during your narration.")
                        
                        # Initialize automation points if empty
                        if not st.session_state.background_volume_automation:
                            st.session_state.background_volume_automation = [
                                {"time": 0.0, "volume": 0.3},
                                {"time": 30.0, "volume": 0.3}
                            ]
                        
                        # Display automation points in a dataframe
                        automation_df = pd.DataFrame(st.session_state.background_volume_automation)
                        edited_df = st.data_editor(
                            automation_df,
                            column_config={
                                "time": st.column_config.NumberColumn(
                                    "Time (seconds)",
                                    min_value=0.0,
                                    format="%.1f"
                                ),
                                "volume": st.column_config.NumberColumn(
                                    "Volume (0-1)",
                                    min_value=0.0,
                                    max_value=1.0,
                                    format="%.2f"
                                )
                            },
                            num_rows="dynamic",
                            key="automation_editor"
                        )
                        
                        # Update automation points
                        if not edited_df.equals(automation_df):
                            st.session_state.background_volume_automation = edited_df.to_dict('records')
                else:
                    # Simple volume control
                    bg_volume = st.slider("Background volume", min_value=0.0, max_value=1.0, value=0.3, step=0.05)
                    st.session_state.bg_volume = bg_volume
            
            # Store selected tracks
            st.session_state.selected_background_tracks = selected_tracks
            
            # Display summary of selected tracks
            if selected_tracks:
                st.markdown("#### Selected Background Tracks")
                for track in selected_tracks:
                    st.markdown(f"- **{track['name']}** ({track['category']}, {track['mood']}, {track['duration']})")
            
            # Keep the original background_track variable for compatibility
            background_track = "None" if not selected_tracks else selected_tracks[0]["name"]
            st.session_state.background_track = background_track
            
            # Continue to next step
            if st.button("Continue to Audio Generation ➡️"):
                st.session_state.current_step = 3
                st.rerun()
        
        # Step 3: Generate Audio
        if st.session_state.current_step >= 3:
            # Update progress steps
            st.markdown("""
            <div class="step-container">
                <div class="step-line"></div>
                <div class="step">1</div>
                <div class="step">2</div>
                <div class="step active">3</div>
                <div class="step">4</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Step 3: Generate Audio")
            
            # Generate individual audio clips
            generate_button = st.button("🔊 Generate Voice Audio")
            
            if generate_button:
                # Clear previous audio files
                if st.session_state.audio_files:
                    cleanup_temp_files(st.session_state.audio_files)
                    st.session_state.audio_files = []
                
                # Generate audio for each dialogue line
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_lines = len(st.session_state.parsed_data)
                audio_files = []
                
                for i, item in enumerate(st.session_state.parsed_data):
                    character = item["character"]
                    dialogue = item["dialogue"]
                    emotion = item["emotion"]
                    
                    # Update progress
                    progress = (i + 1) / total_lines
                    progress_bar.progress(progress)
                    status_text.text(f"Generating audio for {character}: {dialogue[:50]}...")
                    
                    # Get voice settings for character
                    if character in st.session_state.character_voices:
                        voice_config = st.session_state.character_voices[character]
                        provider = voice_config["provider"]
                        voice_id = voice_config["voice_id"]
                        
                        # Generate audio based on provider
                        if provider == "openai":
                            # Generate OpenAI audio
                            audio_path = generate_voice_openai(
                                dialogue,
                                voice_id,
                                speed=st.session_state.voice_settings.get("speed", 1.0),
                                emotion=emotion
                            )
                        elif provider == "elevenlabs":
                            # Generate ElevenLabs audio
                            audio_path = generate_voice_elevenlabs(
                                dialogue,
                                voice_id,
                                stability=st.session_state.voice_settings.get("stability", 0.5),
                                similarity_boost=st.session_state.voice_settings.get("similarity_boost", 0.75),
                                emotion=emotion
                            )
                        
                        if audio_path:
                            audio_files.append(audio_path)
                    else:
                        st.warning(f"No voice assigned for character: {character}")
                
                # Store generated audio files
                st.session_state.audio_files = audio_files
                status_text.text(f"Generated audio for {len(audio_files)} dialogue lines.")
                
                # Continue to next step
                if audio_files:
                    st.session_state.current_step = 4
                    st.rerun()
        
        # Step 4: Final Export
        if st.session_state.current_step >= 4:
            # Update progress steps
            st.markdown("""
            <div class="step-container">
                <div class="step-line"></div>
                <div class="step">1</div>
                <div class="step">2</div>
                <div class="step">3</div>
                <div class="step active">4</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Step 4: Final Export")
            
            # Combine audio files if not already done
            if st.session_state.audio_files and not st.session_state.final_audio:
                with st.spinner("Combining audio files..."):
                    # Create temporary file for final audio
                    final_audio_path = tempfile.mktemp(suffix=".mp3")
                    
                    # Get background track if selected
                    bg_track = None  # Replace with actual background track path if implemented
                    
                    # Combine audio files
                    combined_path = concatenate_audio_files(
                        st.session_state.audio_files,
                        final_audio_path,
                        background_track=bg_track,
                        bg_volume=st.session_state.bg_volume
                    )
                    
                    if combined_path:
                        st.session_state.final_audio = combined_path
                        st.success("Audio files combined successfully!")
            
            # Display final audio
            if st.session_state.final_audio:
                st.markdown("""
                <div class="audio-container">
                    <h3 style="margin-top:0; color:#6C63FF;">🎧 Your Generated Voice Narration</h3>
                </div>
                """, unsafe_allow_html=True)
                
                with open(st.session_state.final_audio, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes)
            
                # Display story text if available
                if st.session_state.story_text:
                    with st.expander("📝 View Your Story Text"):
                        st.markdown("""
                        <div class="story-text-container">
                        """, unsafe_allow_html=True)
                        
                        # Format and display the story text
                        lines = st.session_state.story_text.split('\n')
                        for line in lines:
                            if line.strip():
                                st.markdown(f"<p>{line}</p>", unsafe_allow_html=True)
                                
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Download button for final audio
                with open(st.session_state.final_audio, "rb") as f:
                    b64_audio = base64.b64encode(f.read()).decode()
                    
                download_filename = f"voice_narration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                download_link = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{download_filename}" style="display: inline-block; padding: 0.5rem 1rem; background: linear-gradient(120deg, #6C63FF 0%, #8B5CF6 100%); color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 600; margin-top: 1rem; box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25); transition: all 0.3s ease;">Download Voice Narration</a>'
                st.markdown(download_link, unsafe_allow_html=True)
                
                # Record download in analytics
                if st.session_state.current_project_id:
                    record_analytics_event(st.session_state.current_project_id, "download")
                
                # Project Management Section
                st.markdown("<hr>", unsafe_allow_html=True)
                st.subheader("📂 Project Management")
                
                # Tabs for Project Management
                project_tabs = st.tabs(["Save Project", "Load Project", "Analytics"])
                
                # Save Project Tab
                with project_tabs[0]:
                    st.markdown("""
                    <div class="feature-card">
                        <h3 style="margin-top:0; color:#6C63FF;">💾 Save Your Project</h3>
                        <p>Save your current project settings and audio to access later.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    project_name = st.text_input("Project Name", value=f"Voice Project {datetime.now().strftime('%Y-%m-%d')}")
                    include_audio = st.checkbox("Include audio files", value=True, help="Save generated audio files with the project (increases storage size)")
                    
                    save_col1, save_col2 = st.columns([1, 1])
                    with save_col1:
                        if st.button("💾 Save Project", use_container_width=True):
                            if save_project(project_name, include_audio):
                                st.success(f"Project '{project_name}' saved successfully!")
                                
                                # Record version in analytics
                                if st.session_state.current_project_id:
                                    record_analytics_event(
                                        st.session_state.current_project_id,
                                        "version",
                                        {"changes": "Project saved"}
                                    )
                
                # Load Project Tab
                with project_tabs[1]:
                    st.markdown("""
                    <div class="feature-card">
                        <h3 style="margin-top:0; color:#6C63FF;">📂 Load Saved Projects</h3>
                        <p>Continue working on a previously saved project.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.projects:
                        # Create project table for display
                        project_list = []
                        for project_id, project in st.session_state.projects.items():
                            project_list.append({
                                "ID": project_id,
                                "Name": project["name"],
                                "Created": project["date_created"],
                                "Modified": project["date_modified"]
                            })
                        
                        project_df = pd.DataFrame(project_list)
                        st.dataframe(project_df, use_container_width=True)
                        
                        # Project selection
                        selected_project_id = st.selectbox(
                            "Select Project to Load",
                            options=[p["ID"] for p in project_list],
                            format_func=lambda x: next((p["Name"] for p in project_list if p["ID"] == x), x)
                        )
                        
                        load_col1, load_col2 = st.columns([1, 1])
                        with load_col1:
                            if st.button("📂 Load Project", use_container_width=True):
                                if load_project(selected_project_id):
                                    st.success(f"Project '{st.session_state.projects[selected_project_id]['name']}' loaded successfully!")
                                    st.rerun()
                    else:
                        st.info("No saved projects found. Save a project first to see it here.")
                
                # Analytics Tab
                with project_tabs[2]:
                    st.markdown("""
                    <div class="feature-card">
                        <h3 style="margin-top:0; color:#6C63FF;">📊 Project Analytics</h3>
                        <p>View usage statistics and performance metrics for your projects.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.project_analytics:
                        # Project selection for analytics
                        analytics_projects = [(p_id, st.session_state.projects[p_id]["name"]) 
                                            for p_id in st.session_state.project_analytics.keys() 
                                            if p_id in st.session_state.projects]
                        
                        selected_analytics_project = st.selectbox(
                            "Select Project for Analytics",
                            options=[p[0] for p in analytics_projects],
                            format_func=lambda x: next((p[1] for p in analytics_projects if p[0] == x), x)
                        )
                        
                        if selected_analytics_project:
                            analytics = st.session_state.project_analytics[selected_analytics_project]
                            project_name = st.session_state.projects[selected_analytics_project]["name"]
                            
                            # Display basic metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Plays", analytics["plays"])
                            with col2:
                                st.metric("Downloads", analytics["downloads"])
                            with col3:
                                st.metric("Engagement Score", analytics["engagement_score"])
                            
                            # Display creation and last accessed dates
                            st.markdown(f"""
                            <div style="margin: 15px 0; padding: 10px 15px; background: linear-gradient(120deg, rgba(108, 99, 255, 0.1), rgba(255, 101, 132, 0.1)); 
                                      border-radius: 8px; border-left: 3px solid #6C63FF;">
                                <span style="color: #666;">Created:</span> <span style="color: #6C63FF; font-weight: 500;">{analytics["creation_date"]}</span> | 
                                <span style="color: #666;">Last Accessed:</span> <span style="color: #6C63FF; font-weight: 500;">{analytics["last_accessed"]}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # A/B Test Results
                            if analytics["ab_test_results"]:
                                st.subheader("A/B Test Results")
                                for i, test in enumerate(analytics["ab_test_results"]):
                                    with st.expander(f"Test: {test['test_name']} - {test['date']}"):
                                        st.markdown(f"**Winner:** {test['winner']}")
                                        
                                        # Display metrics in columns
                                        metrics = test.get("metrics", {})
                                        if metrics:
                                            st.markdown("**Metrics:**")
                                            metric_cols = st.columns(len(metrics))
                                            for i, (key, value) in enumerate(metrics.items()):
                                                with metric_cols[i]:
                                                    st.metric(key.replace("_", " ").title(), value)
                            
                            # Version History
                            if analytics["version_history"]:
                                st.subheader("Version History")
                                for version in analytics["version_history"]:
                                    st.markdown(f"""
                                    <div style="margin: 5px 0; padding: 8px 15px; background: rgba(255, 255, 255, 0.7); 
                                              border-radius: 6px; border-left: 2px solid #8B5CF6;">
                                        <span style="color: #6C63FF; font-weight: 600;">v{version['version']}</span> - 
                                        <span style="color: #666; font-size: 0.9em;">{version['date']}</span><br>
                                        <span>{version['changes']}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Add A/B Test button
                            if st.button("Set Up A/B Test"):
                                st.info("A/B Testing allows you to compare different versions of your audio to determine which performs better.")
                                
                                # A/B test setup form
                                test_name = st.text_input("Test Name", value=f"Test for {project_name}")
                                
                                # Test variant parameters
                                st.subheader("Variant A (Original)")
                                st.info("This is your current version")
                                
                                st.subheader("Variant B (Test)")
                                variant_b_type = st.radio("Change type for Variant B:", ["Voice", "Background", "Speed"])
                                
                                variant_b_data = {}
                                if variant_b_type == "Voice":
                                    # Voice selection for variant B
                                    variant_b_data["change_type"] = "voice"
                                    if st.session_state.api_provider == "openai":
                                        variant_b_data["voice"] = st.selectbox(
                                            "Select different voice for variant B",
                                            options=list(openai_voice_models.keys()),
                                            index=1
                                        )
                                elif variant_b_type == "Background":
                                    # Background track selection for variant B
                                    variant_b_data["change_type"] = "background"
                                    variant_b_data["volume"] = st.slider(
                                        "Background Volume for Variant B",
                                        min_value=0.1,
                                        max_value=1.0,
                                        value=0.4,
                                        step=0.1
                                    )
                                elif variant_b_type == "Speed":
                                    # Speed settings for variant B
                                    variant_b_data["change_type"] = "speed"
                                    variant_b_data["speed"] = st.slider(
                                        "Speech Speed for Variant B",
                                        min_value=0.8,
                                        max_value=1.5,
                                        value=1.2,
                                        step=0.1
                                    )
                                
                                if st.button("Run A/B Test"):
                                    with st.spinner("Running A/B test..."):
                                        variant_a_data = {"change_type": "original"}
                                        
                                        # Perform A/B test
                                        if perform_ab_test(
                                            selected_analytics_project,
                                            test_name,
                                            variant_a_data,
                                            variant_b_data
                                        ):
                                            st.success("A/B test completed! Check the Analytics tab for results.")
                                            st.rerun()
                    else:
                        st.info("No project analytics available. Save and use a project first to see analytics.")
                        
                # Reset button
                st.markdown("<hr>", unsafe_allow_html=True)
                if st.button("🔄 Start New Project"):
                    # Clean up temporary files
                    cleanup_temp_files(st.session_state.audio_files)
                    if st.session_state.final_audio:
                        cleanup_temp_files([st.session_state.final_audio])
                    
                    # Reset session state
                    st.session_state.parsed_data = []
                    st.session_state.character_voices = {}
                    st.session_state.audio_files = []
                    st.session_state.final_audio = None
                    st.session_state.current_step = 1
                    st.session_state.story_text = None
                    st.session_state.current_project_id = None
                    
                    st.rerun()
    
    # Voice Dubbing tab
    elif tab == "🌍 Voice Dubbing":
        # Show dubbing interface
        render_dubbing_interface()
        
    # About tab
    elif tab == "ℹ️ About":
        # Show about information and workflow diagram
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #6C63FF; margin-bottom: 1.5rem;">About VoiceCanvas</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="padding: 1.5rem; background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(255, 101, 132, 0.1) 100%); 
                  border-radius: 12px; margin-bottom: 2rem; border-left: 5px solid #6C63FF;">
            <h2 style="color: #6C63FF; font-size: 1.5rem; margin-bottom: 1rem;">What is VoiceCanvas?</h2>
            <p style="font-size: 1.1rem; line-height: 1.6;">
                VoiceCanvas is a powerful text-to-speech platform that transforms your written stories, dialogues, 
                and scripts into expressive voice narrations. With multiple voice providers and background audio options,
                you can create professional audio content for podcasts, audiobooks, animations, and more.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main Features
        st.markdown("""
        <h2 style="color: #6C63FF; margin-top: 2rem; margin-bottom: 1rem;">Key Features</h2>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="padding: 1rem; background-color: white; border-radius: 10px; height: 100%;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #6C63FF;">
                <h3 style="color: #6C63FF; font-size: 1.2rem;">✨ Voice Generation</h3>
                <ul style="margin-top: 0.8rem;">
                    <li>Convert text to natural-sounding speech</li>
                    <li>Auto-parse dialogue with character detection</li>
                    <li>Convert paragraphs to dialogue with AI</li>
                    <li>Assign unique voices to each character</li>
                    <li>Add expression and emotion to narration</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 1rem; background-color: white; border-radius: 10px; height: 100%;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #FF6584;">
                <h3 style="color: #FF6584; font-size: 1.2rem;">🌍 Voice Dubbing</h3>
                <ul style="margin-top: 0.8rem;">
                    <li>Translate audio between languages</li>
                    <li>Maintain original voice characteristics</li>
                    <li>Preserve emotional tone and inflection</li>
                    <li>Support for multiple target languages</li>
                    <li>Option to use different voices for dubbing</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Features
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 1rem; background-color: white; border-radius: 10px; height: 100%;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #4ECDC4;">
                <h3 style="color: #4ECDC4; font-size: 1.2rem;">🎵 Enhanced Audio</h3>
                <ul style="margin-top: 0.8rem;">
                    <li>Add background music tracks</li>
                    <li>Include ambient sound effects</li>
                    <li>Dynamic volume automation</li>
                    <li>Multiple track layering</li>
                    <li>Audio fine-tuning controls</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="padding: 1rem; background-color: white; border-radius: 10px; height: 100%;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #FFD166;">
                <h3 style="color: #FFD166; font-size: 1.2rem;">📂 Project Management</h3>
                <ul style="margin-top: 0.8rem;">
                    <li>Save and load projects</li>
                    <li>Export audio in multiple formats</li>
                    <li>Create project templates</li>
                    <li>Batch process multiple files</li>
                    <li>Version control for projects</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div style="padding: 1rem; background-color: white; border-radius: 10px; height: 100%;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #8A4FFF;">
                <h3 style="color: #8A4FFF; font-size: 1.2rem;">📊 Analytics</h3>
                <ul style="margin-top: 0.8rem;">
                    <li>Track project engagement</li>
                    <li>Perform A/B testing on voices</li>
                    <li>Compare audio variants</li>
                    <li>Audience feedback metrics</li>
                    <li>Quality improvement insights</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Application Workflow Diagram
        st.markdown("""
        <h2 style="color: #6C63FF; margin-top: 3rem; margin-bottom: 1.5rem;">Application Workflow</h2>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="width: 100%; padding: 1.5rem; background-color: white; border-radius: 12px;
                  box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
            <div style="text-align: center; font-weight: bold; margin-bottom: 1rem; color: #555;">
                VoiceCanvas Application Flow
            </div>
            
            <div style="display: flex; justify-content: center; overflow-x: auto; padding: 1rem 0;">
                <div style="min-width: 950px; position: relative;">
                    <!-- Step 1: Text Input -->
                    <div style="position: absolute; left: 0; top: 0; width: 180px; padding: 1rem; 
                              background-color: #F0EEFF; border: 1px solid #6C63FF; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #6C63FF; font-weight: bold; margin-bottom: 0.5rem;">
                            Step 1: Text Input
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Enter text or upload file
                        </div>
                    </div>
                    
                    <!-- Arrow 1 -->
                    <div style="position: absolute; left: 190px; top: 25px; width: 60px; height: 10px; 
                              background-color: #6C63FF;"></div>
                    <div style="position: absolute; left: 250px; top: 20px; border-top: 10px solid transparent;
                              border-bottom: 10px solid transparent; border-left: 15px solid #6C63FF;"></div>
                    
                    <!-- Step 2: Voice Setup -->
                    <div style="position: absolute; left: 275px; top: 0; width: 180px; padding: 1rem; 
                              background-color: #F0EEFF; border: 1px solid #6C63FF; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #6C63FF; font-weight: bold; margin-bottom: 0.5rem;">
                            Step 2: Voice Setup
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Assign voices to characters
                        </div>
                    </div>
                    
                    <!-- Arrow 2 -->
                    <div style="position: absolute; left: 465px; top: 25px; width: 60px; height: 10px; 
                              background-color: #6C63FF;"></div>
                    <div style="position: absolute; left: 525px; top: 20px; border-top: 10px solid transparent;
                              border-bottom: 10px solid transparent; border-left: 15px solid #6C63FF;"></div>
                    
                    <!-- Step 3: Audio Generation -->
                    <div style="position: absolute; left: 550px; top: 0; width: 180px; padding: 1rem; 
                              background-color: #F0EEFF; border: 1px solid #6C63FF; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #6C63FF; font-weight: bold; margin-bottom: 0.5rem;">
                            Step 3: Audio Generation
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Generate voice audio files
                        </div>
                    </div>
                    
                    <!-- Arrow 3 -->
                    <div style="position: absolute; left: 740px; top: 25px; width: 60px; height: 10px; 
                              background-color: #6C63FF;"></div>
                    <div style="position: absolute; left: 800px; top: 20px; border-top: 10px solid transparent;
                              border-bottom: 10px solid transparent; border-left: 15px solid #6C63FF;"></div>
                    
                    <!-- Step 4: Final Export -->
                    <div style="position: absolute; left: 825px; top: 0; width: 180px; padding: 1rem; 
                              background-color: #F0EEFF; border: 1px solid #6C63FF; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #6C63FF; font-weight: bold; margin-bottom: 0.5rem;">
                            Step 4: Final Export
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Combine and export audio
                        </div>
                    </div>
                    
                    <!-- API Integration -->
                    <div style="position: absolute; left: 230px; top: 120px; width: 180px; padding: 1rem; 
                              background-color: #FFF0F5; border: 1px solid #FF6584; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #FF6584; font-weight: bold; margin-bottom: 0.5rem;">
                            API Integration
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            OpenAI, ElevenLabs, Groq
                        </div>
                    </div>
                    
                    <!-- Arrow to API -->
                    <div style="position: absolute; left: 320px; top: 70px; width: 10px; height: 50px; 
                              background-color: #FF6584;"></div>
                    <div style="position: absolute; left: 315px; top: 120px; border-left: 10px solid transparent;
                              border-right: 10px solid transparent; border-top: 15px solid #FF6584;"></div>
                    
                    <!-- Background Audio -->
                    <div style="position: absolute; left: 460px; top: 120px; width: 180px; padding: 1rem; 
                              background-color: #F0FFF4; border: 1px solid #4ECDC4; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #4ECDC4; font-weight: bold; margin-bottom: 0.5rem;">
                            Background Audio
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Music, ambient sounds, SFX
                        </div>
                    </div>
                    
                    <!-- Arrow to Background -->
                    <div style="position: absolute; left: 550px; top: 70px; width: 10px; height: 50px; 
                              background-color: #4ECDC4;"></div>
                    <div style="position: absolute; left: 545px; top: 120px; border-left: 10px solid transparent;
                              border-right: 10px solid transparent; border-top: 15px solid #4ECDC4;"></div>
                    
                    <!-- Project Management -->
                    <div style="position: absolute; left: 690px; top: 120px; width: 180px; padding: 1rem; 
                              background-color: #FFFBEB; border: 1px solid #FFD166; border-radius: 8px; 
                              text-align: center;">
                        <div style="color: #FFD166; font-weight: bold; margin-bottom: 0.5rem;">
                            Project Management
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Save, load, analytics, sharing
                        </div>
                    </div>
                    
                    <!-- Arrow to Project Management -->
                    <div style="position: absolute; left: 780px; top: 70px; width: 10px; height: 50px; 
                              background-color: #FFD166;"></div>
                    <div style="position: absolute; left: 775px; top: 120px; border-left: 10px solid transparent;
                              border-right: 10px solid transparent; border-top: 15px solid #FFD166;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Technical Details
        st.markdown("""
        <h2 style="color: #6C63FF; margin-top: 3rem; margin-bottom: 1.5rem;">Technical Implementation</h2>
        """, unsafe_allow_html=True)
        
        tech_tab1, tech_tab2, tech_tab3 = st.tabs(["Core Functions", "Data Flow", "API Integration"])
        
        with tech_tab1:
            st.markdown("""
            ### Core Functions
            
            - **Text Parsing**: Processes input text to identify characters, dialogue, and emotions
            - **Voice Assignment**: Maps characters to selected voice models from different providers
            - **Audio Generation**: Converts text to speech with emotional inflection
            - **Audio Processing**: Mixes speech with background audio and applies effects
            - **Project Management**: Handles saving, loading, and versioning of projects
            """)
        
        with tech_tab2:
            st.markdown("""
            ### Data Flow
            
            1. **Input Stage**: 
               - Raw text input (manual, file upload, or template)
               - Parsing into structured dialogue data
               - Optional paragraph-to-dialogue conversion
            
            2. **Processing Stage**:
               - Character detection and voice assignment
               - Background audio selection
               - Audio generation for each dialogue line
               - Volume automation and effects processing
            
            3. **Output Stage**:
               - Combining individual audio files
               - Mixing with background tracks
               - Final export with metadata
               - Analytics collection and processing
            """)
        
        with tech_tab3:
            st.markdown("""
            ### API Integration
            
            The application integrates with multiple external services:
            
            - **OpenAI API** - Used for text-to-speech generation with their TTS models
            - **ElevenLabs API** - Provides highly realistic voice generation capabilities
            - **Groq API** - Powers the paragraph-to-dialogue conversion feature
            
            #### Error Handling
            
            The application implements robust error handling:
            - Validates API keys before making requests
            - Provides fallback options when external services fail
            - Graceful degradation of features when necessary
            - Clear user feedback about service status
            """)
        
        # Footer
        st.markdown("""
        <div style="text-align: center; margin-top: 4rem; padding: 2rem; 
                  background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(255, 101, 132, 0.1) 100%);
                  border-radius: 12px;">
            <div style="color: #6C63FF; font-weight: bold; font-size: 1.2rem;">
                VoiceCanvas
            </div>
            <div style="color: #666; margin-top: 0.5rem; font-size: 0.9rem;">
                Created with Streamlit and ❤️
            </div>
        </div>
        """, unsafe_allow_html=True)

# Render Voice Dubbing interface
def render_dubbing_interface():
    # API Setup section
    with st.expander("🔑 API Setup", expanded=False):
        st.markdown("""
        <div class="feature-card">
            <h3 style="margin-top:0; color:#6C63FF;">🔐 API Configuration</h3>
            <p>Set up your voice provider API keys to enable voice dubbing.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API key inputs
        col1, col2 = st.columns(2)
        
        with col1:
            openai_key = st.text_input(
                "Enter your OpenAI API key",
                value=st.session_state.openai_key if st.session_state.openai_key else "",
                type="password",
                key="openai_key_dubbing"
            )
            if openai_key:
                st.session_state.openai_key = openai_key
                st.success("OpenAI API key set successfully!")
            
            # OpenAI voice selection
            openai_voice = st.selectbox(
                "Select OpenAI voice for dubbing",
                list(openai_voice_models.keys()),
                key="openai_voice_dubbing"
            )
            st.session_state.openai_voice = openai_voice_models[openai_voice]
        
        with col2:
            elevenlabs_key = st.text_input(
                "Enter your ElevenLabs API key",
                value=st.session_state.elevenlabs_key if st.session_state.elevenlabs_key else "",
                type="password",
                key="elevenlabs_key_dubbing"
            )
            if elevenlabs_key:
                st.session_state.elevenlabs_key = elevenlabs_key
                st.success("ElevenLabs API key set successfully!")
            
            # Fetch ElevenLabs voices
            if st.button("Fetch ElevenLabs Voices", key="fetch_elevenlabs_dubbing"):
                with st.spinner("Fetching voices from ElevenLabs..."):
                    voices = fetch_elevenlabs_voices()
                    if voices:
                        st.session_state.elevenlabs_voice_models = voices
                        st.success(f"Successfully fetched {len(voices)} voices from ElevenLabs!")
                    else:
                        st.error("Failed to fetch voices from ElevenLabs.")
    
    # Main interface section
    st.subheader("🌐 Voice Dubbing")
    
    # Dubbing provider selection with enhanced UI
    st.markdown("""
    <div class="feature-card">
        <h3 style="margin-top:0; color:#6C63FF;">🎙️ Select Dubbing Provider</h3>
        <p>Choose which service to use for dubbing your audio to another language.</p>
    </div>
    """, unsafe_allow_html=True)
    
    dubbing_provider = st.radio(
        "Dubbing Provider",
        ["OpenAI", "ElevenLabs"],
        horizontal=True
    )
    
    # Target language selection with enhanced UI
    st.markdown("""
    <div class="feature-card">
        <h3 style="margin-top:0; color:#6C63FF;">🌍 Select Target Language</h3>
        <p>Choose the language you want to dub your audio into.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two-column language selection
    col1, col2 = st.columns(2)
    
    with col1:
        target_language_group1 = st.radio(
            "European Languages",
            ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Polish", "Dutch"]
        )
    
    with col2:
        target_language_group2 = st.radio(
            "Asian & Other Languages",
            ["Hindi", "Arabic", "Chinese", "Japanese", "Korean", "Russian", "Turkish"]
        )
    
    # Determine which language was selected
    if target_language_group1 != "English":
        target_language = target_language_group1
    else:
        target_language = target_language_group2
    
    # Display the selected language with an eye-catching style
    st.markdown(f"""
    <div style="margin: 15px 0; padding: 10px 15px; background: linear-gradient(120deg, rgba(108, 99, 255, 0.1), rgba(255, 101, 132, 0.1)); 
               border-radius: 8px; border-left: 3px solid #6C63FF; font-weight: 500;">
        🎯 Selected language for dubbing: <span style="color: #6C63FF; font-weight: 700;">{target_language}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Language code mapping
    language_code_map = {
        "English": "en", "Spanish": "es", "French": "fr", "German": "de", 
        "Italian": "it", "Portuguese": "pt", "Polish": "pl", "Hindi": "hi", 
        "Arabic": "ar", "Chinese": "zh", "Japanese": "ja", "Korean": "ko", 
        "Russian": "ru", "Turkish": "tr", "Dutch": "nl"
    }
    
    # Selected language code
    lang_code = language_code_map.get(target_language, "en")
    
    # Voice selection based on provider
    voice_id = None
    if dubbing_provider == "ElevenLabs":
        if st.session_state.elevenlabs_voice_models:
            selected_voice = st.selectbox(
                "Select ElevenLabs voice for dubbing:", 
                options=list(st.session_state.elevenlabs_voice_models.keys()),
                index=0
            )
            voice_id = st.session_state.elevenlabs_voice_models[selected_voice]
        else:
            st.warning("Please fetch ElevenLabs voices first using the button in the API Setup section.")
    
    # Audio upload with enhanced UI
    st.markdown("""
    <div class="feature-card">
        <h3 style="margin-top:0; color:#6C63FF;">🎵 Upload Your Audio</h3>
        <p>Upload an audio file (MP3, WAV, or OGG format) that you'd like to dub into another language.</p>
    </div>
    """, unsafe_allow_html=True)
    uploaded_audio = st.file_uploader("", type=["mp3", "wav", "ogg"])
    
    if uploaded_audio:
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_audio.name.split(".")[-1]) as temp_file:
            temp_file.write(uploaded_audio.getvalue())
            audio_path = temp_file.name
            
        st.session_state.uploaded_audio = audio_path
        
        # Display original audio
        st.subheader("Original Audio")
        st.audio(uploaded_audio)
    
    # Dubbing process - enhanced button style
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_dubbing = st.button("🎬 Start Dubbing Process", use_container_width=True)
    
    if st.session_state.uploaded_audio and start_dubbing:
        # Validate provider-specific requirements
        if dubbing_provider == "OpenAI":
            if not st.session_state.openai_key:
                st.error("Please enter your OpenAI API key.")
            else:
                with st.spinner(f"Dubbing audio to {target_language} with OpenAI..."):
                    dubbed_audio_path = openai_dubbing(
                        st.session_state.uploaded_audio, 
                        lang_code, 
                        st.session_state.openai_voice
                    )
                    
                    if dubbed_audio_path:
                        st.session_state.dubbed_audio = dubbed_audio_path
                        st.success(f"Audio successfully dubbed to {target_language} with OpenAI!")
                        st.rerun()
        
        elif dubbing_provider == "ElevenLabs":
            if not st.session_state.elevenlabs_key:
                st.error("Please enter your ElevenLabs API key.")
            elif not voice_id:
                st.error("Please select a voice for dubbing.")
            else:
                with st.spinner(f"Dubbing audio to {target_language} with ElevenLabs..."):
                    dubbed_audio_path = elevenlabs_dubbing(
                        st.session_state.uploaded_audio, 
                        lang_code, 
                        voice_id
                    )
                    
                    if dubbed_audio_path:
                        st.session_state.dubbed_audio = dubbed_audio_path
                        st.success(f"Audio successfully dubbed to {target_language} with ElevenLabs!")
                        st.rerun()
    
    # Display dubbed audio if available
    if st.session_state.dubbed_audio:
        st.subheader(f"Dubbed Audio ({target_language})")
        with open(st.session_state.dubbed_audio, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes)
            
        # Download button for dubbed audio
        with open(st.session_state.dubbed_audio, "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode()
            
        download_filename = f"dubbed_audio_{target_language.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        download_link = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{download_filename}" style="display: inline-block; padding: 0.5rem 1rem; background: linear-gradient(120deg, #6C63FF 0%, #8B5CF6 100%); color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 600; margin-top: 1rem; box-shadow: 0 4px 12px rgba(108, 99, 255, 0.25); transition: all 0.3s ease;">Download Dubbed Audio</a>'
        st.markdown(download_link, unsafe_allow_html=True)
        
    # Reset button with improved styling
    st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(108, 99, 255, 0.5), rgba(255,255,255,0));'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        reset_button = st.button("🔄 Reset Dubbing Process", use_container_width=True, type="secondary")
    
    if reset_button:
        if st.session_state.uploaded_audio:
            try:
                os.remove(st.session_state.uploaded_audio)
            except:
                pass
        if st.session_state.dubbed_audio:
            try:
                os.remove(st.session_state.dubbed_audio)
            except:
                pass
                
        st.session_state.uploaded_audio = None
        st.session_state.dubbed_audio = None
        st.rerun()

if __name__ == "__main__":
    main()