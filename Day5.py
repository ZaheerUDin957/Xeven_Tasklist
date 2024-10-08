# 1. File uploading using fastAPI
# Function to extract text from a plain text file
def get_text_file_text(file):
    return file.read().decode('utf-8')  # Decode to convert bytes to string

# Endpoint for uploading and processing a single file
@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    index = len(extracted_texts) + 1  # Generate a new index for the file

    # Check the file type and extract text accordingly
    if file.content_type == "application/pdf":
        text = get_pdf_text(file.file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = get_docx_text(file.file)
    elif file.content_type == "text/plain":
        text = get_text_file_text(file.file)
    else:
        return JSONResponse(status_code=400, content={"error": f"Invalid file type for {file.filename}. Please upload a PDF, DOCX, or plain text document."})

    # Store extracted text with file index in temporary storage
    extracted_texts[file.filename] = {
        "text": text,
        "file_index": index  # Store the file index in the metadata
    }

    # Return success message and current file index
    return {"message": f"File '{file.filename}' processed and saved.", "file_index": index}

# 2. QA using any LLM
import os 
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
import psycopg2
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

app = FastAPI()

def get_db_connection():
    conn = psycopg2.connect(dbname='Db1',user="postgres",password='7887',host="localhost",port=5432)
    return conn

conn = get_db_connection()

class Person(BaseModel):
    person_cnic : int
    person_name : str

class PersonQuestions(BaseModel):
    person_cnic : int
    question : str

# API endpoint to add a new person
@app.post('/add_person')
async def add_person(person: Person):
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if the person already exists in the database
    cur.execute('SELECT * FROM person WHERE person_cnic = %s', (person.person_cnic,))
    existing_person = cur.fetchone()

    if existing_person:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail='Person already exists')

    # Insert person into the database
    cur.execute('INSERT INTO person(person_cnic, person_name) VALUES (%s, %s)', (person.person_cnic, person.person_name))

    conn.commit()
    cur.close()
    conn.close()

    return {'message': 'Person added successfully', 'person_cnic': person.person_cnic, 'person_name': person.person_name}

@app.delete('/delete_person/{person_cnic}')
async def delete_person(person_cnic: int):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if the person exists in the person table
        cur.execute('SELECT * FROM person WHERE person_cnic = %s', (person_cnic,))
        person = cur.fetchone()

        if not person:
            # Person does not exist, raise a 404 HTTPException
            raise HTTPException(status_code=404, detail=f'Person with CNIC {person_cnic} not found in the table')

        # Person exists, proceed to delete
        cur.execute('DELETE FROM person WHERE person_cnic = %s', (person_cnic,))

        # Commit the transaction
        conn.commit()

        return {'message': 'Person deleted successfully', 'person_cnic': person_cnic}
    
    except psycopg2.Error as db_error:
        # Catch any database-specific errors
        conn.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    
    finally:
        cur.close()
        conn.close()

# API endpoint to fetch person information along with their questions and answers
@app.get('/get_person_info/{person_cnic}')
async def get_person_info(person_cnic: int):
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch person information
    cur.execute('SELECT * FROM person WHERE person_cnic = %s', (person_cnic,))
    person = cur.fetchone()

    if person is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail='Person not found in the table')

    # Fetch associated questions and answers
    cur.execute('SELECT question_id, question, answer FROM person_questions WHERE person_cnic = %s', (person_cnic,))
    questions = cur.fetchall()  # Change variable name from 'question' to 'questions'

    # Check if there are no questions associated with the person
    if not questions:
        cur.close()
        conn.close()
        return {
            'message': 'Person found but no associated questions or answers exist.',
            'person_info': {
                'person_cnic': person[0],
                'person_name': person[1],
                'questions': []
            }
        }
    
    # Format person data with questions
    person_info = {
        'person_cnic': person[0],
        'person_name': person[1],
        'questions': [{'question_id': q[0], 'question': q[1], 'answer': q[2]} for q in questions]
    }
    
    cur.close()
    conn.close()
    
    return {'person_info': person_info}

@app.post('/add_question_and_answer')
async def add_question_and_answer(question: PersonQuestions):
    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # Check if the person exists in the person table
        cur.execute('SELECT * FROM person WHERE person_cnic = %s', (question.person_cnic,))
        person = cur.fetchone()  # Fetch the person record

        if person is None:
            raise HTTPException(status_code=404, detail='Person not found in the table')
        
        # Generate an answer using the LLm
        answer = generate_answer(question.question)
        # Strip any newline characters from the answer
        answer = answer.replace('\n', ' ').strip()

        #Insert the question and generated answer into the database
        cur.execute('INSERT INTO person_questions (person_cnic, question, answer) VALUES (%s, %s, %s)', 
                    (question.person_cnic, question.question, answer))
        
        conn.commit()

        return {
            'message': 'Question and answer added successfully',
            'person_cnic': question.person_cnic,
            'question': question.question,
            'answer': answer
        }

    except Exception as e:
        # Handle any exceptions that occur during the operations
        raise HTTPException(status_code=500, detail=f'Internal Server Error: {str(e)}')
        

def generate_answer(prompt: str) -> str:
    # initialize the model with the API Key
    llm = GoogleGenerativeAI(model='gemini-1.5-flash')
    response = llm.invoke(prompt)
    return response

# initialize the database when the app starts
if __name__ == '__main__': 
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


# 3. QA from the uploaded file (RAG system)(vectors, Weaviate)
import weaviate
import weaviate.client as wvc
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import PyPDF2
import docx
import uvicorn
from langchain.embeddings import HuggingFaceEmbeddings

app = FastAPI()

# Temporary storage for extracted text and metadata
extracted_texts = {}

