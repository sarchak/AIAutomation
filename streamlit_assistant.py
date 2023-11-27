import io
import os
from assistants import *
import streamlit as st

from dotenv import load_dotenv

load_dotenv()
from elevenlabs import generate, stream, play
from elevenlabs import set_api_key
import base64
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def play_text(data):
    song = AudioSegment.from_file(io.BytesIO(data), format="mp3")
    play(song)


def play_from_file(filepath):
    data = open(filepath, "rb").read()
    song = AudioSegment.from_file(io.BytesIO(data), format="mp3")
    play(song)


set_api_key(os.environ["ELEVENLABS_API_KEY"])

st.title("McHelper Bot")
st.header("McDonald's Drive thru assistant")

instructions = """
Role: As McHelper, your primary role is to assist customers in choosing from the McDonald's menu. 
Your focus is on providing information about the menu items, including descriptions, ingredients, and any special promotions. 
You should suggest additional items to complement a customer's order, but limit these suggestions to maximum one during the interaction to avoid being perceived as pushy or irritating.

Approach: You possess extensive knowledge of the McDonald's menu and are skilled in guiding customers through their choices, 
ensuring they are aware of all relevant options. You take note of any specific dietary preferences or requests, 
such as vegetarian, vegan, or gluten-free needs. Your suggestions for additional items should be based on the customer's 
current selection and their stated preferences.

Interaction: Maintain a friendly and helpful demeanor, prioritizing the customer's needs and preferences.
After making one thoughtful suggestions, focus solely on providing information and answering questions about the menu. 
Avoid repeated or aggressive upselling techniques. Your goal is to ensure a pleasant and efficient ordering experience, 
respecting the customer's choices and time.
"""

if "assistant_id" not in st.session_state:
    print("Creating assistant")
    assistant_id = create_assistant(
        "McHelper", instructions, retrieval_file="mcdonalds_menu.txt"
    )
    st.session_state.assistant_id = assistant_id

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What would you like to order today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        tmp_run = None
        messages = []
        if "thread" not in st.session_state and "run" not in st.session_state:
            thread, run = create_thread_and_run(st.session_state.assistant_id, prompt)
            st.session_state.thread = thread
            st.session_state.run = run
            _ = wait_on_run(run, st.session_state.thread)
            messages = get_response(st.session_state.thread)
        else:
            run = submit_message(
                st.session_state.assistant_id, st.session_state.thread, prompt
            )
            _ = wait_on_run(run, st.session_state.thread)
            messages = get_response(st.session_state.thread)

        pretty_print(messages)
        message_placeholder = st.empty()
        full_response = ""
        assistant_message = messages.data[-1].content[0].text.value
        message_placeholder.write(assistant_message)
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_message}
        )
        ## Elevenlabs
        # audio = generate(
        #     text=assistant_message,
        #     voice="Amilia",
        #     model="eleven_multilingual_v2",
        # )
        # play_text(audio)

        # 0o009=9876543
        # message_placeholder = st.empty()
        # full_response = ""
        # message_placeholder.write("hello there")
