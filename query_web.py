import ollama
import chromadb
import web_crawler
import json
import requests
import sys
from bs4 import BeautifulSoup

# Initialize database client and collection
CLIENT = chromadb.Client()
COLLECTION = CLIENT.create_collection(name="docs")

# Constants
EMBEDDINGS_MODEL = "nomic-embed-text"  # Model for generating embeddings
MODEL = "llama3.2"  # Language model to query
N_RESULTS = 5  # Number of search results to include
VERBOSE = False  # Enable verbose output for debugging

def create_embedding(text):
    """
    Generate an embedding for a given text using the specified model.

    Args:
        text (str): The text to embed.

    Returns:
        list: The embedding vector for the input text.
    """
    response = ollama.embeddings(model=EMBEDDINGS_MODEL, prompt=text)
    return response["embedding"]

def store_embeddings(ids, embeddings, documents):
    """
    Store embeddings in the ChromaDB collection.

    Args:
        ids (list): List of unique IDs for the documents.
        embeddings (list): List of embedding vectors.
        documents (list): List of corresponding documents.
    """
    COLLECTION.add(ids=ids, embeddings=embeddings, documents=documents)

def embed_pages(pages):
    """
    Embed a list of web pages and store them in the database.

    Args:
        pages (list): List of dictionaries with "document" and "uri" keys.
    """
    for page in pages:
        output_verbose(f"Processing page:\n{page}")
        embedding = create_embedding(page["document"])
        store_embeddings(
            ids=[page["uri"]],
            embeddings=[embedding],
            documents=[page["document"]],
        )

def query_embedding(embedding, n_results=N_RESULTS):
    """
    Query the database for the most relevant documents to a given embedding.

    Args:
        embedding (list): The embedding vector to query.
        n_results (int): The number of top results to retrieve.

    Returns:
        dict: Query results containing relevant document IDs and metadata.
    """
    results = COLLECTION.query(query_embeddings=embedding, n_results=n_results)
    return results

def output_verbose(text):
    """
    Print debug output if verbose mode is enabled.

    Args:
        text (str): The text to print.
    """
    if VERBOSE:
        print(f"\n{text}\n")

if __name__ == "__main__":
    # Retrieve the search query from command-line arguments or prompt the user
    if len(sys.argv) < 2:
        question = input("Enter search query: ")
    else:
        question = sys.argv[1]

    # Get search results from the query
    search_results = web_crawler.query_search_engine(question)

    # Embed the search results and store them in the database
    embed_pages(search_results)

    # Generate an embedding for the query prompt and retrieve relevant pages
    prompt_embedding = create_embedding(question)
    relevant_pages = query_embedding(prompt_embedding, n_results=N_RESULTS)
    output_verbose(relevant_pages)

    # Fetch the web pages' text content and create a structured data variable
    web_data = []
    for url in relevant_pages["ids"][0]:
        web_data.append(web_crawler.get_webpage_text(url))
    web_data_json = json.dumps(web_data)
    output_verbose(web_data_json)

    # Construct the prompt for the language model
    prompt = (
        f"You are an objective research assistant who gives concise, authoritative answers to questions. "
        f"You will be given a question and a piece of structured data. For each variable called 'text', decide if "
        f"the value answers the question and then use the information to construct your answer to the question. "
        f"If any part of the text is irrelevant to the question, then ignore it. If any part of the text seems like "
        f"a web page error, ignore it. Answer the question only. Do not give explanations or descriptions about the information. "
        f"Generate numbered citations within your answer using the 'url' variable and list the references. Be sure to cite all "
        f"statements in your answer. The question is: {question}. The data structure is: {web_data_json}"
    )

    # Query the language model and print the answer
    print("\nQuerying Ollama...")
    answer = ollama.generate(model=MODEL, prompt=prompt, stream=False)

    print("\nANSWER\n=================\n")
    print(answer["response"])
