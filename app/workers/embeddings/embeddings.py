from os import environ
from openai import OpenAI
import numpy as np
from numpy.linalg import norm

# Load dotenv file
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=environ["OPENAI_API_KEY"])

def build_embeddings(title, texts):
    embeddings = []
    title_embedding = client.embeddings.create(input=title, model="text-embedding-3-small").data[0].embedding
    title_embedding = title_embedding / (norm(title_embedding))
    relevancy_threshold = 10
    count = 0
    print(f"Title: {title}")
    #print(f"Building embeddings for {len(text)} paragraphs")
    for i in range(len(texts)):
        #print(f"Building embedding for paragraph {i}")
        text_embedding = client.embeddings.create(input=texts[i], model="text-embedding-3-small").data[0].embedding
        text_embedding = text_embedding / (norm(text_embedding))
        embedding_i = []
        relevancy = find_relevancy(title_embedding, text_embedding)
        #print(f"Text: {text[i]}")
        #print(f"Relevancy: {relevancy}")
        if relevancy > relevancy_threshold:
            embedding_i.append(1)
            embedding_i.append(text_embedding)
            count += 1
        else:
            embedding_i.append(0)
            embedding_i.append(None)
        embeddings.append(embedding_i)
    print(f"Number of embeddings built: {count}")
    return embeddings

def find_relevancy(title_embedding, text_embedding):
    # Calculate cosine similarity between title and text embeddings
    similarity_score = np.dot(title_embedding, text_embedding)
    return similarity_score * 100


def prompt_embedding(prompt):
    return client.embeddings.create(input=prompt, model="text-embedding-3-small").data[0].embedding
