import streamlit as st
import time
import os

from utils import utils

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
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    print(message)
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        # Need to display a loading spinner
        with st.spinner("Searching the archive..."):
            time.sleep(2)
    # Generate the response
    with st.spinner("Generating response..."):
        start_time = time.time()
        generator_response = utils.generator.generate_response(prompt)
        end_time = time.time()
    st.success(f"Time taken: {end_time - start_time} seconds")
    with st.chat_message("assistant"):
        with st.expander("**ARCHIVE RESULTS**", expanded=False):
            # Also want to display the citations
            for citation in generator_response[1]:
                st.write(citation)
        message = generator_response[0] if generator_response[0] else "No response generated"
        st.write(
            message
        )
    st.session_state.messages.append({"role": "assistant", "content": message})
