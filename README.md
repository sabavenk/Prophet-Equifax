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

## Folder Structure
- model_development/: Contains evaluation folder and notebook with R&D work. Please refer to this for a details on implementation and evaluation approaches. 
- createVectorDB.py: Main script to create and populate Pinecone indices.
- utils.py: Utility functions for embedding generation and Pinecone operations.
- .env: File to store environment variables (not included in the repository for security reasons).
- requirements.txt: List of required Python libraries.


## Design and Implementation

### Choice of Pinecone: 
- Well suited for demos due to its ease of setup and user-friendly interface. It supports rapid prototyping and scalability, which are essential for showcasing capabilities in a limited time.
- Tradeoffs: While Pinecone is excellent for demos, Qdrant might be a better choice for production environments, especially for a cybersecurity company dealing with sensitive logs data. Qdrant offers robust security 
features and on-premise deployment options, which are critical for handling sensitive data. For the sake of expedience and convenience, Pinecone was chosen. 
### Choice of Models:

- GPT-3.5-Turbo: Used as the default model due to its balance of performance and cost. It provides high-quality responses while being cost-effective for frequent API calls. Considered an open source model but considering familiarity of use and the fact that advanced prompting and RAG techniques tend to work better on larger parameter models, this was the sensible choice. 
- Evaluator Model (GPT-4o): Used for evaluations, this model is on par with GPT-4 but cheaper, making it a practical choice for benchmarking and evaluation without compromising on quality.

### Dataset:

- Subset of 10-K Filing: A 27-page subset of the Q1 2018 Equifax 10-K filing was used. This subset contained the necessary information for the chatbot and was manageable enough for manual labeling of questions and answers. The size was optimal for fitting into the context window of the model, ensuring comprehensive coverage of the document within the model's capabilities.
Implementation
Embeddings-Based Search
Embedding Generation:

The generate_embedding function in utils.py uses OpenAI's embedding API to convert text into vector embeddings.
### Vector Storage:

Pinecone is used to store these embeddings, enabling efficient similarity search. Two indices are created: prophet-equifax for page content and prophet-equifax-qb for question bank data (generated using gpt-3.5-turbo)

### Challenges Faced
- Data Preparation and Eval: Ensuring the dataset was both large enough for a RAG system to be required and small enough to be inspected manually was tricky. Parsing PDFs can also be a hassle and fortunately nearly all the data except for a chart was in text form. The preprocessing steps involved to clean and tokenize text data effectivel was minimal but creating the evaluation dataset took time and was no way to automate getting expert answers. 
- RAG Approaches: Noticed that the base RAG was peforming around 70% and struggled with recalling specific facts when indexed by page. Most of the errors were due to not retrieving the correct page or retriving it but missing the critical information due to 'lost-in-the-middle' problem where if answer is in the middle of a longer context then it's more likely to be missed in the end. The idea to mitigate these were to introduce a question bank to enhance the retrieval accuracy with a more direct apple-to-apple comparisons between queries and questions a page is capable of answering. The second approach was simply enhancing the system prompt with a role and more detailed task description along with a 'reminders' prompt at the end to mitigate 'lost-in-the-middle' effect. 

### Evaluations
The project includes an evaluations folder with three files, each representing different approaches for evaluating the question bank:

- Benchmark Approach: This file contains the initial benchmark approach for evaluating the question bank.
- Score: 71.25
- 
- AI-Generated Question Bank: This file includes evaluations with AI-generated questions.
- Score: 76.925
  
- Refined Prompts and Question Bank: This file contains evaluations with refined prompts and an improved question bank.
- Score: 78.25

Each approach was evaluated on the same set of questions compared to expert answers. The evaluations were conducted by me and vetted by my brother, a cybersecurity analyst who has worked with this data before for a report.

### Next Steps
To further improve the performance, the following approaches can be considered:

- Smaller Chunks: Mitigating the "lost in the middle" problem by breaking down the content into smaller, more manageable chunks.
- Graph RAG (Retrieval-Augmented Generation): Synthesizing larger contexts to handle and retrieve relevant information more effectively.

