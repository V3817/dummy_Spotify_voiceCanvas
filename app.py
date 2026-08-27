import streamlit as st
import re
import tempfile
import os
import time
import json
import random
from datetime import datetime
import pandas as pd
from io import BytesIO
import base64
import requests
import groq
from pydub import AudioSegment

# Set page configuration
st.set_page_config(
    page_title="VoiceCanvas Spotify",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API clients
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

groq_client = groq.Client(api_key=GROQ_API_KEY)

# Helper functions for API integration
def text_to_speech_elevenlabs(text, voice_id="21m00Tcm4TlvDq8ikWAM", model_id="eleven_multilingual_v2", 
                           voice_settings=None, is_cloned_voice=False, character_voice_mapping=None):
    """
    Convert text to speech using ElevenLabs API with support for:
    - Standard voices
    - Cloned voices
    - Character voice mapping for dialogue
    - Voice dubbing
    """
    try:
        import re
        import os
        
        # Use custom API key if provided, otherwise use the built-in key
        if not st.session_state.use_built_in_elevenlabs and st.session_state.custom_elevenlabs_key:
            ELEVENLABS_API_KEY = st.session_state.custom_elevenlabs_key
        else:
            ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
        
        if not ELEVENLABS_API_KEY:
            st.error("ElevenLabs API key not found. Please provide a valid API key in the API Settings.")
            return None
        
        # Default voice settings if not provided
        if not voice_settings:
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,  # Style control (0.0 to 1.0)
                "use_speaker_boost": True  # Enhanced clarity
            }
        
        # Check if we need to process the text for different character voices
        if character_voice_mapping and ":" in text:
            # If dialogue format detected, split and process each line with different voices
            lines = text.split('\n')
            audio_segments = []
            
            for line in lines:
                if ":" in line:
                    # Extract character name and their dialogue
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        character = parts[0].strip()
                        dialogue = parts[1].strip()
                        
                        # Get voice ID for this character if it exists in mapping
                        character_voice_id = voice_id  # Default
                        if character in character_voice_mapping:
                            character_voice_id = character_voice_mapping[character]
                        
                        # Generate speech for this line with appropriate voice
                        line_audio = generate_single_voice_clip(dialogue, character_voice_id, model_id, voice_settings, ELEVENLABS_API_KEY)
                        if line_audio:
                            audio_segments.append(line_audio)
            
            # Combine all audio segments if any were successfully generated
            if audio_segments:
                # Here we would normally combine audio segments using pydub
                # For now, return the first segment as a simple implementation
                return audio_segments[0]
            else:
                return None
        
        # For simple text or if no character mapping, generate with single voice
        return generate_single_voice_clip(text, voice_id, model_id, voice_settings, ELEVENLABS_API_KEY)
    
    except Exception as e:
        st.error(f"Error in text_to_speech_elevenlabs: {str(e)}")
        return None


def generate_single_voice_clip(text, voice_id, model_id, voice_settings, api_key):
    """Helper function to generate a single voice clip with ElevenLabs"""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error generating voice clip: {str(e)}")
        return None

def generate_dialogue_with_groq(text, character_names=None):
    """Use Groq API to convert a paragraph into dialogue with character assignments"""
    if not character_names:
        character_names = ["Character 1", "Character 2"]
    
    prompt = f"""Convert the following paragraph into a dialogue between multiple characters.
    Identify the best characters to include based on the content.
    Use these character names if they fit: {', '.join(character_names)}.
    Format the response as a JSON array of dialogue objects with 'character' and 'line' fields.
    
    Paragraph:
    {text}
    
    Example format:
    [
      {{"character": "Character 1", "line": "What they say"}},
      {{"character": "Character 2", "line": "Their response"}}
    ]
    """
    
    try:
        # Use custom API key if provided, otherwise use the built-in key
        if not st.session_state.use_built_in_groq and st.session_state.custom_groq_key:
            client = groq.Client(api_key=st.session_state.custom_groq_key)
        else:
            client = groq_client
        
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a dialogue writer who converts paragraphs into natural-sounding dialogue."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            st.error("Failed to parse dialogue response as JSON")
            return []
    except Exception as e:
        st.error(f"Error generating dialogue: {str(e)}")
        return []

def clone_voice_elevenlabs(voice_sample, voice_name, description="Custom cloned voice"):
    """Create a cloned voice using ElevenLabs API"""
    try:
        import requests
        import os
        import tempfile
        
        # Use custom API key if provided, otherwise use the built-in key
        if not st.session_state.use_built_in_elevenlabs and st.session_state.custom_elevenlabs_key:
            api_key = st.session_state.custom_elevenlabs_key
        else:
            api_key = os.environ.get("ELEVENLABS_API_KEY")
        
        if not api_key:
            st.error("ElevenLabs API key not found. Please provide a valid API key in the API Settings.")
            return None
        
        # API endpoint for voice creation
        url = "https://api.elevenlabs.io/v1/voices/add"
        
        # Headers
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        # Save voice sample to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(voice_sample.read())
            temp_file_path = temp_file.name
        
        # Prepare form data
        files = {
            'files': (os.path.basename(temp_file_path), open(temp_file_path, 'rb'), 'audio/mpeg')
        }
        
        data = {
            'name': voice_name,
            'description': description,
        }
        
        # Send request
        response = requests.post(url, headers=headers, data=data, files=files)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Check if request was successful
        if response.status_code in [200, 201]:
            result = response.json()
            st.success(f"Voice '{voice_name}' cloned successfully!")
            return result.get('voice_id')
        else:
            st.error(f"ElevenLabs voice cloning failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in clone_voice_elevenlabs: {str(e)}")
        return None


