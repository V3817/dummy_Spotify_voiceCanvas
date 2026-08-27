import streamlit as st
import uuid
import time
import random
from datetime import datetime

# Define Listening Room styles
listening_room_styles = """
<style>
    /* Listening Room Specific Styles */
    .listening-room-container {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .song-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        border-left: 3px solid #6C63FF;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .song-card:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .song-votes {
        font-size: 1.6rem;
        font-weight: 600;
        color: #6C63FF;
        margin-right: 12px;
    }
    
    .now-playing {
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border-left: 3px solid #FF6584;
        position: relative;
        overflow: hidden;
    }
    
    .now-playing::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
                   rgba(255,255,255,0) 0%, 
                   rgba(255,255,255,0.1) 50%, 
                   rgba(255,255,255,0) 100%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
    }
    
    .vote-button {
        background: rgba(108, 99, 255, 0.2);
        color: white;
        border: 1px solid rgba(108, 99, 255, 0.5);
        border-radius: 4px;
        padding: 5px 10px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .vote-button:hover {
        background: rgba(108, 99, 255, 0.4);
        transform: scale(1.05);
    }
    
    .room-code {
        background: rgba(0, 0, 0, 0.2);
        color: #FF6584;
        font-family: monospace;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    .equalizer {
        display: flex;
        align-items: flex-end;
        height: 15px;
        margin-left: 10px;
    }
    
    .equalizer-bar {
        width: 3px;
        background: #FF6584;
        margin-right: 2px;
        animation: equalize 1s infinite alternate;
    }
    
    .equalizer-bar:nth-child(1) { animation-delay: 0.0s; }
    .equalizer-bar:nth-child(2) { animation-delay: 0.1s; }
    .equalizer-bar:nth-child(3) { animation-delay: 0.2s; }
    .equalizer-bar:nth-child(4) { animation-delay: 0.1s; }
    .equalizer-bar:nth-child(5) { animation-delay: 0.2s; }
    
    @keyframes equalize {
        0% { height: 3px; }
        100% { height: 15px; }
    }
    
    .chat-container {
        max-height: 300px;
        overflow-y: auto;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        padding: 10px;
        margin-top: 15px;
    }
    
    .chat-message {
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        width: fit-content;
        max-width: 80%;
    }
    
    .my-message {
        background: rgba(108, 99, 255, 0.2);
        margin-left: auto;
        text-align: right;
    }
    
    .other-message {
        background: rgba(255, 255, 255, 0.05);
    }
    
    .message-sender {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 2px;
    }
    
    .message-content {
        font-size: 0.9rem;
    }
    
    .message-time {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 4px;
        text-align: right;
    }
    
    .participant-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 15px;
    }
    
    .participant-avatar {
        background: rgba(108, 99, 255, 0.3);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
    }
    
    .add-song-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
    }
</style>
"""

# Sample background music for this feature
SAMPLE_SONGS = [
    {"title": "Midnight Dreams", "artist": "Luna Echo", "duration": "3:45", "id": "song1", "source": "Library"},
    {"title": "Electric Sunset", "artist": "Neon Wave", "duration": "4:12", "id": "song2", "source": "Library"},
    {"title": "Mountain High", "artist": "The Climbers", "duration": "3:28", "id": "song3", "source": "Library"},
    {"title": "Ocean Breeze", "artist": "Coastal Vibes", "duration": "5:03", "id": "song4", "source": "Library"},
    {"title": "Urban Jungle", "artist": "City Lights", "duration": "2:55", "id": "song5", "source": "Library"}
]

# Sample room chat messages
SAMPLE_CHAT = [
    {"sender": "DJ Alex", "content": "Welcome to the Listening Room! Vote for your favorite songs.", "time": "5 min ago"},
    {"sender": "Mia", "content": "I'm loving the current playlist 🎵", "time": "3 min ago"},
    {"sender": "System", "content": "Now playing: Electric Sunset by Neon Wave", "time": "2 min ago"},
    {"sender": "Jake", "content": "Can someone add some jazz to the queue?", "time": "1 min ago"}
]

# Sample room participants
SAMPLE_PARTICIPANTS = [
    {"name": "DJ Alex", "is_host": True},
    {"name": "Mia", "is_host": False},
    {"name": "Jake", "is_host": False},
    {"name": "Sofia", "is_host": False},
    {"name": "You", "is_host": False}
]

def generate_room_code():
    """Generate a unique room code for the listening room."""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))

