import os
import generation.response_generator as ResponseGenerator
from archive.build_archive import Archive


BACKEND_URL="https://alethia-law.onrender.com"
#BACKEND_URL="http://localhost:5001"
backend_url = BACKEND_URL

#st.title("!")

# Text box to enter the user's name
#user_name = st.text_input("Enter your name", key="name")
user_name = "Oliver"
# Assuming you want to save files in a directory named 'uploaded_cases' in the current working directory
save_dir = 'uploaded_cases'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

class Utils:
    def __init__(self):
        self.user_name = user_name
        self.save_dir = save_dir
        self.archive = Archive(user_name, backend_url)
        self.generator = ResponseGenerator.ResponseGenerator(user_name, backend_url)

utils = Utils()