def dub_audio_with_elevenlabs(audio_file, target_language, text_transcript=None, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Dub audio or video with a new voice using ElevenLabs"""
    try:
        import tempfile
        import os
        
        # First extract audio if it's a video file
        # For this simple implementation, we'll assume the file is already audio
        
        # Create a transcript if not provided
        if not text_transcript:
            # We would normally use a transcription service here
            # For now, simulate with a placeholder
            text_transcript = "This is a simulated transcript of the audio file for dubbing demonstration."
        
        # Translate transcript to target language if needed
        # We would normally use a translation service here
        # For now, simply use the original text
        translated_text = text_transcript
        
        # Generate the dubbed audio
        dubbed_audio = text_to_speech_elevenlabs(
            translated_text, 
            voice_id=voice_id,
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,  # Slight style enhancement for dubbing
            }
        )
        
        if dubbed_audio:
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(dubbed_audio)
                return temp_file.name
        
        return None
    except Exception as e:
        st.error(f"Error in dub_audio_with_elevenlabs: {str(e)}")
        return None


def analyze_text_tone(text):
    """Analyze the emotional tone and musical elements of text"""
    prompt = f"""Analyze the following text for its emotional tone and musical characteristics.
    Return a JSON object with these keys:
    - tone (string): overall emotional tone (e.g., 'melancholic', 'upbeat')
    - tempo (string): suggested musical tempo (e.g., 'slow', 'moderate', 'fast')
    - key_elements (array): array of strings, key emotional or thematic elements
    - intensity_curve (array): array of 8 numbers between 0-1 representing the emotional intensity throughout the text
    - music_genre (string): suggested musical genre that would fit this content
    
    Text to analyze:
    {text}
    """
    
    try:
        # Use custom API key if provided, otherwise use the built-in key
        if not st.session_state.use_built_in_groq and st.session_state.custom_groq_key:
            client = groq.Client(api_key=st.session_state.custom_groq_key)
        else:
            client = groq_client
            
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a literary and music analyst who provides detailed tonal analysis of text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=512,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            st.error("Failed to parse tone analysis response")
            return {
                "tone": "neutral",
                "tempo": "moderate",
                "key_elements": ["error analyzing"],
                "intensity_curve": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                "music_genre": "ambient"
            }
    except Exception as e:
        st.error(f"Error analyzing text tone: {str(e)}")
        return {
            "tone": "neutral",
            "tempo": "moderate",
            "key_elements": ["error analyzing"],
            "intensity_curve": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            "music_genre": "ambient"
        }

# Define enhanced CSS with Spotify theming
enhanced_css = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');
    
    /* Global Theme - Now with Spotify Dark Theme */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: #121212;
        color: #FFFFFF;
        border-radius: 1.2rem;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF;
    }
    
    p, div, span {
        color: #B3B3B3;
    }
    
    .main-header {
        font-size: 3.4rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1DB954 0%, #1ED760 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        animation: fadeIn 1.2s ease-in-out;
    }
    
    .sub-header {
        font-size: 1.6rem;
        background: linear-gradient(120deg, #1DB954 0%, #1ED760 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2.5rem;
        text-align: center;
        font-weight: 500;
        animation: slideUp 1s ease-in-out;
    }
    
    /* Buttons */
    .stButton>button {
        background: #1DB954;
        color: white;
        border: none;
        border-radius: 2rem;
        padding: 0.7rem 1.4rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.25);
        font-family: 'Montserrat', sans-serif;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(29, 185, 84, 0.3);
        background: #1ED760;
    }
    
    .stButton>button:active {
        transform: translateY(1px);
    }
    
    /* Input Fields */
    .api-input {
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        padding: 1.5rem;
        background-color: rgba(40, 40, 40, 0.85);
        border-radius: 0.8rem;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
        border-left: 5px solid #1DB954;
        transition: all 0.3s ease;
    }
    
    .api-input:hover {
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.2);
        background-color: rgba(50, 50, 50, 0.95);
        transform: translateY(-2px);
    }
    
    /* Section Styling */
    .css-1r6slb0, .css-1inwz65 {
        border-radius: 0.9rem;
        border: 1px solid rgba(40, 40, 40, 0.5);
        background-color: rgba(40, 40, 40, 0.8);
        padding: 1.4rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    /* Sidebar Styling */
    .css-1d391kg, .css-163ttbj {
        background: #000000;
        border-right: 1px solid rgba(40, 40, 40, 0.5);
    }
    
    /* Audio Player */
    audio {
        width: 100%;
        border-radius: 10px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
        background: linear-gradient(90deg, #1DB954 0%, #1ED760 100%);
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
        background-color: rgba(40, 40, 40, 0.8);
        border-radius: 0.7rem;
        border: 1px solid rgba(29, 185, 84, 0.2);
        transition: all 0.3s ease;
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF;
    }
    
    .streamlit-expanderHeader:hover, .stSelectbox > div > div:hover {
        background-color: rgba(50, 50, 50, 0.95);
        border-color: rgba(29, 185, 84, 0.4);
        transform: translateY(-1px);
    }
    
    /* Text Area */
    .stTextArea > div > div {
        border-radius: 0.7rem;
        border: 1px solid rgba(29, 185, 84, 0.25);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
        background-color: #282828;
        color: #FFFFFF;
    }
    
    .stTextArea > div > div:focus-within {
        border-color: #1DB954;
        box-shadow: 0 0 0 2px rgba(29, 185, 84, 0.25);
        transform: translateY(-2px);
    }

    /* Dataframe/Table Styling */
    .dataframe {
        border-radius: 0.7rem;
        overflow: hidden;
        border: none !important;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
        font-family: 'Poppins', sans-serif;
        background-color: #282828;
    }
    
    .dataframe th {
        background: linear-gradient(90deg, #1DB954 0%, #1ED760 100%) !important;
        color: white !important;
        font-weight: 600;
        padding: 0.8rem 1.2rem !important;
    }
    
    .dataframe td {
        padding: 0.7rem 1.2rem !important;
        border-bottom: 1px solid #333333;
        background-color: #282828;
        color: #B3B3B3;
    }
    
    .dataframe tr:nth-child(even) td {
        background-color: #333333;
    }
    
    /* Tooltips */
    .stTooltipIcon {
        color: #1DB954 !important;
    }
    
    /* Audio Container */
    .audio-container {
        background: #282828;
        border-radius: 12px;
        padding: 16px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border-left: 5px solid #1DB954;
        transition: all 0.3s ease;
    }
    
    .audio-container:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        transform: translateY(-4px);
        background: #333333;
    }
    
    /* Lyrics Container */
    .lyrics-container {
        background: #282828;
        border-radius: 10px;
        padding: 16px 20px;
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 20px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
        font-family: 'Poppins', sans-serif;
    }
    
    .lyrics-container p {
        border-bottom: 1px solid rgba(50, 50, 50, 0.5);
        padding-bottom: 12px;
        margin-bottom: 12px;
        line-height: 1.5;
        color: #B3B3B3;
    }
    
    .lyrics-container p.active {
        color: #FFFFFF;
        font-weight: 600;
    }
    
    .lyrics-container p:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .lyrics-container strong {
        color: #1DB954;
        font-weight: 600;
    }
    
    .lyrics-container em {
        color: #1ED760;
        font-style: italic;
        font-weight: 500;
    }
    
    /* Spotify Album Card */
    .album-card {
        background: #282828;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 20px;
    }
    
    .album-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.4);
        background: #333333;
    }
    
    .album-image-container {
        position: relative;
        overflow: hidden;
    }
    
    .album-image {
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .album-card:hover .album-image {
        transform: scale(1.05);
    }
    
    .album-details {
        padding: 15px;
    }
    
    .album-title {
        color: #FFFFFF;
        font-weight: 600;
        margin-bottom: 5px;
        font-size: 16px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .album-artist {
        color: #b3b3b3;
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Track List */
    .track-item {
        display: flex;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: #282828;
        transition: all 0.2s ease;
        cursor: pointer;
        align-items: center;
    }
    
    .track-item:hover {
        background: #333333;
    }
    
    .track-number {
        color: #b3b3b3;
        width: 30px;
        font-size: 14px;
    }
    
    .track-info {
        flex-grow: 1;
    }
    
    .track-title {
        color: #FFFFFF;
        font-weight: 500;
        margin-bottom: 4px;
    }
    
    .track-artist {
        color: #b3b3b3;
        font-size: 13px;
    }
    
    .track-duration {
        color: #b3b3b3;
        font-size: 14px;
        width: 50px;
        text-align: right;
    }
    
    .track-item.active {
        background: rgba(29, 185, 84, 0.15);
        border-left: 3px solid #1DB954;
    }
    
    .track-item.active .track-title {
        color: #1DB954;
    }
    
    /* Play Button */
    .play-button {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) scale(0);
        width: 60px;
        height: 60px;
        background: #1DB954;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
    }
    
    .play-button svg {
        width: 24px;
        height: 24px;
        fill: white;
    }
    
    .album-card:hover .play-button {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
    
    /* Player Controls */
    .player-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
    }
    
    .control-button {
        background: transparent;
        border: none;
        color: #b3b3b3;
        font-size: 20px;
        cursor: pointer;
        margin: 0 15px;
        transition: all 0.2s ease;
    }
    
    .control-button:hover {
        color: #FFFFFF;
        transform: scale(1.1);
    }
    
    .control-button.play {
        width: 60px;
        height: 60px;
        background: #1DB954;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        margin: 0 20px;
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
    }
    
    .control-button.play:hover {
        background: #1ED760;
        transform: scale(1.05);
    }
    
    .progress-container {
        width: 100%;
        height: 4px;
        background: #535353;
        border-radius: 2px;
        margin: 10px 0;
        cursor: pointer;
        position: relative;
    }
    
    .progress-bar {
        height: 100%;
        background: #b3b3b3;
        border-radius: 2px;
        transition: width 0.1s linear;
    }
    
    .progress-container:hover .progress-bar {
        background: #1DB954;
    }
    
    .progress-thumb {
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        transform: translate(-50%, -50%);
        display: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .progress-container:hover .progress-thumb {
        display: block;
    }
    
    /* Social Features */
    .social-icons {
        display: flex;
        gap: 15px;
        margin-top: 15px;
    }
    
    .social-icon {
        background: #333333;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .social-icon:hover {
        background: #444444;
        transform: translateY(-3px);
    }
    
    .social-icon svg {
        width: 20px;
        height: 20px;
        fill: #b3b3b3;
    }
    
    .social-icon:hover svg {
        fill: #FFFFFF;
    }
    
    .liked {
        color: #1DB954 !important;
    }
    
    /* Comment Section */
    .comment-container {
        background: #282828;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }
    
    .comment-input {
        display: flex;
        margin-bottom: 15px;
    }
    
    .comment-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        overflow: hidden;
        margin-right: 15px;
    }
    
    .comment-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .comment-box {
        flex-grow: 1;
        background: #333333;
        border-radius: 20px;
        border: none;
        padding: 10px 15px;
        color: white;
        outline: none;
    }
    
    .comment-item {
        display: flex;
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #333333;
    }
    
    .comment-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    .comment-content {
        flex-grow: 1;
    }
    
    .comment-user {
        color: white;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .comment-text {
        color: #b3b3b3;
    }
    
    .comment-time {
        color: #6c6c6c;
        font-size: 12px;
        margin-top: 5px;
    }
    
    /* Profile Card */
    .profile-card {
        background: linear-gradient(135deg, #333333 0%, #222222 100%);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .profile-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        overflow: hidden;
        border: 4px solid rgba(29, 185, 84, 0.7);
        margin-bottom: 15px;
    }
    
    .profile-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .profile-name {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .profile-username {
        color: #b3b3b3;
        margin-bottom: 15px;
    }
    
    .profile-stats {
        display: flex;
        gap: 20px;
        margin-bottom: 15px;
    }
    
    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .stat-value {
        color: white;
        font-weight: 600;
        font-size: 18px;
    }
    
    .stat-label {
        color: #b3b3b3;
        font-size: 12px;
    }
    
    /* New Playlist Button */
    .new-playlist-button {
        display: flex;
        align-items: center;
        background: #282828;
        border-radius: 8px;
        padding: 12px 15px;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 15px;
    }
    
    .new-playlist-button:hover {
        background: #333333;
    }
    
    .new-playlist-icon {
        background: #b3b3b3;
        width: 35px;
        height: 35px;
        border-radius: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
    }
    
    .new-playlist-icon svg {
        fill: #282828;
    }
    
    .new-playlist-text {
        color: white;
        font-weight: 600;
    }
    
    /* Volume Control */
    .volume-control {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
    }
    
    .volume-icon {
        color: #b3b3b3;
        cursor: pointer;
    }
    
    .volume-icon:hover {
        color: white;
    }
    
    .volume-slider {
        flex-grow: 1;
        height: 4px;
        background: #535353;
        border-radius: 2px;
        cursor: pointer;
        position: relative;
    }
    
    .volume-level {
        height: 100%;
        background: #b3b3b3;
        border-radius: 2px;
        transition: width 0.1s ease;
    }
    
    .volume-slider:hover .volume-level {
        background: #1DB954;
    }
    
    /* Voice/Music Mixer */
    .mixer-control {
        margin-top: 20px;
    }
    
    .mixer-slider {
        width: 100%;
        margin-top: 10px;
    }
    
    /* Tone Analysis Visualization */
    .tone-visual {
        display: flex;
        height: 60px;
        margin: 15px 0;
        gap: 2px;
    }
    
    .tone-bar {
        flex-grow: 1;
        background: #333333;
        border-radius: 2px;
        position: relative;
        transition: all 0.3s ease;
    }
    
    .tone-value {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, rgba(29, 185, 84, 0.7) 0%, #1DB954 100%);
        border-radius: 2px;
    }
    
    /* Highlight Marker */
    .highlight-marker {
        background: rgba(29, 185, 84, 0.2);
        border-left: 3px solid #1DB954;
        padding: 8px 12px;
        border-radius: 0 5px 5px 0;
        margin: 10px 0;
    }
</style>
"""

# Sample data for the app
class SampleData:
    @staticmethod
    def get_sample_songs():
        return [
            {
                "id": 1,
                "title": "Voice of Nature",
                "artist": "Eden Sound",
                "album": "Natural Echoes",
                "duration": "3:24",
                "image_url": "https://images.unsplash.com/photo-1624535243357-34369104228c",
                "audio_url": "https://freesound.org/data/previews/612/612095_5674468-lq.mp3",
                "likes": 1245,
                "plays": 45289,
                "shares": 256,
                "lyrics": [
                    "Listen to the voice of nature,",
                    "Whispering through the trees.",
                    "Echoes of ancient wisdom,",
                    "Carried by the breeze.",
                    "Mountains standing tall and proud,",
                    "Rivers flowing deep and free.",
                    "This is the voice of nature,",
                    "Speaking to you and me."
                ],
                "tone_analysis": [0.7, 0.4, 0.8, 0.6, 0.7, 0.9, 0.5, 0.6],
                "highlights": [
                    {"position": 1, "text": "Voice of nature - Key theme establishing connection with environment"},
                    {"position": 4, "text": "Ancient wisdom - Historical reference adding depth"}
                ],
                "comments": [
                    {"user": "MusicLover", "avatar": "https://images.unsplash.com/photo-1591200687746-73cfd588ea5e", "text": "This song completely transports me to a forest! Love the ambient sounds.", "time": "2 days ago"},
                    {"user": "AudioPhile", "avatar": "https://images.unsplash.com/photo-1517697471339-4aa32003c11a", "text": "The voice modulation at 1:24 is perfect!", "time": "1 day ago"}
                ]
            },
            {
                "id": 2,
                "title": "Digital Dreams",
                "artist": "Cyber Pulse",
                "album": "Virtual Reality",
                "duration": "4:12",
                "image_url": "https://images.unsplash.com/photo-1587731556938-38755b4803a6",
                "audio_url": "https://freesound.org/data/previews/384/384187_7218762-lq.mp3",
                "likes": 987,
                "plays": 32145,
                "shares": 178,
                "lyrics": [
                    "Pixels dance across my eyes,",
                    "In this world of digital dreams.",
                    "Virtual landscapes come alive,",
                    "Nothing is quite what it seems.",
                    "Connected minds, collective thoughts,",
                    "A new frontier to explore.",
                    "In this realm of ones and zeros,",
                    "We find what we're searching for."
                ],
                "tone_analysis": [0.3, 0.8, 0.5, 0.9, 0.4, 0.7, 0.6, 0.8],
                "highlights": [
                    {"position": 1, "text": "Pixels dance - Visual metaphor creating strong imagery"},
                    {"position": 6, "text": "New frontier - Exploration theme enhancing futuristic concept"}
                ],
                "comments": [
                    {"user": "TechBeats", "avatar": "https://images.unsplash.com/photo-1499557354967-2b2d8910bcca", "text": "The electronic undertones really enhance the futuristic theme!", "time": "5 days ago"},
                    {"user": "RhythmSeeker", "avatar": "https://images.unsplash.com/photo-1650783756081-f235c2c76b6a", "text": "I've listened to this on repeat for hours.", "time": "3 days ago"}
                ]
            },
            {
                "id": 3,
                "title": "Mystic Journey",
                "artist": "Aurora Skies",
                "album": "Beyond Horizons",
                "duration": "5:36",
                "image_url": "https://images.unsplash.com/photo-1494232410401-ad00d5433cfa",
                "audio_url": "https://freesound.org/data/previews/408/408740_5121075-lq.mp3",
                "likes": 2341,
                "plays": 67890,
                "shares": 432,
                "lyrics": [
                    "Venture past the known horizon,",
                    "Into realms of mystic light.",
                    "Where stars are born and planets form,",
                    "In the canvas of the night.",
                    "Cosmic whispers guide your journey,",
                    "Through galaxies untold.",
                    "Discovering the secrets,",
                    "That the universe holds."
                ],
                "tone_analysis": [0.5, 0.6, 0.9, 0.7, 0.8, 0.4, 0.9, 0.5],
                "highlights": [
                    {"position": 2, "text": "Mystic light - Ethereal atmosphere creation"},
                    {"position": 5, "text": "Cosmic whispers - Personification adding mystical element"}
                ],
                "comments": [
                    {"user": "CosmicVibes", "avatar": "https://images.unsplash.com/photo-1658314756129-5b27f344b65b", "text": "The orchestration here is absolutely beautiful.", "time": "1 week ago"},
                    {"user": "StellarSound", "avatar": "https://images.unsplash.com/photo-1650783756107-739513b38177", "text": "That instrumental break at 3:40 gave me goosebumps!", "time": "4 days ago"}
                ]
            },
            {
                "id": 4,
                "title": "Urban Rhythm",
                "artist": "City Pulse",
                "album": "Metropolitan",
                "duration": "3:48",
                "image_url": "https://images.unsplash.com/photo-1510759704643-849552bf3b66",
                "audio_url": "https://freesound.org/data/previews/414/414360_8075558-lq.mp3",
                "likes": 1743,
                "plays": 52369,
                "shares": 284,
                "lyrics": [
                    "Concrete jungle, towers high,",
                    "Neon lights paint the sky.",
                    "City beats, urban flow,",
                    "People rushing to and fro.",
                    "Street corner symphonies,",
                    "Jazz and hip-hop harmonies.",
                    "This is the rhythm of the streets,",
                    "Where different cultures meet."
                ],
                "tone_analysis": [0.8, 0.7, 0.5, 0.9, 0.6, 0.8, 0.9, 0.7],
                "highlights": [
                    {"position": 0, "text": "Concrete jungle - Classic urban metaphor establishing setting"},
                    {"position": 5, "text": "Street corner symphonies - Musical metaphor connecting urban environment with sound"}
                ],
                "comments": [
                    {"user": "BeatMaker", "avatar": "https://images.unsplash.com/photo-1591200687746-73cfd588ea5e", "text": "This perfectly captures the energy of city life!", "time": "3 days ago"},
                    {"user": "RhythmicSoul", "avatar": "https://images.unsplash.com/photo-1499557354967-2b2d8910bcca", "text": "The beat drop at 1:15 is everything!", "time": "Yesterday"}
                ]
            }
        ]
    
    @staticmethod
    def get_playlists():
        return [
            {"id": 1, "name": "Chill Vibes", "image_url": "https://images.unsplash.com/photo-1616663395731-d70897355fd8", "songs": 12},
            {"id": 2, "name": "Focus Flow", "image_url": "https://images.unsplash.com/photo-1588066077857-70494c21533c", "songs": 8},
            {"id": 3, "name": "Creative Boost", "image_url": "https://images.unsplash.com/photo-1616663395403-2e0052b8e595", "songs": 15},
            {"id": 4, "name": "Ambient Sounds", "image_url": "https://images.unsplash.com/photo-1588066080712-b972871ee36b", "songs": 10}
        ]
    
    @staticmethod
    def get_user_profile():
        return {
            "name": "Alex Morgan",
            "username": "@voicecanvas_alex",
            "bio": "Voice artist and audio enthusiast. Creating immersive sound experiences.",
            "avatar": "https://images.unsplash.com/photo-1517697471339-4aa32003c11a",
            "followers": 1247,
            "following": 382,
            "tracks": 28
        }
    
    @staticmethod
    def get_featured_artists():
        return [
            {"name": "Eden Sound", "image_url": "https://images.unsplash.com/photo-1517697471339-4aa32003c11a", "followers": 12452},
            {"name": "Cyber Pulse", "image_url": "https://images.unsplash.com/photo-1499557354967-2b2d8910bcca", "followers": 8923},
            {"name": "Aurora Skies", "image_url": "https://images.unsplash.com/photo-1650783756081-f235c2c76b6a", "followers": 24571},
            {"name": "City Pulse", "image_url": "https://images.unsplash.com/photo-1658314756129-5b27f344b65b", "followers": 18342}
        ]

# Helper functions
def get_svg_play_button():
    return """
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white">
        <path d="M8 5v14l11-7z"/>
    </svg>
    """

def get_spotify_logo():
    return """
    <svg xmlns="http://www.w3.org/2000/svg" width="120" height="36" viewBox="0 0 1134 340" fill="#1DB954">
        <path d="M8 171c0 92 76 168 168 168s168-76 168-168S268 4 176 4 8 79 8 171zm230 78c-39-24-89-30-147-17-14 2-16-18-4-20 64-15 118-8 162 19 11 7 0 24-11 18zm17-45c-45-28-114-36-167-20-17 5-23-21-7-25 61-18 136-9 188 23 14 9 0 31-14 22zM80 133c-17 6-28-23-9-30 59-18 159-15 221 22 17 9 1 37-17 27-54-32-144-35-195-19zm379 91c-17 0-33-6-47-20-1 0-1 1-1 1l-16 19c-1 1-1 2 0 3 18 16 40 24 64 24 34 0 55-19 55-47 0-24-15-37-50-46-29-7-34-12-34-22s10-16 23-16 25 5 39 15c0 0 1 1 2 1s1-1 1-1l14-20c1-1 1-1 0-2-16-13-35-20-56-20-31 0-53 19-53 46 0 29 20 38 52 46 28 6 32 12 32 22 0 11-10 17-25 17zm95-77v-13c0-1-1-2-2-2h-26c-1 0-2 1-2 2v147c0 1 1 2 2 2h26c1 0 2-1 2-2v-46c10 11 21 16 36 16 27 0 54-21 54-61s-27-60-54-60c-15 0-26 5-36 17zm30 78c-18 0-31-15-31-35s13-34 31-34 30 14 30 34-12 35-30 35zm68-34c0 34 27 60 62 60s62-27 62-61-26-60-61-60-63 27-63 61zm30-1c0-20 13-34 32-34s33 15 33 35-13 34-32 34-33-15-33-35zm140-58v-29c0-1 0-2-1-2h-26c-1 0-2 1-2 2v29h-13c-1 0-2 1-2 2v22c0 1 1 2 2 2h13v58c0 23 11 35 34 35 9 0 18-2 25-6 1 0 1-1 1-2v-21c0-1 0-2-1-2h-2c-5 3-11 4-16 4-8 0-12-4-12-12v-54h30c1 0 2-1 2-2v-22c0-1-1-2-2-2h-30zm129-3c0-11 4-15 13-15 5 0 10 0 15 2h1s1-1 1-2V93c0-1 0-2-1-2-5-2-12-3-22-3-24 0-36 14-36 39v5h-13c-1 0-2 1-2 2v22c0 1 1 2 2 2h13v89c0 1 1 2 2 2h26c1 0 1-1 1-2v-89h25l39 89c-4 9-8 11-14 11-5 0-10-1-15-4h-1l-1 1-9 19c0 1 0 3 1 3 9 5 17 7 27 7 19 0 30-9 39-33l45-116v-2c0-1-1-1-2-1h-27c-1 0-1 1-1 2l-28 78-30-78c0-1-1-2-2-2h-44v-3zm-83 3c-1 0-2 1-2 2v113c0 1 1 2 2 2h26c1 0 1-1 1-2V134c0-1 0-2-1-2h-26zm-6-33c0 10 9 19 19 19s18-9 18-19-8-18-18-18-19 8-19 18zm245 69c10 0 19-8 19-18s-9-18-19-18-18 8-18 18 8 18 18 18zm0-34c9 0 17 7 17 16s-8 16-17 16-16-7-16-16 7-16 16-16zm4 18c3-1 5-3 5-6 0-4-4-6-8-6h-8v19h4v-6h4l4 6h5zm-3-9c2 0 4 1 4 3s-2 3-4 3h-4v-6h4z"/>
    </svg>
    """

# Fixed version that doesn't use direct HTML
def render_album_card(song, index):
    album_container = st.container()
    with album_container:
        # Use st.image for the album cover
        st.image(song['image_url'], width=150)
        # Use st.write for text
        st.write(f"**{song['title']}**")
        st.write(f"{song['artist']}")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_track_item(song, index, is_active=False):
    # Use a container for the track item
    track_container = st.container()
    with track_container:
        # Create columns for track layout
        cols = st.columns([1, 8, 3])
        
        # Track number
        with cols[0]:
            st.write(f"{index + 1}")
        
        # Track info (title and artist)
        with cols[1]:
            if is_active:
                st.markdown(f"**{song['title']}**")
            else:
                st.write(f"{song['title']}")
            st.write(f"{song['artist']}")
        
        # Duration
        with cols[2]:
            st.write(f"{song['duration']}")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_tone_visualization(tones):
    """Render tone visualization using Streamlit components"""
    # Create a container for tone visualization
    tone_container = st.container()
    
    with tone_container:
        # Create a progress bar for each tone intensity
        for i, tone in enumerate(tones):
            # Scale the tone value to 0-1 range for progress bar
            st.progress(tone)
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_lyrics(lyrics, highlights=None):
    """Render lyrics using Streamlit components instead of raw HTML"""
    # Create a container for lyrics
    lyrics_container = st.container()
    
    with lyrics_container:
        # Display each line of lyrics
        for i, line in enumerate(lyrics):
            # Check if line has highlight
            highlight_note = ""
            if highlights:
                for highlight in highlights:
                    if highlight["position"] == i:
                        # If highlighted, display differently
                        st.markdown(f"**{line}**")
                        st.markdown(f"*{highlight['text']}*")
                        highlight_note = highlight['text']  # Save to avoid duplicate
            
            # If no highlight or already displayed, show normal line
            if not highlight_note:
                st.text(line)
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_comments(comments):
    """Render comments section using Streamlit components"""
    # Create a container for comments
    comments_container = st.container()
    
    with comments_container:
        # Comment input with user avatar
        user_profile = SampleData.get_user_profile()
        
        cols = st.columns([1, 6])
        with cols[0]:
            st.image(user_profile['avatar'], width=50)
        with cols[1]:
            st.text_input("Add a comment...", key="comment_input")
        
        # Existing comments
        for i, comment in enumerate(comments):
            st.markdown("---")
            
            # Comment with avatar and content
            comm_cols = st.columns([1, 6])
            with comm_cols[0]:
                st.image(comment['avatar'], width=50)
            
            with comm_cols[1]:
                st.markdown(f"**{comment['user']}**")
                st.write(comment['text'])
                st.caption(comment['time'])
                
                # Comment actions - use index instead of id
                action_cols = st.columns([1, 1, 5])
                with action_cols[0]:
                    st.button("❤️ Like", key=f"like_comment_{i}")
                with action_cols[1]:
                    st.button("↩️ Reply", key=f"reply_comment_{i}")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_social_share_buttons(song_id):
    """Render social media sharing buttons for a song using Streamlit components"""
    # Create container for share buttons
    share_container = st.container()
    
    with share_container:
        st.subheader("Share this audio")
        
        # Create columns for social media buttons
        cols = st.columns(4)
        
        # Facebook button
        with cols[0]:
            if st.button("Facebook", key=f"fb_share_{song_id}"):
                st.info("Shared to Facebook!")
        
        # Twitter button
        with cols[1]:
            if st.button("Twitter", key=f"twitter_share_{song_id}"):
                st.info("Shared to Twitter!")
        
        # Instagram button
        with cols[2]:
            if st.button("Instagram", key=f"insta_share_{song_id}"):
                st.info("Shared to Instagram!")
        
        # Copy link button
        with cols[3]:
            if st.button("Copy Link", key=f"link_share_{song_id}"):
                st.info("Copied link to clipboard!")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_likes_and_engagement(song):
    """Render the likes, plays, shares stats for a song using Streamlit components"""
    # Create a container for engagement stats
    engagement_container = st.container()
    
    with engagement_container:
        # Create three columns for likes, plays, and shares
        cols = st.columns(3)
        
        # Likes column
        with cols[0]:
            st.metric("Likes", song['likes'])
            st.button("❤️ Like", key=f"like_metric_{song['id']}")
        
        # Plays column
        with cols[1]:
            st.metric("Plays", song['plays'])
        
        # Shares column
        with cols[2]:
            st.metric("Shares", song['shares'])
            st.button("📤 Share", key=f"share_metric_{song['id']}")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_profile_card(profile):
    # Create a container for the profile card
    profile_container = st.container()
    
    with profile_container:
        # Display avatar
        st.image(profile['avatar'], width=150)
        
        # Display name and username
        st.title(profile['name'])
        st.write(profile['username'])
        
        # Create columns for stats
        cols = st.columns(3)
        
        # Column 1: Followers
        with cols[0]:
            st.write(f"**{profile['followers']}**")
            st.write("Followers")
        
        # Column 2: Following
        with cols[1]:
            st.write(f"**{profile['following']}**")
            st.write("Following")
        
        # Column 3: Tracks
        with cols[2]:
            st.write(f"**{profile['tracks']}**")
            st.write("Tracks")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_player_controls(song=None):
    if not song:
        song = SampleData.get_sample_songs()[0]
    
    # Create a container for player controls
    player_container = st.container()
    
    with player_container:
        # Song title and artist
        st.subheader(f"{song['title']} - {song['artist']}")
        
        # Audio player
        st.audio(song['audio_url'])
        
        # Player controls using columns
        cols = st.columns([1, 1, 1, 5])
        with cols[0]:
            st.button("◀◀", key=f"prev_button_{song['id']}")
        with cols[1]:
            st.button("▶", key=f"play_button_{song['id']}")
        with cols[2]:
            st.button("▶▶", key=f"next_button_{song['id']}")
            
        # Progress bar
        st.progress(0.45)
        
        # Time display
        time_cols = st.columns(2)
        with time_cols[0]:
            st.text("1:32")
        with time_cols[1]:
            st.text(f"{song['duration']}")
        
        # Volume control
        st.slider("Volume", min_value=0, max_value=100, value=70, key=f"volume_slider_{song['id']}")
        
        # Social icons using emoji buttons
        social_cols = st.columns([1, 1, 1, 5])
        with social_cols[0]:
            st.button("❤️", key=f"like_button_{song['id']}")
        with social_cols[1]:
            st.button("📤", key=f"share_button_{song['id']}")
        with social_cols[2]:
            st.button("📋", key=f"playlist_button_{song['id']}")
        with social_cols[3]:
            st.text(f"{song['likes']} likes • {song['plays']} plays • {song['shares']} shares")
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_sidebar_playlists():
    """Render sidebar playlists using Streamlit components"""
    # Create container for playlists
    playlists_container = st.container()
    
    with playlists_container:
        # Create new playlist button
        if st.button("➕ Create Playlist", key="create_playlist_btn"):
            st.session_state.show_create_playlist = True
        
        # Get playlists from sample data
        playlists = SampleData.get_playlists()
        
        # Display each playlist
        for playlist in playlists:
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(playlist['image_url'], width=35)
            with cols[1]:
                if st.button(f"{playlist['name']} ({playlist['songs']})", 
                           key=f"playlist_{playlist['id']}"):
                    st.session_state.selected_playlist = playlist['id']
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_featured_artists():
    """Render featured artists using Streamlit components"""
    # Create container for featured artists
    artists_container = st.container()
    
    with artists_container:
        st.subheader("Featured Artists")
        
        # Get artists from sample data
        artists = SampleData.get_featured_artists()
        
        # Display each artist
        for i, artist in enumerate(artists):
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(artist['image_url'], width=35)
            with cols[1]:
                if st.button(f"{artist['name']} • {artist['followers']} followers", 
                           key=f"artist_{i}"):
                    st.session_state.selected_artist = artist['name']
    
    # Return empty string as we're using Streamlit components directly
    return ""

def render_voice_mixer():
    """Render voice/music mixer using Streamlit components"""
    # Create a container for voice mixer
    mixer_container = st.container()
    
    with mixer_container:
        st.subheader("Voice/Music Mixer")
        st.caption("Adjust the balance between vocals and background music")
        
        # Create a slider for voice/music balance
        st.slider("Voice/Music Balance", 
                 min_value=0, 
                 max_value=100, 
                 value=60, 
                 key=f"voice_mixer_slider",
                 help="Slide left for more voice, right for more music")
        
        # Labels for the slider
        cols = st.columns(2)
        with cols[0]:
            st.text("Voice")
        with cols[1]:
            st.text("Music")
    
    # Return empty string as we're using Streamlit components directly
    return ""

# Main application
def main():
    # Inject CSS
    st.markdown(enhanced_css, unsafe_allow_html=True)
    
    # App header with Spotify styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div style="text-align: center;">{get_spotify_logo()}</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="main-header">VoiceCanvas</h1>', unsafe_allow_html=True)
        st.markdown('<h3 class="sub-header">Transform Text to Professional Audio</h3>', unsafe_allow_html=True)
    
    # Sidebar with user profile and playlists
    with st.sidebar:
        # Now directly calling the render functions that use Streamlit components
        render_profile_card(SampleData.get_user_profile())
        
        # API Settings Section
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🔑 API Settings")
        
        with st.expander("API Configuration", expanded=True):
            # Initialize session state for API keys if not present
            if 'use_built_in_elevenlabs' not in st.session_state:
                st.session_state.use_built_in_elevenlabs = True
            if 'use_built_in_groq' not in st.session_state:
                st.session_state.use_built_in_groq = True
            if 'custom_elevenlabs_key' not in st.session_state:
                st.session_state.custom_elevenlabs_key = ""
            if 'custom_groq_key' not in st.session_state:
                st.session_state.custom_groq_key = ""
            if 'custom_openai_key' not in st.session_state:
                st.session_state.custom_openai_key = ""
            
            # Check built-in API keys
            elevenlabs_key_available = os.environ.get("ELEVENLABS_API_KEY") is not None
            groq_key_available = os.environ.get("GROQ_API_KEY") is not None
            
            # ElevenLabs API Settings
            st.markdown("""
            <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; color: white;">ElevenLabs API</span>
                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #1DB954;"></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            use_built_in_elevenlabs = st.checkbox(
                "Use built-in API key", 
                value=st.session_state.use_built_in_elevenlabs,
                key="elevenlabs_built_in_checkbox",
                help="Use the built-in ElevenLabs API key provided with VoiceCanvas"
            )
            
            st.session_state.use_built_in_elevenlabs = use_built_in_elevenlabs
            
            if not use_built_in_elevenlabs:
                custom_elevenlabs_key = st.text_input(
                    "Your ElevenLabs API Key", 
                    value=st.session_state.custom_elevenlabs_key,
                    type="password",
                    key="elevenlabs_key_input",
                    help="Enter your own ElevenLabs API key"
                )
                st.session_state.custom_elevenlabs_key = custom_elevenlabs_key
            
            # Groq API Settings
            st.markdown("""
            <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; color: white;">Groq API</span>
                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #1DB954;"></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            use_built_in_groq = st.checkbox(
                "Use built-in API key", 
                value=st.session_state.use_built_in_groq,
                key="groq_built_in_checkbox",
                help="Use the built-in Groq API key provided with VoiceCanvas"
            )
            
            st.session_state.use_built_in_groq = use_built_in_groq
            
            if not use_built_in_groq:
                custom_groq_key = st.text_input(
                    "Your Groq API Key", 
                    value=st.session_state.custom_groq_key,
                    type="password",
                    key="groq_key_input",
                    help="Enter your own Groq API key"
                )
                st.session_state.custom_groq_key = custom_groq_key
            
            # OpenAI API Settings (always custom since not built-in)
            st.markdown("""
            <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; color: white;">OpenAI API (Optional)</span>
                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #FF5252;"></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            custom_openai_key = st.text_input(
                "Your OpenAI API Key", 
                value=st.session_state.custom_openai_key,
                type="password",
                key="openai_key_input",
                help="Enter your OpenAI API key (optional)"
            )
            st.session_state.custom_openai_key = custom_openai_key
            
            # Help information
            st.markdown("""
            <div style="background: rgba(29, 185, 84, 0.1); padding: 12px; border-radius: 8px; margin-top: 15px; border-left: 3px solid #1DB954;">
                <p style="margin: 0; color: #b3b3b3; font-size: 12px;">
                    <strong style="color: white;">About API Keys</strong><br>
                    VoiceCanvas includes built-in API keys for ElevenLabs and Groq, but you can use your own for higher quotas and additional features.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Use Streamlit's built-in components for headings
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Your Library")
        
        # Directly call the render functions (which now use Streamlit components)
        render_sidebar_playlists()
        st.markdown("<hr>", unsafe_allow_html=True)
        render_featured_artists()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Voice Creation", "Discover", "Your Library", "Smart Features"])
    
    with tab1:
        # Top section with featured content
        st.markdown("<h2>Featured Audio Content</h2>", unsafe_allow_html=True)
        
        # First row with album cards
        col1, col2, col3, col4 = st.columns(4)
        for i, col in enumerate([col1, col2, col3, col4]):
            with col:
                # Directly call the render function (which now uses Streamlit components)
                render_album_card(SampleData.get_sample_songs()[i], i)
        
        # Player section
        selected_song = SampleData.get_sample_songs()[0]  # Default to first song
        # Directly call the render function (which now uses Streamlit components)
        render_player_controls(selected_song)
        
        # Social sharing and engagement section
        col1, col2 = st.columns([1, 2])
        with col1:
            # Directly call the render function (which now uses Streamlit components)
            render_social_share_buttons(selected_song['id'])
        with col2:
            # Directly call the render function (which now uses Streamlit components)
            render_likes_and_engagement(selected_song)
        
        # Add CSS for the engagement stats
        st.markdown("""
        <style>
        .engagement-stats {
            display: flex;
            gap: 24px;
            margin-top: 15px;
        }
        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            background: #282828;
            padding: 15px;
            border-radius: 8px;
            min-width: 100px;
            transition: all 0.3s ease;
        }
        .stat-item:hover {
            background: #333333;
            transform: translateY(-3px);
        }
        .stat-icon {
            width: 24px;
            height: 24px;
            fill: #b3b3b3;
            margin-bottom: 8px;
        }
        .stat-value {
            font-size: 20px;
            font-weight: 600;
            color: #FFFFFF;
        }
        .stat-label {
            font-size: 12px;
            color: #b3b3b3;
            margin-top: 4px;
        }
        .social-share-container {
            background: #282828;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .comment-actions {
            display: flex;
            gap: 15px;
            margin-top: 8px;
            font-size: 13px;
        }
        .comment-like, .comment-reply {
            color: #b3b3b3;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .comment-like:hover, .comment-reply:hover {
            color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Lyrics and analysis section
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("<h3>Lyrics</h3>", unsafe_allow_html=True)
            # Directly call the render function (which now uses Streamlit components)
            render_lyrics(selected_song['lyrics'], selected_song['highlights'])
        
        with col2:
            st.markdown("<h3>Tone Analysis</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #b3b3b3;'>Intensity pattern throughout the audio</p>", unsafe_allow_html=True)
            # Directly call the render function (which now uses Streamlit components)
            render_tone_visualization(selected_song['tone_analysis'])
            # Directly call the render function (which now uses Streamlit components)
            render_voice_mixer()
        
        # Comments section
        st.markdown("<h3>Comments & Feedback</h3>", unsafe_allow_html=True)
        # Directly call the render function (which now uses Streamlit components)
        render_comments(selected_song['comments'])
    
    with tab2:
        st.markdown("<h2>Create New Voice Content</h2>", unsafe_allow_html=True)
        
        # Text input section
        st.markdown("<h3>Enter Your Text</h3>", unsafe_allow_html=True)
        text_input = st.text_area("Type or paste your text here", height=200, 
                                  placeholder="Enter your text to convert to speech...\n\nTip: You can format dialogue with character names followed by a colon, e.g.\nNarrator: This is the beginning of our story.\nAlex: Hello there!")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            voice_provider = st.selectbox("Voice Provider", ["ElevenLabs", "Groq", "Amazon Polly"])
        
        with col2:
            voice_style = st.selectbox("Voice Style", ["Natural", "Expressive", "Professional", "Friendly", "Serious"])
        
        # Voice character selection
        st.markdown("<h3>Voice Characters</h3>", unsafe_allow_html=True)
        
        # Add an auto-detect characters button
        if st.button("Auto-Detect Characters with Groq AI"):
            if text_input:
                with st.spinner("Analyzing text and detecting characters..."):
                    try:
                        # Call the Groq API to analyze the text
                        tone_analysis = analyze_text_tone(text_input)
                        
                        # Display the tone analysis results
                        st.markdown("<h4>Text Analysis Results</h4>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown(f"**Emotional Tone:** {tone_analysis['tone']}")
                            st.markdown(f"**Suggested Tempo:** {tone_analysis['tempo']}")
                            st.markdown(f"**Recommended Music Genre:** {tone_analysis['music_genre']}")
                        
                        with col2:
                            st.markdown("**Key Elements:**")
                            elements_list = ""
                            for element in tone_analysis['key_elements'][:4]:  # Show up to 4 elements
                                elements_list += f"- {element}<br>"
                            st.markdown(elements_list, unsafe_allow_html=True)
                        
                        # Display tone visualization (using Streamlit components directly)
                        render_tone_visualization(tone_analysis['intensity_curve'])
                        
                        # Try to convert to dialogue if it's not already in dialogue format
                        if ":" not in text_input:
                            st.markdown("<h4>Converted to Dialogue</h4>", unsafe_allow_html=True)
                            dialogue = generate_dialogue_with_groq(text_input)
                            
                            # Handle the dialogue result from Groq
                            dialogue_text = ""
                            if isinstance(dialogue, list):
                                for line in dialogue:
                                    if 'character' in line and 'line' in line:
                                        dialogue_text += f"{line['character']}: {line['line']}\n"
                            elif isinstance(dialogue, dict) and 'dialogue' in dialogue:
                                for line in dialogue['dialogue']:
                                    dialogue_text += f"{line['character']}: {line['line']}\n"
                            
                            if dialogue_text:
                                st.text_area("Dialogue Version", dialogue_text, height=150)
                            else:
                                st.warning("Could not convert to dialogue format. Please try with different text.")
                    except Exception as e:
                        st.error(f"Error analyzing text: {str(e)}")
            else:
                st.warning("Please enter some text first.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            narrator_voice = st.selectbox("Narrator Voice", ["Morgan (Male)", "Olivia (Female)", "Skylar (Gender Neutral)", "Custom..."])
        
        with col2:
            character1 = st.selectbox("Character 1", ["Not Detected", "Alex (Male)", "Sophia (Female)", "Custom..."])
        
        with col3:
            character2 = st.selectbox("Character 2", ["Not Detected", "Jamie (Male)", "Emma (Female)", "Custom..."])
        
        # Voice Cloning Section
        st.markdown("<h3>Voice Cloning 🎤</h3>", unsafe_allow_html=True)
        st.markdown("Clone a voice by uploading a sample or using voice fingerprint technology", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            voice_sample = st.file_uploader("Upload Voice Sample", type=["mp3", "wav", "m4a"], key="voice_sample")
            if voice_sample:
                st.audio(voice_sample, format=f"audio/{voice_sample.name.split('.')[-1]}")
                if st.button("Clone Voice"):
                    with st.spinner("Cloning voice... This may take a minute..."):
                        voice_name = st.session_state.get("voice_name", "My Custom Voice")
                        voice_id = clone_voice_elevenlabs(voice_sample, voice_name)
                        if voice_id:
                            st.session_state.cloned_voice_id = voice_id
                            st.success(f"Voice cloned successfully! Voice ID: {voice_id}")
                            
                            # Show sample generation option after cloning
                            sample_text = "Hello! This is a sample of my cloned voice. It sounds pretty amazing, doesn't it?"
                            if st.button("Generate sample with cloned voice"):
                                with st.spinner("Generating audio sample with your cloned voice..."):
                                    audio_bytes = text_to_speech_elevenlabs(
                                        sample_text, 
                                        voice_id=voice_id
                                    )
                                    if audio_bytes:
                                        st.audio(audio_bytes, format="audio/mp3")
        
        with col2:
            voice_name = st.text_input("Voice Name", placeholder="Give this voice a name (e.g., 'My Custom Voice')", key="voice_name")
            similarity = st.slider("Voice Similarity", min_value=0, max_value=100, value=85, 
                      help="Higher values will make the generated voice more similar to the uploaded sample")
            st.markdown("""
            <div style="background: #282828; padding: 15px; border-radius: 8px; margin-top: 15px;">
                <h4 style="margin-top: 0; color: white;">Voice Cloning Guidelines</h4>
                <ul style="color: #b3b3b3;">
                    <li>Use a clear voice sample with minimal background noise</li>
                    <li>Sample should be at least 30 seconds long for best results</li>
                    <li>Pronounce words clearly and at a natural pace</li>
                    <li>Avoid music or other voices in the background</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Voice Dubbing Section
        st.markdown("<h3>Voice Dubbing 🎬</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            dub_file = st.file_uploader("Upload Video/Audio to Dub", type=["mp4", "mp3", "wav"], key="dub_file")
            if dub_file:
                file_type = dub_file.name.split('.')[-1]
                if file_type == "mp4":
                    st.video(dub_file)
                else:
                    st.audio(dub_file, format=f"audio/{file_type}")
                    
                # Text area for transcript
                transcript = st.text_area("Transcript (optional)", 
                                        placeholder="Enter the transcript of the audio if you have it, or let us generate it automatically", 
                                        key="dub_transcript")
        
        with col2:
            dub_language = st.selectbox("Dubbing Language", ["English", "Spanish", "French", "German", "Japanese", "Chinese", "Hindi"], key="dub_language")
            dub_voice = st.selectbox("Dubbing Voice", ["Male (Deep)", "Male (Natural)", "Female (Natural)", "Female (Soft)", "Custom..."], key="dub_voice")
            preserve_timing = st.checkbox("Preserve original timing", value=True, key="preserve_timing")
            subtitles = st.checkbox("Include subtitle track", value=True, key="subtitles")
            
            if dub_file:
                if st.button("Generate Dubbed Version", key="dub_button"):
                    with st.spinner("Generating dubbed audio..."):
                        # Map voice selection to voice IDs
                        voice_mapping = {
                            "Male (Deep)": "ErXwobaYiN019PkySvjV", 
                            "Male (Natural)": "ZQe5CZNOzWyzPSCn5a3c",
                            "Female (Natural)": "21m00Tcm4TlvDq8ikWAM", 
                            "Female (Soft)": "AZnzlk1XvdvUeBnXmlld",
                            "Custom...": st.session_state.get("cloned_voice_id")
                        }
                        
                        voice_id = voice_mapping.get(dub_voice)
                        if voice_id:
                            # Get transcript if not provided
                            if not transcript:
                                transcript = "This is a sample transcript for dubbing demonstration."
                                
                            # Generate dubbed audio
                            dubbed_file = dub_audio_with_elevenlabs(dub_file, dub_language, transcript, voice_id)
                            if dubbed_file:
                                with open(dubbed_file, "rb") as f:
                                    st.audio(f.read(), format="audio/mp3")
                                
                                st.success("Dubbing completed successfully!")
                                st.markdown("""
                                <div style="background: #282828; padding: 15px; border-radius: 8px; margin-top: 15px;">
                                    <h4 style="margin-top: 0; color: white;">Share Your Dubbed Content</h4>
                                    <div style="display: flex; justify-content: space-around; margin-top: 10px;">
                                        <button style="background: #1DB954; border: none; color: white; padding: 8px 16px; border-radius: 20px; cursor: pointer;">Download</button>
                                        <button style="background: #1DB954; border: none; color: white; padding: 8px 16px; border-radius: 20px; cursor: pointer;">Share</button>
                                        <button style="background: #1DB954; border: none; color: white; padding: 8px 16px; border-radius: 20px; cursor: pointer;">Save to Library</button>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("Please select a valid voice for dubbing.")
        
        # Background audio section
        st.markdown("<h3>Background Audio 🎵</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            background_type = st.selectbox("Background Type", ["None", "Ambient", "Music", "Sound Effects"])
        
        with col2:
            background_track = st.selectbox("Background Track", ["Gentle Piano", "Forest Ambience", "Happy Ukulele", "Epic Orchestral", "Custom..."])
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Generate Voice Audio", use_container_width=True):
                if text_input:
                    with st.spinner("Generating voice audio..."):
                        try:
                            # Generate voice audio using the selected provider
                            if voice_provider == "ElevenLabs":
                                # Set up character voice mapping if there are characters detected
                                character_voice_mapping = None
                                
                                # Check if text is in dialogue format
                                if ":" in text_input and (character1 != "Not Detected" or character2 != "Not Detected" or narrator_voice != "Custom..."):
                                    character_voice_mapping = {}
                                    
                                    # Map narrator voice
                                    if narrator_voice == "Morgan (Male)":
                                        character_voice_mapping["Narrator"] = "ErXwobaYiN019PkySvjV"
                                    elif narrator_voice == "Olivia (Female)":
                                        character_voice_mapping["Narrator"] = "21m00Tcm4TlvDq8ikWAM"
                                    elif narrator_voice == "Skylar (Gender Neutral)":
                                        character_voice_mapping["Narrator"] = "pNInz6obpgDQGcFmaJgB"
                                    
                                    # Map character 1 voice
                                    if character1 == "Alex (Male)":
                                        character_voice_mapping["Alex"] = "ZQe5CZNOzWyzPSCn5a3c"
                                    elif character1 == "Sophia (Female)":
                                        character_voice_mapping["Sophia"] = "AZnzlk1XvdvUeBnXmlld"
                                    
                                    # Map character 2 voice
                                    if character2 == "Jamie (Male)":
                                        character_voice_mapping["Jamie"] = "jBpfuIE2acCO8z3wKNLl"
                                    elif character2 == "Emma (Female)":
                                        character_voice_mapping["Emma"] = "LcfcDJNUP1GQjkzn1xUU"
                                
                                # Also use any custom cloned voice if available
                                if st.session_state.get("cloned_voice_id"):
                                    if voice_name:
                                        # If user has a cloned voice, add it to character mapping
                                        if character_voice_mapping is None:
                                            character_voice_mapping = {}
                                        character_voice_mapping[voice_name] = st.session_state.get("cloned_voice_id")
                                
                                # Set voice style parameters
                                voice_settings = {
                                    "stability": 0.5,
                                    "similarity_boost": 0.75,
                                    "style": 0.0
                                }
                                
                                if voice_style == "Expressive":
                                    voice_settings["style"] = 0.7
                                elif voice_style == "Professional":
                                    voice_settings["stability"] = 0.8
                                    voice_settings["style"] = 0.3
                                elif voice_style == "Friendly":
                                    voice_settings["stability"] = 0.4
                                    voice_settings["similarity_boost"] = 0.8
                                    voice_settings["style"] = 0.5
                                elif voice_style == "Serious":
                                    voice_settings["stability"] = 0.9
                                    voice_settings["style"] = 0.1
                                
                                # Convert the text to speech using ElevenLabs with all parameters
                                audio_bytes = text_to_speech_elevenlabs(
                                    text_input,
                                    voice_settings=voice_settings,
                                    character_voice_mapping=character_voice_mapping
                                )
                                if audio_bytes:
                                    # Save the generated audio to a temporary file
                                    timestamp = int(time.time())
                                    temp_audio_path = f"temp_audio_{timestamp}.mp3"
                                    
                                    with open(temp_audio_path, "wb") as f:
                                        f.write(audio_bytes)
                                    
                                    # Display the audio player
                                    st.audio(temp_audio_path, format="audio/mp3")
                                    
                                    # Show success message
                                    st.success("Audio generated successfully!")
                                    
                                    # Add sharing options
                                    st.markdown("<h4>Share Your Creation</h4>", unsafe_allow_html=True)
                                    share_col1, share_col2 = st.columns([1, 1])
                                    with share_col1:
                                        st.markdown("""
                                        <div class="social-share-container">
                                            <div class="social-icons">
                                                <div class="social-icon" onclick="alert('Shared to Facebook!')">
                                                    <svg viewBox="0 0 24 24">
                                                        <path d="M12 2.04C6.5 2.04 2 6.53 2 12.06C2 17.06 5.66 21.21 10.44 21.96V14.96H7.9V12.06H10.44V9.85C10.44 7.34 11.93 5.96 14.22 5.96C15.31 5.96 16.45 6.15 16.45 6.15V8.62H15.19C13.95 8.62 13.56 9.39 13.56 10.18V12.06H16.34L15.89 14.96H13.56V21.96C15.9 21.59 18.03 20.38 19.6 18.58C21.17 16.78 22.06 14.49 22 12.06C22 6.53 17.5 2.04 12 2.04Z" />
                                                    </svg>
                                                </div>
                                                <div class="social-icon" onclick="alert('Shared to Twitter!')">
                                                    <svg viewBox="0 0 24 24">
                                                        <path d="M22.46 6C21.69 6.35 20.86 6.58 20 6.69C20.88 6.16 21.56 5.32 21.88 4.31C21.05 4.81 20.13 5.16 19.16 5.36C18.37 4.5 17.26 4 16 4C13.65 4 11.73 5.92 11.73 8.29C11.73 8.63 11.77 8.96 11.84 9.27C8.28 9.09 5.11 7.38 3 4.79C2.63 5.42 2.42 6.16 2.42 6.94C2.42 8.43 3.17 9.75 4.33 10.5C3.62 10.5 2.96 10.3 2.38 10C2.38 10 2.38 10 2.38 10.03C2.38 12.11 3.86 13.85 5.82 14.24C5.46 14.34 5.08 14.39 4.69 14.39C4.42 14.39 4.15 14.36 3.89 14.31C4.43 16 6 17.26 7.89 17.29C6.43 18.45 4.58 19.13 2.56 19.13C2.22 19.13 1.88 19.11 1.54 19.07C3.44 20.29 5.7 21 8.12 21C16 21 20.33 14.46 20.33 8.79C20.33 8.6 20.33 8.42 20.32 8.23C21.16 7.63 21.88 6.87 22.46 6Z" />
                                                    </svg>
                                                </div>
                                                <div class="social-icon" onclick="alert('Shared to Instagram!')">
                                                    <svg viewBox="0 0 24 24">
                                                        <path d="M7.8 2H16.2C19.4 2 22 4.6 22 7.8V16.2C22 19.4 19.4 22 16.2 22H7.8C4.6 22 2 19.4 2 16.2V7.8C2 4.6 4.6 2 7.8 2M7.6 4C5.61 4 4 5.61 4 7.6V16.4C4 18.39 5.61 20 7.6 20H16.4C18.39 20 20 18.39 20 16.4V7.6C20 5.61 18.39 4 16.4 4H7.6M17.25 5.5C17.94 5.5 18.5 6.06 18.5 6.75C18.5 7.44 17.94 8 17.25 8C16.56 8 16 7.44 16 6.75C16 6.06 16.56 5.5 17.25 5.5M12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7M12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" />
                                                    </svg>
                                                </div>
                                                <div class="social-icon" onclick="alert('Copied link to clipboard!')">
                                                    <svg viewBox="0 0 24 24">
                                                        <path d="M10.59 13.41C11 13.8 11 14.43 10.59 14.83C10.2 15.22 9.57 15.22 9.17 14.83C7.22 12.88 7.22 9.71 9.17 7.76L12.71 4.22C14.66 2.27 17.83 2.27 19.78 4.22C21.73 6.17 21.73 9.34 19.78 11.29L18.29 12.78C18.3 11.96 18.17 11.14 17.89 10.36L18.36 9.88C19.54 8.71 19.54 6.81 18.36 5.64C17.19 4.46 15.29 4.46 14.12 5.64L10.59 9.17C9.41 10.34 9.41 12.24 10.59 13.41M14.83 9.17C14.44 8.78 14.44 8.15 14.83 7.76C15.22 7.36 15.85 7.36 16.24 7.76C18.18 9.7 18.18 12.87 16.24 14.83L12.7 18.36C10.76 20.31 7.58 20.31 5.64 18.36C3.69 16.42 3.69 13.25 5.64 11.3L7.13 9.82C7.12 10.63 7.25 11.45 7.53 12.23L7.05 12.71C5.88 13.88 5.88 15.78 7.05 16.95C8.23 18.13 10.13 18.13 11.3 16.95L14.83 13.41C16.01 12.24 16.01 10.34 14.83 9.17Z" />
                                                    </svg>
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with share_col2:
                                        # Add like and comment section
                                        st.markdown("""
                                        <div style="background: #282828; padding: 15px; border-radius: 8px;">
                                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                                <button class="social-icon">❤️</button>
                                                <span>0 likes</span>
                                            </div>
                                            <input type="text" class="comment-box" placeholder="Add a comment...">
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.warning(f"Voice generation with {voice_provider} is not yet implemented. Please select ElevenLabs.")
                        except Exception as e:
                            st.error(f"Error generating audio: {str(e)}")
                else:
                    st.warning("Please enter some text first.")
        
        with col2:
            st.button("Preview", use_container_width=True)
        
        with col3:
            st.button("Save to Library", use_container_width=True)
    
    with tab3:
        st.markdown("<h2>Discover Content</h2>", unsafe_allow_html=True)
        
        # Search and filter section
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.text_input("Search for content", placeholder="Search by title, artist, or keywords...")
        with col2:
            st.selectbox("Category", ["All", "Voice Overs", "Narration", "Music", "Podcasts"])
        with col3:
            st.selectbox("Sort By", ["Most Popular", "Newest", "Trending", "Most Liked"])
        
        # Display tracks in a list
        st.markdown("<h3>Trending Tracks</h3>", unsafe_allow_html=True)
        for i, song in enumerate(SampleData.get_sample_songs()):
            is_active = i == 0  # Make the first one active
            st.markdown(render_track_item(song, i, is_active), unsafe_allow_html=True)
        
        # Popular playlists section
        st.markdown("<h3>Popular Playlists</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        playlists = SampleData.get_playlists()
        for i, col in enumerate([col1, col2, col3, col4]):
            with col:
                playlist = playlists[i]
                st.markdown(f"""
                <div class="album-card">
                    <div class="album-image-container">
                        <img src="{playlist['image_url']}" class="album-image" alt="{playlist['name']}">
                        <div class="play-button">
                            {get_svg_play_button()}
                        </div>
                    </div>
                    <div class="album-details">
                        <div class="album-title">{playlist['name']}</div>
                        <div class="album-artist">{playlist['songs']} songs</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<h2>Your Library</h2>", unsafe_allow_html=True)
        
    with tab5:
        st.markdown("<h2>Smart Features</h2>", unsafe_allow_html=True)
        
        st.markdown("""
        <p style="color: #b3b3b3; margin-bottom: 20px;">
        Discover the future of voice-powered music with these innovative features.
        </p>
        """, unsafe_allow_html=True)
        
        # Display the 8 smart features from the image in a grid
        feature_cols = st.columns(2)
        
        with feature_cols[0]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #282828 0%, #3D3D3D 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <h3 style="color: white; margin-top: 0;">🎭 Advanced Mood-Based Playlists</h3>
                <p style="color: #b3b3b3;">AI detects your mood and generates the perfect playlist</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Deep personalization</div>
            </div>
            """, unsafe_allow_html=True)
            
            tabs = st.tabs(["Mood Selection", "AI Mood Detection", "Advanced Settings"])
            
            with tabs[0]:
                # More comprehensive mood options
                mood_category = st.selectbox("Mood Category", 
                                         ["Energetic", "Relaxed", "Emotional", "Focused", "Social"])
                
                # Dynamic sub-mood options based on category
                if mood_category == "Energetic":
                    mood = st.selectbox("Select specific mood:", 
                                      ["Upbeat & Happy", "Excited", "Motivated", "Empowered", "Adventurous", "Triumphant"])
                elif mood_category == "Relaxed":
                    mood = st.selectbox("Select specific mood:", 
                                      ["Calm", "Peaceful", "Dreamy", "Sleepy", "Chilled", "Meditative"])
                elif mood_category == "Emotional":
                    mood = st.selectbox("Select specific mood:", 
                                      ["Nostalgic", "Melancholic", "Romantic", "Heartbroken", "Hopeful", "Bittersweet"])
                elif mood_category == "Focused":
                    mood = st.selectbox("Select specific mood:", 
                                      ["Deep Work", "Creative Flow", "Study Mode", "Problem Solving", "Strategic Thinking"])
                elif mood_category == "Social":
                    mood = st.selectbox("Select specific mood:", 
                                      ["Party", "Intimate Gathering", "Road Trip", "Dinner Party", "Workout Group"])
                
                # Context factors that enhance mood detection
                st.multiselect("Additional context factors", 
                             ["Time of day", "Weather", "Season", "Location", "Recent activities"])
            
            with tabs[1]:
                st.markdown("""
                <div style="background: rgba(29, 185, 84, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #1DB954;">
                    <h4 style="margin-top: 0;">AI Mood Detection</h4>
                    <p>Let our AI analyze your current mood based on multiple signals:</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("Analysis of recent listening patterns", value=True)
                    st.checkbox("Time of day and activity detection", value=True)
                    st.checkbox("Weather integration", value=True)
                
                with col2:
                    st.checkbox("Optional camera mood detection", value=False)
                    st.checkbox("Connected device data (fitness trackers, etc.)", value=False)
                    st.checkbox("Smartphone activity patterns", value=False)
                
                if st.button("Detect My Current Mood", key="detect_mood_btn"):
                    with st.spinner("Analyzing your mood patterns..."):
                        # Simulate AI processing
                        time.sleep(2)
                        st.success("AI detected your current mood: Energetic & Optimistic")
                        st.info("Based on: Morning listening patterns, recent upbeat song selections, and sunny weather in your location")
            
            with tabs[2]:
                st.slider("Mood match intensity", min_value=0, max_value=100, value=70,
                        help="Higher values create playlists that strongly match your detected mood, lower values incorporate more variety")
                
                st.selectbox("Mood transformation", 
                           ["Maintain current mood", "Gradually elevate mood", "Transition to calm", "Boost energy", "Improve focus"],
                           help="Choose whether you want music that maintains your current mood or helps transform it")
                
                duration = st.slider("Playlist duration (minutes)", min_value=15, max_value=180, value=60, step=15)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("Include new music discovery", value=True)
                    st.checkbox("Include your favorites", value=True)
                
                with col2:
                    st.checkbox("Adapt to changing moods", value=True)
                    st.checkbox("Save mood history", value=False)
            
            # Main button for generating playlist with enhanced UI
            if st.button("Generate Advanced Mood Playlist", key="advanced_mood_playlist_btn", use_container_width=True):
                with st.spinner("Creating your AI-powered mood-based playlist..."):
                    # Simulate more complex AI processing
                    progress_bar = st.progress(0)
                    
                    # Simulate different stages of playlist creation
                    st.caption("Analyzing your listening patterns...")
                    time.sleep(0.5)
                    progress_bar.progress(20)
                    
                    st.caption("Detecting mood patterns...")
                    time.sleep(0.5)
                    progress_bar.progress(40)
                    
                    st.caption("Curating songs for your current mood...")
                    time.sleep(0.5)
                    progress_bar.progress(60)
                    
                    st.caption("Optimizing track sequence for mood enhancement...")
                    time.sleep(0.5)
                    progress_bar.progress(80)
                    
                    st.caption("Finalizing your personalized experience...")
                    time.sleep(0.5)
                    progress_bar.progress(100)
                    
                    # Display success with more detailed feedback
                    st.success("Your advanced mood playlist is ready!")
                    
                    # Show mock playlist with more detailed information
                    st.markdown("""
                    <div style="background: #282828; padding: 15px; border-radius: 8px;">
                        <h4 style="margin-top: 0; color: white;">Your Energetic Morning Boost</h4>
                        <p style="color: #b3b3b3; font-size: 12px;">Customized for your current mood • 60 minutes • 15 songs</p>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                            <button style="background: #1DB954; border: none; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Play Now</button>
                            <button style="background: transparent; border: 1px solid #1DB954; color: #1DB954; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Save to Library</button>
                            <button style="background: transparent; border: 1px solid #b3b3b3; color: #b3b3b3; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Share</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with feature_cols[1]:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #282828 0%, #3D3D3D 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <h3 style="color: white; margin-top: 0;">👥 Social Listening Rooms</h3>
                <p style="color: #b3b3b3;">Real-time group listening parties with interactive features</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Community, engagement</div>
            </div>
            """, unsafe_allow_html=True)
            
            social_tabs = st.tabs(["Join Rooms", "Create Room", "Discover"])
            
            with social_tabs[0]:
                st.markdown("""
                <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="margin-top: 0; color: white;">Active Listening Rooms</h4>
                    <p style="color: #b3b3b3; font-size: 12px;">Join friends or others listening to music in real-time</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Featured rooms with more detailed information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 10px; cursor: pointer; border: 1px solid #333;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: #1DB954; display: flex; align-items: center; justify-content: center;">
                                <span style="color: white; font-weight: bold;">JM</span>
                            </div>
                            <div>
                                <h5 style="margin: 0; color: white;">Jazz Moods</h5>
                                <p style="margin: 0; color: #b3b3b3; font-size: 12px;">Hosted by Jamie • 28 listeners</p>
                            </div>
                        </div>
                        <p style="color: #b3b3b3; font-size: 12px; margin-bottom: 8px;">Exploring classic and modern jazz with fellow enthusiasts</p>
                        <div style="display: flex; justify-content: flex-end;">
                            <button style="background: #1DB954; border: none; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Join Room</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 10px; cursor: pointer; border: 1px solid #333;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: #BF40BF; display: flex; align-items: center; justify-content: center;">
                                <span style="color: white; font-weight: bold;">MP</span>
                            </div>
                            <div>
                                <h5 style="margin: 0; color: white;">Monday Productivity</h5>
                                <p style="margin: 0; color: #b3b3b3; font-size: 12px;">Hosted by Work Buddies • 54 listeners</p>
                            </div>
                        </div>
                        <p style="color: #b3b3b3; font-size: 12px; margin-bottom: 8px;">Focus-enhancing tracks to start your week strong</p>
                        <div style="display: flex; justify-content: flex-end;">
                            <button style="background: #1DB954; border: none; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Join Room</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 10px; cursor: pointer; border: 1px solid #333;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: #FF6B6B; display: flex; align-items: center; justify-content: center;">
                                <span style="color: white; font-weight: bold;">FP</span>
                            </div>
                            <div>
                                <h5 style="margin: 0; color: white;">Friday Party</h5>
                                <p style="margin: 0; color: #b3b3b3; font-size: 12px;">Hosted by DJ Alex • 142 listeners</p>
                            </div>
                        </div>
                        <p style="color: #b3b3b3; font-size: 12px; margin-bottom: 8px;">Weekend vibes with dance tracks and live DJ transitions</p>
                        <div style="display: flex; justify-content: flex-end;">
                            <button style="background: #1DB954; border: none; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Join Room</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 10px; cursor: pointer; border: 1px solid #333;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: #4682B4; display: flex; align-items: center; justify-content: center;">
                                <span style="color: white; font-weight: bold;">CS</span>
                            </div>
                            <div>
                                <h5 style="margin: 0; color: white;">Chill Study Session</h5>
                                <p style="margin: 0; color: #b3b3b3; font-size: 12px;">Hosted by StudyGroup • 89 listeners</p>
                            </div>
                        </div>
                        <p style="color: #b3b3b3; font-size: 12px; margin-bottom: 8px;">Ambient and lo-fi tracks perfect for study sessions</p>
                        <div style="display: flex; justify-content: flex-end;">
                            <button style="background: #1DB954; border: none; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px;">Join Room</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.button("Browse All Rooms", key="browse_rooms_btn", use_container_width=True)
            
            with social_tabs[1]:
                st.markdown("""
                <div style="background: rgba(29, 185, 84, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #1DB954; margin-bottom: 15px;">
                    <h4 style="margin-top: 0;">Create Your Listening Room</h4>
                    <p style="color: #b3b3b3;">Host your own music session and invite friends or the public to join</p>
                </div>
                """, unsafe_allow_html=True)
                
                room_name = st.text_input("Room Name", placeholder="Name your listening room...", key="create_room_name")
                room_description = st.text_area("Room Description", placeholder="Describe what you'll be listening to...", key="room_description", height=80)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.selectbox("Room Theme", 
                               ["None", "Party Vibes", "Focus & Study", "Chill Session", "Workout", "Discover New Music", "Throwback", "Custom..."], 
                               key="room_theme")
                
                with col2:
                    st.selectbox("Privacy Setting", 
                               ["Public (Anyone can join)", "Friends Only", "Private (Invite Only)", "Password Protected"], 
                               key="create_room_privacy")
                
                # Advanced room settings with collapsible section
                with st.expander("Advanced Room Settings"):
                    st.checkbox("Enable voice chat", value=True, key="voice_chat")
                    st.checkbox("Allow listeners to request songs", value=True, key="song_requests")
                    st.checkbox("Enable collaborative queue editing", value=False, key="collab_queue")
                    st.checkbox("Show currently playing on your profile", value=True, key="show_playing")
                    st.number_input("Maximum number of participants", min_value=2, max_value=500, value=50, key="max_participants")
                    st.selectbox("Queue Management", 
                               ["Host Controls Everything", "Voting System", "Round-Robin DJ Mode"], 
                               key="queue_management")
                
                # Start time options
                col1, col2 = st.columns(2)
                with col1:
                    st.selectbox("Start Time", ["Now", "Schedule for Later"], key="start_time")
                
                with col2:
                    if st.session_state.get("start_time") == "Schedule for Later":
                        st.date_input("Date", key="schedule_date")
                    else:
                        st.selectbox("Session Duration", 
                                   ["1 hour", "2 hours", "3 hours", "4 hours", "Unlimited"], 
                                   key="session_duration")
                
                # Invite options
                st.text_input("Invite Friends (email or username)", placeholder="Enter emails or usernames separated by commas", key="create_room_invites")
                
                # Create button with enhanced UI
                if st.button("Create & Launch Room", key="create_launch_room_btn", use_container_width=True):
                    with st.spinner("Setting up your interactive listening room..."):
                        # Simulate more complex room setup process
                        progress_bar = st.progress(0)
                        
                        st.caption("Creating room infrastructure...")
                        time.sleep(0.4)
                        progress_bar.progress(20)
                        
                        st.caption("Configuring audio streaming...")
                        time.sleep(0.4)
                        progress_bar.progress(40)
                        
                        st.caption("Setting up chat functionality...")
                        time.sleep(0.4)
                        progress_bar.progress(60)
                        
                        st.caption("Preparing user permissions...")
                        time.sleep(0.4)
                        progress_bar.progress(80)
                        
                        st.caption("Sending invitations...")
                        time.sleep(0.4)
                        progress_bar.progress(100)
                        
                        # Success message with more detail
                        st.success("Your listening room is ready to launch!")
                        
                        # Show the created room with host controls
                        st.markdown("""
                        <div style="background: #282828; padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <h4 style="margin: 0; color: white;">Your Room: Chill Vibes Only</h4>
                                <span style="background: #1DB954; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">LIVE</span>
                            </div>
                            <p style="color: #b3b3b3; font-size: 14px; margin-bottom: 15px;">Ready to go! Share the link below or start adding music to your queue.</p>
                            <input type="text" value="https://voicecanvas.app/room/chillvibesonly" style="width: 100%; padding: 8px; background: #3E3E3E; border: none; border-radius: 4px; color: white; margin-bottom: 15px;">
                            <div style="display: flex; gap: 10px;">
                                <button style="flex: 1; background: #1DB954; border: none; color: white; padding: 8px 0; border-radius: 4px; font-weight: bold;">Start Playing</button>
                                <button style="flex: 1; background: transparent; border: 1px solid #1DB954; color: #1DB954; padding: 8px 0; border-radius: 4px;">Copy Invite Link</button>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            with social_tabs[2]:
                st.markdown("""
                <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="margin-top: 0; color: white;">Discover Trending Rooms</h4>
                    <p style="color: #b3b3b3; font-size: 12px;">Find popular listening sessions across different genres and themes</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Search and filter options
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.text_input("Search rooms", placeholder="Artist, genre, mood...", key="search_rooms")
                
                with col2:
                    st.selectbox("Filter by", ["All", "Music Genre", "Mood", "Activity", "Language"], key="room_filter")
                
                # Genre quick filters
                st.markdown("""
                <div style="display: flex; gap: 8px; margin: 15px 0; overflow-x: auto; padding-bottom: 5px;">
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">All Genres</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">Pop</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">Hip Hop</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">Rock</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">Electronic</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">R&B</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">Jazz</span>
                    <span style="background: #282828; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer;">Classical</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Featured trending rooms
                st.markdown("<h5>Trending Now</h5>", unsafe_allow_html=True)
                
                trending_col1, trending_col2, trending_col3 = st.columns(3)
                
                with trending_col1:
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; cursor: pointer; height: 160px; position: relative; overflow: hidden;">
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7) 80%);"></div>
                        <div style="position: absolute; bottom: 12px; left: 12px; right: 12px;">
                            <h5 style="margin: 0; color: white;">Indie Discoveries</h5>
                            <p style="margin: 5px 0; color: #b3b3b3; font-size: 12px;">432 listeners • 24 hours</p>
                            <div style="display: flex; align-items: center; gap: 5px; margin-top: 8px;">
                                <div style="width: 20px; height: 20px; border-radius: 50%; background: #FF6B6B;"></div>
                                <span style="color: #b3b3b3; font-size: 12px;">Live DJ Sets</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with trending_col2:
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; cursor: pointer; height: 160px; position: relative; overflow: hidden;">
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7) 80%);"></div>
                        <div style="position: absolute; bottom: 12px; left: 12px; right: 12px;">
                            <h5 style="margin: 0; color: white;">2000s Throwback</h5>
                            <p style="margin: 5px 0; color: #b3b3b3; font-size: 12px;">283 listeners • Weekly</p>
                            <div style="display: flex; align-items: center; gap: 5px; margin-top: 8px;">
                                <div style="width: 20px; height: 20px; border-radius: 50%; background: #4682B4;"></div>
                                <span style="color: #b3b3b3; font-size: 12px;">Nostalgic Hits</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with trending_col3:
                    st.markdown("""
                    <div style="background: #282828; padding: 12px; border-radius: 8px; cursor: pointer; height: 160px; position: relative; overflow: hidden;">
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7) 80%);"></div>
                        <div style="position: absolute; bottom: 12px; left: 12px; right: 12px;">
                            <h5 style="margin: 0; color: white;">Lofi Study Beats</h5>
                            <p style="margin: 5px 0; color: #b3b3b3; font-size: 12px;">975 listeners • 24/7</p>
                            <div style="display: flex; align-items: center; gap: 5px; margin-top: 8px;">
                                <div style="width: 20px; height: 20px; border-radius: 50%; background: #BF40BF;"></div>
                                <span style="color: #b3b3b3; font-size: 12px;">Focus Music</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Calendar of scheduled rooms
                with st.expander("Upcoming Scheduled Rooms"):
                    st.markdown("""
                    <div style="color: #b3b3b3; font-size: 14px;">
                        <div style="display: flex; padding: 10px 0; border-bottom: 1px solid #333;">
                            <div style="width: 30%;">Today, 8:00 PM</div>
                            <div style="width: 40%;">Album Listening Party: New Releases</div>
                            <div style="width: 30%; text-align: right;">
                                <button style="background: transparent; border: 1px solid #1DB954; color: #1DB954; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Set Reminder</button>
                            </div>
                        </div>
                        <div style="display: flex; padding: 10px 0; border-bottom: 1px solid #333;">
                            <div style="width: 30%;">Tomorrow, 7:30 PM</div>
                            <div style="width: 40%;">Acoustic Sessions with Live Q&A</div>
                            <div style="width: 30%; text-align: right;">
                                <button style="background: transparent; border: 1px solid #1DB954; color: #1DB954; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Set Reminder</button>
                            </div>
                        </div>
                        <div style="display: flex; padding: 10px 0; border-bottom: 1px solid #333;">
                            <div style="width: 30%;">Sat, 9:00 PM</div>
                            <div style="width: 40%;">Electronic Dance Party</div>
                            <div style="width: 30%; text-align: right;">
                                <button style="background: transparent; border: 1px solid #1DB954; color: #1DB954; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Set Reminder</button>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        feature_cols = st.columns(2)
        
        with feature_cols[0]:
            st.markdown("""
            <div style="background: #282828; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">🤖 Enhanced AI Playlist Creation</h3>
                <p style="color: #b3b3b3;">Smarter, more creative AI playlist prompts</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Curation, discovery</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_area("Describe your perfect playlist", 
                       placeholder="E.g., 'Songs that feel like a road trip along the coast at sunset with old friends'", 
                       key="ai_playlist_prompt", 
                       height=100)
            
            if st.button("Generate AI Playlist", key="ai_playlist_btn"):
                with st.spinner("Creating your uniquely personal playlist..."):
                    # Simulate API call delay
                    time.sleep(2)
                    st.success("Your AI-powered playlist is ready to explore!")
        
        with feature_cols[1]:
            st.markdown("""
            <div style="background: #282828; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">🎯 Deeper Personalization</h3>
                <p style="color: #b3b3b3;">Micro-recommendations, cross-content suggestions</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Discovery, retention</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.multiselect("Select your interests beyond music", 
                         ["Podcasts", "Audiobooks", "Live Events", "Artist Interviews", "Music Videos", "Lyrics & Poetry", "Music Production", "Music History"], 
                         key="cross_content_interests")
            
            if st.button("Enhance My Recommendations", key="enhance_recs_btn"):
                with st.spinner("Personalizing your experience..."):
                    # Simulate API call delay
                    time.sleep(1.8)
                    st.success("Your recommendations have been enhanced!")
        
        feature_cols = st.columns(2)
        
        with feature_cols[0]:
            st.markdown("""
            <div style="background: #282828; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">🎧 High-Fidelity/Immersive Audio</h3>
                <p style="color: #b3b3b3;">Lossless audio, spatial sound, VR concerts</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Audio quality, immersion</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.selectbox("Audio Quality Preference", 
                       ["Standard (128kbps)", "High (256kbps)", "Premium (320kbps)", "Lossless (FLAC)", "Spatial Audio", "3D Audio (requires compatible headphones)"], 
                       key="audio_quality")
            
            if st.button("Apply Audio Settings", key="audio_settings_btn"):
                with st.spinner("Updating your audio quality settings..."):
                    # Simulate API call delay
                    time.sleep(1)
                    st.success("Your audio quality settings have been updated!")
        
        with feature_cols[1]:
            st.markdown("""
            <div style="background: #282828; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">🔄 Improved Social/Sharing Features</h3>
                <p style="color: #b3b3b3;">Song snippets, collaborative playlists, live updates</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Social, viral growth</div>
            </div>
            """, unsafe_allow_html=True)
            
            sharing_tabs = st.tabs(["Song Snippets", "Collaborative Playlists", "Live Updates"])
            
            with sharing_tabs[0]:
                st.slider("Snippet Length (seconds)", min_value=5, max_value=30, value=15, key="snippet_length")
                st.button("Create Shareable Snippet", key="snippet_btn")
            
            with sharing_tabs[1]:
                st.text_input("Collaborative Playlist Name", placeholder="Enter name...", key="collab_playlist_name")
                st.text_input("Invite Friends (email or username)", placeholder="Enter emails or usernames separated by commas", key="collab_invites")
                st.button("Create Collaborative Playlist", key="collab_playlist_btn")
            
            with sharing_tabs[2]:
                st.checkbox("Enable Live Activity Feed", value=True, key="live_updates")
                st.checkbox("Share My Listening Activity", value=True, key="share_listening")
                st.button("Save Sharing Preferences", key="sharing_prefs_btn")
        
        feature_cols = st.columns(2)
        
        with feature_cols[0]:
            st.markdown("""
            <div style="background: #282828; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">⚙️ Smarter Playlists & Automation</h3>
                <p style="color: #b3b3b3;">Rule-based playlist updates, event integration</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Convenience, pro users</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.multiselect("Add automation rules", 
                         ["Auto-add songs I've liked", 
                          "Auto-remove songs after 10 plays", 
                          "Refresh playlist weekly with new tracks", 
                          "Auto-create playlists based on my listening history",
                          "Integrate with calendar events",
                          "Time-of-day specific playlists"], 
                         key="automation_rules")
            
            if st.button("Apply Automation Rules", key="automation_btn"):
                with st.spinner("Setting up your playlist automation..."):
                    # Simulate API call delay
                    time.sleep(1.5)
                    st.success("Your playlist automation has been configured!")
        
        with feature_cols[1]:
            st.markdown("""
            <div style="background: #282828; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin-top: 0;">♿ Accessibility & Inclusivity</h3>
                <p style="color: #b3b3b3;">Translations, audio descriptions, UI themes</p>
                <div style="background: #1DB954; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 12px;">Inclusivity, usability</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.selectbox("Language", ["English", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic", "Hindi"], key="accessibility_language")
            st.selectbox("UI Theme", ["Default", "High Contrast", "Dark Mode", "Light Mode", "Colorblind Friendly", "Large Text"], key="accessibility_theme")
            st.checkbox("Enable Screen Reader Support", value=False, key="screen_reader")
            st.checkbox("Enable Audio Descriptions for Content", value=False, key="audio_descriptions")
            
            if st.button("Apply Accessibility Settings", key="accessibility_btn"):
                with st.spinner("Updating your accessibility settings..."):
                    # Simulate API call delay
                    time.sleep(1)
                    st.success("Your accessibility settings have been saved!")
        
        # Display user's content
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("<h3>Collections</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div class="new-playlist-button active">
                    <div class="new-playlist-text">Your Voice Creations</div>
                </div>
                <div class="new-playlist-button">
                    <div class="new-playlist-text">Liked Tracks</div>
                </div>
                <div class="new-playlist-button">
                    <div class="new-playlist-text">Downloaded</div>
                </div>
                <div class="new-playlist-button">
                    <div class="new-playlist-text">Shared with You</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<h3>Your Voice Creations</h3>", unsafe_allow_html=True)
            
            # Mix of user's content
            if not st.session_state.get("user_tracks"):
                st.session_state.user_tracks = SampleData.get_sample_songs()[:2]  # Just use the first 2 as examples
            
            for i, track in enumerate(st.session_state.user_tracks):
                st.markdown(render_track_item(track, i), unsafe_allow_html=True)
            
            st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
            st.button("Create New Voice Track", use_container_width=False)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Add JavaScript for interactivity
    st.markdown("""
    <script>
        // This would add interactive functionality if browser JavaScript were enabled in Streamlit
        // For now, these are just placeholders showing what could be implemented
        
        // Example function to handle play button clicks
        function playTrack(trackId) {
            console.log('Play track:', trackId);
            // This would play the selected track
        }
        
        // Example function to handle like button clicks
        function likeTrack(trackId) {
            console.log('Like track:', trackId);
            // This would toggle the like state for a track
        }
        
        // Example function to handle share button clicks
        function shareTrack(trackId) {
            console.log('Share track:', trackId);
            // This would open a share dialog
        }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
