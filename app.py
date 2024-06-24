import streamlit as st
from streamlit_chat import message

from os.path import join as pjoin
import yaml

root = '.'
data_folder = 'data'
script_folder = 'scripts'
dialogue_folder = 'dialogues'
config_file = 'config.yaml'

with open(pjoin(root, config_file), 'r') as f:
    config = yaml.safe_load(f)

superheroes = config['LIST_OF_SUPERHEROES']

from query import get_response

def api_calling(question, superhero):
    message = get_response(question, superhero)
    return message

# Define superhero names

st.title("Chat with your favorite superhero!")

# Sidebar for superhero selection
st.sidebar.title("Superhero Selector")
selected_hero = st.sidebar.selectbox("Choose a superhero", superheroes)
# Display the selected superhero
st.sidebar.write(f"You selected: {selected_hero}")

# Initialize selected superhero in session state
if 'selected_hero' not in st.session_state:
    st.session_state['selected_hero'] = superheroes[0]  # Set default superhero

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []

if 'response' not in st.session_state:
    st.session_state['response'] = []

def get_text():
    input_text = st.text_input("write here", key="input")
    return input_text

user_input = get_text()

if user_input:
    output = api_calling(user_input, selected_hero)
    output = output.lstrip("\n")

    # Store the output
    st.session_state.response.append(user_input)
    st.session_state.user_input.append(output)

    # Clear the text input field
    user_input = ""  # Resetting the value to an empty string

message_history = st.empty()

if st.session_state['user_input']:
    for i in range(len(st.session_state['user_input']) - 1, -1, -1):
        # This function displays user input
        message(st.session_state["user_input"][i], 
                key=str(i),avatar_style="icons")
        # This function displays response
        message(st.session_state['response'][i], 
                avatar_style="miniavs",is_user=True,
                key=str(i) + 'data_by_user')
        # st.session_state['user_input'] = []

# Check if superhero selection has changed
if st.session_state['selected_hero'] != selected_hero:
    # Update selected superhero in session state
    st.session_state['selected_hero'] = selected_hero
    st.session_state['response'] = []
    st.session_state['user_input'] = []
    # Rerun the app to start fresh
    st.rerun()

# Update selected superhero in session state
st.session_state['selected_hero'] = selected_hero
