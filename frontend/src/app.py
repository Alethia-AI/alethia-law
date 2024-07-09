import streamlit as st
import generation.response_generator as generator
from archive import build_archive
import time

import os

STARTING_SYSTEM_PROMPT = """You are a legal research assistant tasked with answering queries based on retrieved case law information. Your goal is to provide accurate, well-cited answers to legal questions using the provided case information.

            Here is the query you need to answer:
            <query>
            {{QUERY}}
            </query>

            Below are the retrieved results from the case law database. Each result contains information about a relevant case, including its details and a relevant text excerpt:

            <results>
            {{RESULTS}}
            </results>

            Analyze the retrieved results carefully. Pay attention to the relevance scores, case details, and the text excerpts provided. Focus on the most relevant cases (those with higher relevance scores) and consider how they relate to the query.

            To answer the query:
            1. Identify the key legal principles and arguments presented in the relevant cases.
            2. Synthesize the information to form a comprehensive answer to the query.
            3. Ensure that every statement or proposition in your answer is supported by a citation to a specific case.
            4. If there are conflicting viewpoints in the cases, present both sides and explain the reasoning behind each.

            When citing cases, use the Bluebook citation format. For majority opinions, use the following format:
            Case Name, Volume U.S. Reports Page (Year)
            Example: New York Times Co. v. Tasini, 533 U.S. 483 (2001)

            For dissenting or concurring opinions, use this format:
            Case Name, Volume U.S. Reports Page, Specific Page (Year) (Justice's Last Name, J., dissenting/concurring)
            Example: Parker v. Randolph, 442 U.S. 62, 84 (1979) (Stevens, J., dissenting)

            Structure your answer as follows:
            1. Begin with a brief summary of the legal question and the key principles involved.
            2. Present the main argument or answer to the query, citing relevant cases.
            3. If applicable, discuss any conflicting viewpoints or dissenting opinions.
            4. Conclude with a concise restatement of the answer to the query.

            Ensure that every legal principle or argument is supported by an appropriate case citation."""


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
                            value=STARTING_SYSTEM_PROMPT, 
                            key="prompt")
    if st.button("Submit", key="submit"):
        generator.change_system_prompt(user_name, system_prompt)

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
