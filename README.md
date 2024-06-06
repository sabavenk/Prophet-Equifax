# Equifax Prophet Project

This repository contains a Python project to create and populate Pinecone indices with OpenAI embeddings for Equifax data. The project includes scripts for setting up the environment, processing data, and evaluating different approaches for generating and refining question banks.

## Setup Instructions

### 1. Install Required Libraries

Ensure you have Python installed on your system. Install the required libraries using `pip`:

```sh
pip install -r requirements.txt
```
### 2. Set Up Environment Variables

Create a .env file in the root directory of the project with your OpenAI and Pinecone API keys:

```makefile
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```
### 3. Run the Vector DB Script

To populate the Pinecone vector database with the provided files, run the main script:

```sh
python createVectorDB.py
```

This script will:

Create two indices: prophet-equifax and prophet-equifax-qb.
Process and upsert page content and question bank data into the respective indices.

### 4. Streamlit App

To launch the Q/A chatbot interface using Streamlit, run the following command:

```sh
streamlit run app.py
```
This will start the Streamlit server and open the app in your default web browser. You can then interact with the chatbot interface to ask questions about security operations and get detailed responses.

### Folder Structure
- model_development/: Contains evaluation folder and notebook with R&D work. Please refer to this for a details on implementation and evaluation approaches. 
- createVectorDB.py: Main script to create and populate Pinecone indices.
- utils.py: Utility functions for embedding generation and Pinecone operations.
- .env: File to store environment variables (not included in the repository for security reasons).
- requirements.txt: List of required Python libraries.


### Design and Implementation
Evaluation Approaches
The project includes an evaluations folder with three files, each representing different approaches for evaluating the question bank:

- Benchmark Approach: This file contains the initial benchmark approach for evaluating the question bank.
- AI-Generated Question Bank: This file includes evaluations with AI-generated questions.
- Refined Prompts and Question Bank: This file contains evaluations with refined prompts and an improved question bank.

Each approach was evaluated on the same set of questions compared to expert answers. The scores (0-100) were as follows:

- Benchmark Approach: 71.25
- AI-Generated Question Bank: 76.925
- Refined Prompts and Question Bank: 78.25

The evaluations were conducted by me and vetted by my brother, a cybersecurity analyst who has worked with this data before for a report.

### Next Steps
To further improve the performance, the following approaches can be considered:

- Smaller Chunks: This approach aims to mitigate the "lost in the middle" problem by breaking down the content into smaller, more manageable chunks.
- Graph RAG (Retrieval-Augmented Generation): This approach aims to synthesize larger contexts, making it easier to handle and retrieve relevant information.

