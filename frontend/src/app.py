import streamlit as st
import time
import os
import json

from utils import utils
import concurrent.futures


# Define a function to generate the response in parallel
def generate_response(prompt, nprompt):
    non_augmented_message = utils.generator.non_augmented_generator(prompt)
    generator_response = utils.generator.generate_response(nprompt)
    return non_augmented_message, generator_response

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()
### CHAT_INTERFACE ###
with st.expander("**ARCHIVE**", expanded=True):

    case = st.file_uploader("Upload case", type=["pdf", "docx", "txt", "md"])
    if st.button("Upload", key="upload"):
        try:
            if case is not None:
                # Construct the full path where you want to save the file
                file_path = os.path.join(utils.save_dir, case.name)
                
                # Open the file in write-binary mode and save the content
                with open(file_path, "wb") as f:
                    f.write(case.getbuffer())
                
                response = utils.archive.upload_case(file_path)
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
                            value=utils.generator.get_system_prompt(), 
                            key="prompt")
    if st.button("Submit", key="submit"):
        if utils.generator.change_system_prompt(system_prompt):
            st.write("System prompt has been updated.")
        else:
            st.write("Error in updating system prompt.")

# initialize history
if "messages" not in st.session_state or "prompts" not in st.session_state:
    st.session_state.messages = []
    st.session_state.prompts = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    cols = st.columns(2)
    with cols[0]:
        with st.chat_message(message[0]["role"]):
            st.markdown(message[0]["content"])
    with cols[1]:
        with st.chat_message(message[1]["role"]):
            st.markdown(message[1]["content"])

if prompt := st.chat_input("What do you want to know?"):
    # Make sure that there are no double quotes in the prompt
    st.session_state.messages.append(({"role": "user", "content": prompt}, {"role": "user", "content": prompt}))
    with st.chat_message("user"):
        st.markdown(prompt)
        # Need to display a loading spinner
        with st.spinner("Searching the archive..."):
            time.sleep(2)
    # Generate the response
    prompt = prompt.replace('"', "")
    prompt = prompt.replace('\'', "")
    st.session_state.prompts.append(({"role": "user", "content": prompt}, {"role": "user", "content": prompt}))
    with st.spinner("Generating response..."):
        #start_time_rag = time.time()
        #end_time = time.time()
        #st.success(f"Time taken: {end_time - start_time_rag} seconds")
        prompt = json.dumps([{"role": m[0]["role"], "content": m[0]["content"]} for m in st.session_state.prompts])
        nprompt = json.dumps([{"role": m[1]["role"], "content": m[1]["content"]} for m in st.session_state.prompts])
        # Use concurrent.futures to run the function in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(generate_response, prompt, nprompt)
    with st.chat_message("assistant"):
        cols = st.columns(2)
        non_augmented_message, generator_response = future.result()
        with cols[0]:
            with st.expander("**ARCHIVE RESULTS**", expanded=False):
                # Also want to display the citations
                for citation in generator_response[1]:
                    st.write(citation)
            message = generator_response[0] if generator_response[0] else "No response generated"
            st.write(
                message
            )
            message_prompts = message.replace('"', "")
            message_prompts = message.replace('\'', "")
        with cols[1]:
            with st.expander("**LLM**", expanded=False):
                st.write("[claude-3-haiku-20240307](https://www.anthropic.com/news/claude-3-family)")
            st.write(
                non_augmented_message
            )
            non_augmented_message_prompts = non_augmented_message.replace('"', "")
            non_augmented_message_prompts = non_augmented_message.replace('\'', "")
    st.session_state.messages.append(({"role": "assistant", "content": message}, {"role": "assistant", "content": non_augmented_message}))
    st.session_state.prompts.append(({"role": "assistant", "content": message_prompts}, {"role": "assistant", "content": non_augmented_message_prompts}))