# Initialize the embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Function to extract text from a PDF file
def get_pdf_text(pdf):
    pdf_reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:  # Ensure we don't append None if the page has no text
            text += page_text + "\n"
    return text

# Function to extract text from a DOCX file
def get_docx_text(file):
    doc = docx.Document(file)
    allText = []
    for docpara in doc.paragraphs:
        allText.append(docpara.text)
    text = ' '.join(allText)
    return text

# Function to extract text from a plain text file
def get_text_file_text(file):
    return file.read().decode('utf-8')  # Decode to convert bytes to string

# Endpoint for uploading and processing a single file
@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    index = len(extracted_texts) + 1  # Generate a new index for the file

    # Check the file type and extract text accordingly
    if file.content_type == "application/pdf":
        text = get_pdf_text(file.file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = get_docx_text(file.file)
    elif file.content_type == "text/plain":
        text = get_text_file_text(file.file)
    else:
        return JSONResponse(status_code=400, content={"error": f"Invalid file type for {file.filename}. Please upload a PDF, DOCX, or plain text document."})

    # Store extracted text with file index in temporary storage
    extracted_texts[file.filename] = {
        "text": text,
        "file_index": index  # Store the file index in the metadata
    }

    # Return success message and current file index
    return {"message": f"File '{file.filename}' processed and saved.", "file_index": index}

# Endpoint to retrieve text for all uploaded files
@app.get("/all-text/")
async def get_all_text():
    if not extracted_texts:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")
    
    all_text_data = []
    
    # Iterate over all the files in storage and return their texts
    for filename, file_data in extracted_texts.items():
        text = file_data["text"]
        file_index = file_data["file_index"]
        all_text_data.append({
            "filename": filename,
            "file_index": file_index,
            "text": text
        })
    
    # Return all texts and metadata
    return {"all_files": all_text_data}

# Function to split text into chunks with metadata
def get_text_chunks(text, filename, file_index, chunk_size=2000):
    chunks = []
    text_length = len(text)
    
    # Split text into chunks of specified size
    for i in range(0, text_length, chunk_size):
        chunk = text[i:i + chunk_size]
        metadata = {
            "filename": filename,
            "file_index": file_index,
            "chunk_number": (i // chunk_size) + 1
        }
        chunks.append({
            "page_content": chunk,
            "metadata": metadata
        })
    return chunks

# Endpoint to retrieve text chunks for all uploaded files, including metadata
@app.get("/text-chunks/")
async def get_text_chunks_for_all_files():
    if not extracted_texts:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")

    all_chunks_data = []

    # Iterate over all the files in storage
    for filename, file_data in extracted_texts.items():
        text = file_data["text"]
        file_index = file_data["file_index"]

        # Get text chunks for the current file
        chunks = get_text_chunks(text, filename, file_index)

        # Append chunks and metadata for this file to the final result
        all_chunks_data.append({
            "filename": filename,
            "file_index": file_index,
            "chunks": [{"content": chunk["page_content"], "metadata": chunk["metadata"]} for chunk in chunks]
        })

    # Return all text chunks and metadata for all files
    return {"all_files_chunks": all_chunks_data}

# Function to generate vector embeddings for the text
def get_text_embeddings(text):
    return embeddings.embed_documents([text])

# Endpoint to retrieve vector embeddings for all uploaded files
@app.get("/text-embeddings/")
async def get_embeddings_for_all_files():
    if not extracted_texts:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")
    
    all_embeddings_data = []

    # Iterate over all files and generate embeddings for each
    for filename, file_data in extracted_texts.items():
        text = file_data["text"]
        file_index = file_data["file_index"]
        
        # Generate embeddings for the current file's text
        vector_embeddings = get_text_embeddings(text)
        
        # Append embeddings and metadata for this file to the result
        all_embeddings_data.append({
            "filename": filename,
            "file_index": file_index,
            "embeddings": vector_embeddings
        })

    # Return the vector embeddings for all files
    return {"all_files_embeddings": all_embeddings_data}

import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate_client as wvc  # Ensure you import the necessary module for authentication

# Define your connection parameters
WEAVIATE_CLUSTER = "https://grpc-gtsciyecsluwcmaacparba.c0.us-west3.gcp.weaviate.cloud"
WEAVIATE_API_KEY = "CU9BCJ0LFPjooAfcK6JeojXU7Zh6LDs5Tb11"  # Replace with your actual Weaviate API key
OPENAI_API_KEY = ""  # Replace with your actual OpenAI API key

def connect_vector_db(use_cloud=True):
    """
    Connects to Weaviate vector database (either local or cloud).
    
    Args:
        use_cloud (bool): If True, connects to Weaviate cloud; otherwise connects to local Weaviate.

    Returns:
        Weaviate client object.
    """
    if use_cloud:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_CLUSTER,                                    # Replace with your Weaviate Cloud URL
            auth_credentials=wvc.init.Auth.api_key(WEAVIATE_API_KEY),    # Replace with your Weaviate Cloud key
            headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}                  # Optional: Add header for OpenAI API key
        )
        print("Connected to Weaviate Cloud.")
    else:
        client = weaviate.connect_to_local()
        print("Connected to local Weaviate instance.")
    
    return client
db = WeaviateVectorStore.from_documents(all_chunks_data, all_embeddings_data, client=weaviate_client)
# Example usage:
weaviate_client = connect_vector_db(use_cloud=True)  # Connect to Weaviate Cloud
# or
# weaviate_client = connect_vector_db(use_cloud=False)  # Connect to local Weaviate


docsearch = WeaviateVectorStore.from_documents(
    texts,
    embeddings,
    client=client_ar,
)
t = docsearch.as_retriever()
t.invoke("Suggest me three down payment programs or schemes")

# initialize the database when the app starts
if __name__ == '__main__': 
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

