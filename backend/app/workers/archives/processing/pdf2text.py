from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownElementNodeParser

import os

load_dotenv()

class PDFProcessor:

    def __init__(self):
        self.parser = LlamaParse(
            api_key=os.environ.get("LLAMA_CLOUD_API_KEY"),
            result_type="text",  # "markdown" and "text" are available
            verbose=True,
        )

        self.file_extractor = {".pdf": self.parser}

        print("PDFProcessor initialized")

    async def process_file(self, path: str):
        print("Processing file: ", path)
        documents = await self.parser.aload_data(path)
        print("Documents processed: ", len(documents))
        text = ""
        for doc in documents:
            text += doc.text
            text += "\n"

        text_path = path.replace(".pdf", ".txt")
        with open(text_path, "w") as f:
            f.write(text)

        return text_path
    
    async def process_directory(self, path: str):
        documents = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".pdf"):
                    documents += await self.process_file(os.path.join(root, file))
        return documents

    
processor = PDFProcessor()