import json
import os
import re

import openai
from openai import OpenAI

from cachetools import cached, TTLCache
from pinecone import Pinecone, ServerlessSpec

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

GPT35 = "gpt-3.5-turbo"
GPT4 = "gpt-4o"
EMBEDDING_MODEL_3_LARGE = "text-embedding-3-large"

# Load contents of Equifax 10-K document for retrieval 
with open('equifax_10k_contents.json', 'r') as file:
    pages = json.load(file)

SYSTEM_PROMPT = '''You are an elite cybsersecurity analyst with an emphasis on investigating corporate cyber attacks. You have a reputation for being thorough and precise when 
providing answers and not making assumptions or jumping to conclusions without sufficient evidence and reasoning.
Your task is to use only the page excerpts from SEC 10-K filings on Equifax to answer general questions about the company and the cyber security breach that occurred. 
Return a concise and thorough response if the information provided in the pages can answer the query.

PAGE EXCERPTS:
'''

REMINDER_PROMPT = '''REMINDERS: 
- Ensure that you only answer questions supported by the page excerpts and don't make inferences that are not supported by the text
- Recall that 'Brexit' refers to the event of UK splitting from the EU during that time in 2017/2018
- If the query is not related to Equifax or the security breach at all or can't be answered with the provided information simply return 'No relevant information' then explain why and don't generate further tokens
'''

cache = TTLCache(maxsize=10000, ttl=12 * 60 * 60)

@cached(cache)
def get_api_response(system_message, user_message, model="gpt-3.5-turbo", use_reminder_prompt=False):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    if use_reminder_prompt:
        messages.append({"role": "user", "content" : REMINDER_PROMPT})
    response = client.chat.completions.create(
            model=model,
            messages=messages 
    )
    # Extract and return the response content
    return response.choices[0].message.content

@cached(cache)
def generate_embedding(text, model=EMBEDDING_MODEL_3_LARGE):
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=text,
        model=model,
        dimensions=256
    )
    emb = response.data[0].embedding
    return emb

def add_vector_to_db(text, id_val, index_name):
     embedding = generate_embedding(text)
     pc.Index(index_name).upsert(vectors=[{"id": id_val, "values": embedding}])

def get_relevant_chunks(query, k=3, use_qb_index=False):
    test_embedding = generate_embedding(query)
    if use_qb_index:
        idx_name = "prophet-equifax-qb"
    else:
        idx_name = "prophet-equifax"
    results = pc.Index(idx_name).query(
      vector=test_embedding,
      top_k=k 
    )

    return results

def get_top_unique_indices(values, top_n=3):
    # Sort the list based on the score value in descending order
    sorted_values = sorted(values, key=lambda x: x[1], reverse=True)

    # Dictionary to keep track of the unique values and their first index
    unique_indices = {}
    for index, (original_index, value) in enumerate(sorted_values):
        if value not in unique_indices:
            unique_indices[value] = original_index
        if len(unique_indices) == top_n:
            break

    # Get the first indices of the top N unique values
    top_indices = list(unique_indices.values())
    return top_indices

def process_query(system_message, query, pages=pages, use_qb_index=True, model=GPT35):
    relevant_data = get_relevant_chunks(query, use_qb_index=False)
    if use_qb_index:
        chunks = [(x['id'], x['score']) for x in relevant_data['matches']]
        relevant_qb_data = get_relevant_chunks(query, use_qb_index=True)
        chunks_qb = [(x['id'].split('_')[0], x['score']) for x in relevant_qb_data['matches']]
        chunks += chunks_qb
        chunks = get_top_unique_indices(chunks)
    else:
        chunks = [x['id'] for x in relevant_data['matches']]

    chunks = list(set(chunks)) # unique page numbers
    content = str([pages[c] for c in chunks])
    user_message = query + "\n here are the relevant text chunks:\n" + content
    answer = get_api_response(system_message, user_message, use_reminder_prompt=True, model=model)

    return chunks, answer

    def split_questions(input_list):
        questions = []
    
        for item in input_list:
            # Remove leading/trailing whitespace
            item = item.strip()
            
            # Check if the item has numbered questions
            if re.match(r'^\d+\.', item):
                # Split based on numbered pattern e.g., '1.', '2.', etc.
                split_items = re.split(r'\d+\.\s+', item)
                # Remove any empty strings resulting from the split
                split_items = [q for q in split_items if q.strip()]
                questions.extend(split_items)
            else:
                # Split non-numbered questions by newline followed by space or at least one space
                split_items = re.split(r'\n\s*|\s*\n\s*', item)
                split_items = [q.strip('"').strip() for q in split_items if q.strip()]
                questions.extend(split_items)
        
        # Final cleaning to ensure no leading/trailing whitespace
        questions = [q.strip() for q in questions if q.strip()]
        
        return questions
