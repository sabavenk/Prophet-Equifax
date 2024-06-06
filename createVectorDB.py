import os
import json
from utils import generate_embedding, split_questions, pages, pc


def create_pc_index(index_name):
    pc.create_index(
    name=index_name,
    dimension=256,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-west-2"
        )
    )

def process_and_upsert_pages(index_name, pages):
    for page_num, text in pages.items():
        embedding = generate_embedding(text)
        pc.Index("prophet-equifax").upsert(vectors=[{"id": page_num, "values": embedding}])

def process_and_upsert_questions(index_name, qb):
    for p_num in qb:
        if len(qb[p_num]) == 1:
            curr_q_list = split_questions(qb[p_num])
        else:
            curr_q_list = qb[p_num]
            for i in range(len(curr_q_list)):
                embedding = generate_embedding(curr_q_list[i])
                pc.Index(index_name).upsert(vectors=[{"id": f"{p_num}_{i}", "values": embedding}])

def main():
    # Load environment variables
    load_env_file('.env')

    # Create indices
    create_pc_index("prophet-equifax")
    create_pc_index("prophet-equifax-qb")

    # Load question bank data
    with open('gpt_generated_question_bank.json', 'r') as file:
        qb = json.load(file)

    # Process and upsert data
    process_and_upsert_pages("prophet-equifax", pages)
    process_and_upsert_questions("prophet-equifax-qb", qb)

if __name__ == "__main__":
    main()