def run_listening_room():
    """Run the Listening Room feature."""
    
    # Apply Listening Room styles
    st.markdown(listening_room_styles, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎧 The Listening Room</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Collaborative Music Experience</h2>', unsafe_allow_html=True)
    
    # Initialize session state variables for Listening Room
    if 'listening_room_active' not in st.session_state:
        st.session_state.listening_room_active = False
    if 'room_code' not in st.session_state:
        st.session_state.room_code = generate_room_code()
    if 'room_name' not in st.session_state:
        st.session_state.room_name = "My Listening Room"
    if 'playlist' not in st.session_state:
        st.session_state.playlist = SAMPLE_SONGS.copy()
        for song in st.session_state.playlist:
            song['votes'] = random.randint(0, 5)
    if 'now_playing' not in st.session_state:
        # Start with the most voted song
        most_voted = max(st.session_state.playlist, key=lambda x: x.get('votes', 0))
        st.session_state.now_playing = most_voted['id']
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = SAMPLE_CHAT.copy()
    if 'participants' not in st.session_state:
        st.session_state.participants = SAMPLE_PARTICIPANTS.copy()
    if 'user_voted_songs' not in st.session_state:
        st.session_state.user_voted_songs = set()
    
    # Room setup section
    if not st.session_state.listening_room_active:
        st.markdown("### Create or Join a Listening Room")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Create New Room")
            room_name = st.text_input("Room Name", value="My Listening Room")
            username = st.text_input("Your Display Name", value="DJ")
            
            if st.button("Create Room"):
                st.session_state.room_name = room_name
                st.session_state.room_code = generate_room_code()
                st.session_state.participants[4]["name"] = username
                st.session_state.participants[4]["is_host"] = True
                st.session_state.listening_room_active = True
                st.rerun()
                
        with col2:
            st.markdown("#### Join Existing Room")
            join_code = st.text_input("Room Code")
            join_name = st.text_input("Your Display Name", value="Guest")
            
            if st.button("Join Room"):
                # In a real app, this would validate the room code
                if join_code:
                    st.session_state.room_code = join_code
                    st.session_state.participants[4]["name"] = join_name
                    st.session_state.listening_room_active = True
                    st.rerun()
                else:
                    st.error("Please enter a valid room code")
        
        # Display sample room preview
        st.markdown("### Room Preview")
        st.markdown(
            f"""
            <div class="listening-room-container">
                <h3>{st.session_state.room_name}</h3>
                <p>5 participants · 5 songs in queue</p>
                <div class="song-card now-playing">
                    <div style="display: flex; align-items: center;">
                        <span class="song-votes">3</span>
                        <div>
                            <strong>Electric Sunset</strong> · Neon Wave
                            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">4:12</div>
                        </div>
                        <div class="equalizer" style="margin-left: auto;">
                            <div class="equalizer-bar" style="height: 8px;"></div>
                            <div class="equalizer-bar" style="height: 13px;"></div>
                            <div class="equalizer-bar" style="height: 5px;"></div>
                            <div class="equalizer-bar" style="height: 10px;"></div>
                            <div class="equalizer-bar" style="height: 7px;"></div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    else:
        # Active Listening Room UI
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Room header with code
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                    <h3>{st.session_state.room_name}</h3>
                    <div style="display: flex; align-items: center;">
                        <span style="margin-right: 10px;">Room Code:</span>
                        <span class="room-code">{st.session_state.room_code}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Now Playing section
            now_playing_song = next((song for song in st.session_state.playlist if song['id'] == st.session_state.now_playing), None)
            if now_playing_song:
                st.markdown(
                    f"""
                    <div class="listening-room-container" style="background: linear-gradient(135deg, #2d2d44 0%, #1e1e2f 100%);">
                        <h3>Now Playing</h3>
                        <div class="song-card now-playing">
                            <div style="display: flex; align-items: center;">
                                <span class="song-votes">{now_playing_song.get('votes', 0)}</span>
                                <div>
                                    <strong>{now_playing_song['title']}</strong> · {now_playing_song['artist']}
                                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">{now_playing_song['duration']} · {now_playing_song['source']}</div>
                                </div>
                                <div class="equalizer" style="margin-left: auto;">
                                    <div class="equalizer-bar" style="height: 8px;"></div>
                                    <div class="equalizer-bar" style="height: 13px;"></div>
                                    <div class="equalizer-bar" style="height: 5px;"></div>
                                    <div class="equalizer-bar" style="height: 10px;"></div>
                                    <div class="equalizer-bar" style="height: 7px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Song Queue section
            st.markdown(
                """
                <div class="listening-room-container">
                    <h3>Vote for Next Songs</h3>
                """,
                unsafe_allow_html=True
            )
            
            # Sort playlist by votes, excluding the currently playing song
            sorted_playlist = sorted(
                [song for song in st.session_state.playlist if song['id'] != st.session_state.now_playing],
                key=lambda x: x.get('votes', 0),
                reverse=True
            )
            
            for i, song in enumerate(sorted_playlist):
                # Create columns for song info and vote button
                song_col, vote_col = st.columns([5, 1])
                
                with song_col:
                    st.markdown(
                        f"""
                        <div class="song-card">
                            <div style="display: flex; align-items: center;">
                                <span class="song-votes">{song.get('votes', 0)}</span>
                                <div>
                                    <strong>{song['title']}</strong> · {song['artist']}
                                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">{song['duration']} · {song['source']}</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with vote_col:
                    # Vote button
                    voted = song['id'] in st.session_state.user_voted_songs
                    if st.button(
                        "👍 Voted" if voted else "👍 Vote", 
                        key=f"vote_{song['id']}",
                        disabled=voted
                    ):
                        # Add vote to song
                        for s in st.session_state.playlist:
                            if s['id'] == song['id']:
                                s['votes'] = s.get('votes', 0) + 1
                                break
                        
                        # Add to user's voted songs
                        st.session_state.user_voted_songs.add(song['id'])
                        
                        # Add message to chat
                        st.session_state.chat_messages.append({
                            "sender": st.session_state.participants[4]["name"],
                            "content": f"I voted for {song['title']} by {song['artist']}",
                            "time": "just now"
                        })
                        
                        st.rerun()
            
            # Add song button
            if st.button("➕ Add Song to Queue"):
                # In a real app, this would open a search interface
                # For demo, add a random song
                new_song = {
                    "title": f"New Song {uuid.uuid4().hex[:4]}",
                    "artist": "User Added",
                    "duration": f"{random.randint(2, 5)}:{random.randint(10, 59):02d}",
                    "id": f"user_song_{uuid.uuid4().hex[:8]}",
                    "source": "User Added",
                    "votes": 1
                }
                
                st.session_state.playlist.append(new_song)
                st.session_state.user_voted_songs.add(new_song['id'])
                
                # Add message to chat
                st.session_state.chat_messages.append({
                    "sender": st.session_state.participants[4]["name"],
                    "content": f"I added {new_song['title']} to the queue",
                    "time": "just now"
                })
                
                st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Skip button for the host
            if st.session_state.participants[4]["is_host"]:
                if st.button("⏭️ Skip to Next Song"):
                    # Find the most voted song to play next
                    next_songs = [song for song in st.session_state.playlist if song['id'] != st.session_state.now_playing]
                    if next_songs:
                        most_voted = max(next_songs, key=lambda x: x.get('votes', 0))
                        st.session_state.now_playing = most_voted['id']
                        
                        # Add message to chat
                        st.session_state.chat_messages.append({
                            "sender": "System",
                            "content": f"Now playing: {most_voted['title']} by {most_voted['artist']}",
                            "time": "just now"
                        })
                        
                        st.rerun()
        
        with col2:
            # Chat and Participants section
            st.markdown(
                """
                <div class="listening-room-container">
                    <h3>Room Chat</h3>
                """,
                unsafe_allow_html=True
            )
            
            # Chat messages
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            for message in st.session_state.chat_messages:
                message_class = "my-message" if message["sender"] == st.session_state.participants[4]["name"] else "other-message"
                st.markdown(
                    f"""
                    <div class="chat-message {message_class}">
                        <div class="message-sender">{message["sender"]}</div>
                        <div class="message-content">{message["content"]}</div>
                        <div class="message-time">{message["time"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Chat input
            chat_message = st.text_input("Type a message", key="chat_input")
            if st.button("Send") and chat_message:
                # Add message to chat
                st.session_state.chat_messages.append({
                    "sender": st.session_state.participants[4]["name"],
                    "content": chat_message,
                    "time": "just now"
                })
                
                # Clear input (this doesn't work directly in Streamlit, but would in a real app)
                st.rerun()
            
            # Participants section
            st.markdown("<h3>Participants</h3>", unsafe_allow_html=True)
            st.markdown('<div class="participant-container">', unsafe_allow_html=True)
            
            for participant in st.session_state.participants:
                initial = participant["name"][0].upper()
                host_label = " (Host)" if participant["is_host"] else ""
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-right: 10px;">
                        <div class="participant-avatar" style="background: {'rgba(255, 101, 132, 0.3)' if participant['is_host'] else 'rgba(108, 99, 255, 0.3)'}">
                            {initial}
                        </div>
                        <div style="margin-left: 8px; font-size: 0.9rem;">
                            {participant["name"]}{host_label}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Leave room button
            if st.button("Leave Room"):
                st.session_state.listening_room_active = False
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
