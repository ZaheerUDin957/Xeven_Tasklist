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


# 3. QA from the uploaded file (RAG system)(vectors, Qdrant)
# 
