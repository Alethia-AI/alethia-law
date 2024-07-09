import streamlit as st
import generation.response_generator as generator
from archive import build_archive
import time

import os


#st.title("!")

# Text box to enter the user's name
#user_name = st.text_input("Enter your name", key="name")
user_name = "Oliver"

# Assuming you want to save files in a directory named 'uploaded_cases' in the current working directory
save_dir = 'uploaded_cases'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

with st.expander("**ARCHIVE**", expanded=True):

    case = st.file_uploader("Upload case", type=["pdf", "docx", "txt", "md"])
    if st.button("Upload", key="upload"):
        try:
            if case is not None:
                # Construct the full path where you want to save the file
                file_path = os.path.join(save_dir, case.name)
                
                # Open the file in write-binary mode and save the content
                with open(file_path, "wb") as f:
                    f.write(case.getbuffer())
                
                response = build_archive.upload_case(user_name, file_path)
                st.write(response + ". It may take upto 5 minutes for the case to be processed in the archive.")
        except Exception as e:
            st.write(f"Error: {e}")

    
    #if st.button("Go to Archive", key="archive"):
    #    st.write(build_archive.get_archive())
    #if st.button("Clear Archive", key="clear"):
    #    build_archive.clear_archive()
    

with st.expander("**PROMPT**", expanded=True):
    # Have a textbox that allows the user to enter a prompt
    system_prompt = st.text_area(
                            "SYSTEM_PROMPT",
                            value=generator.get_system_prompt(user_name), 
                            key="prompt")
    if st.button("Submit", key="submit"):
        generator.change_system_prompt(user_name, system_prompt)
        st.write("System prompt has been updated.")

# initialize history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    start_time = time.time()
    generator_repsonse = generator.generate_response(user_name, prompt)
    end_time = time.time()
    st.write(f"Time taken: {end_time - start_time} seconds")
    with st.chat_message("assistant"):
        message = st.write(
            generator_repsonse
        )
    st.session_state.messages.append({"role": "assistant", "content": message})
