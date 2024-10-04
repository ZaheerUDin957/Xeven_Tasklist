# Task1

# main.py
from fastapi import FastAPI, Query
from typing import Optional, List
from models import ProductQuery, Pagination

app = FastAPI()

# Sample product database (for demo purposes)
products = [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 1000, "rating": 4.5, "available": True},
    {"id": 2, "name": "Phone", "category": "electronics", "price": 600, "rating": 4.0, "available": False},
    {"id": 3, "name": "T-shirt", "category": "fashion", "price": 20, "rating": 3.8, "available": True},
    {"id": 4, "name": "Book", "category": "books", "price": 15, "rating": 4.9, "available": True},
    {"id": 5, "name": "Headphones", "category": "electronics", "price": 150, "rating": 4.3, "available": True},
]


@app.get("/products/")
async def filter_products(
    category: Optional[str] = Query(None, description="Category of the product"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    available: Optional[bool] = Query(None, description="Filter by availability (True or False)"),
    sort_by: Optional[str] = Query("price", description="Sort by 'price' or 'rating'"),
):
    """
    Filter products based on category, price range, and availability.
    Sort products based on price or rating.
    """
    filtered_products = products

    # Filter by category
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]

    # Filter by price range
    if price_min is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= price_min]
    if price_max is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= price_max]

    # Filter by availability
    if available is not None:
        filtered_products = [p for p in filtered_products if p["available"] == available]

    # Sort products by price or rating
    if sort_by == "price":
        filtered_products = sorted(filtered_products, key=lambda x: x["price"])
    elif sort_by == "rating":
        filtered_products = sorted(filtered_products, key=lambda x: x["rating"], reverse=True)

    return {"products": filtered_products}

# models.py


from fastapi import FastAPI, Query
from typing import Optional, List
from models import ProductQuery, Pagination

app = FastAPI()

# Sample product database (for demo purposes)
products = [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 1000, "rating": 4.5, "available": True},
    {"id": 2, "name": "Phone", "category": "electronics", "price": 600, "rating": 4.0, "available": False},
    {"id": 3, "name": "T-shirt", "category": "fashion", "price": 20, "rating": 3.8, "available": True},
    {"id": 4, "name": "Book", "category": "books", "price": 15, "rating": 4.9, "available": True},
    {"id": 5, "name": "Headphones", "category": "electronics", "price": 150, "rating": 4.3, "available": True},
]


@app.get("/products/")
async def filter_products(
    category: Optional[str] = Query(None, description="Category of the product"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    available: Optional[bool] = Query(None, description="Filter by availability (True or False)"),
    sort_by: Optional[str] = Query("price", description="Sort by 'price' or 'rating'"),
):
    """
    Filter products based on category, price range, and availability.
    Sort products based on price or rating.
    """
    filtered_products = products

    # Filter by category
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]

    # Filter by price range
    if price_min is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= price_min]
    if price_max is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= price_max]

    # Filter by availability
    if available is not None:
        filtered_products = [p for p in filtered_products if p["available"] == available]

    # Sort products by price or rating
    if sort_by == "price":
        filtered_products = sorted(filtered_products, key=lambda x: x["price"])
    elif sort_by == "rating":
        filtered_products = sorted(filtered_products, key=lambda x: x["rating"], reverse=True)

    return {"products": filtered_products}

# Task2

from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
import uvicorn

# initialize FastAPI app
app = FastAPI()

# create database connection
def get_db_connection():
    conn = psycopg2.connect(dbname = 'Db1', user = 'postgres', password='7887', host = 'localhost', port='5432')
    return conn

# initialize the database tables
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # SQL statement to create person table
    create_person_table = '''
    CREATE TABLE IF NOT EXISTS person(
    person_cnic INT NOT NULL PRIMARY KEY,
    person_name VARCHAR(100) NOT NULL
    )'''

    # SQL statement to create questions table 
    create_person_question_table = '''
    CREATE TABLE IF NOT EXISTS person_questions(
    question_id SERIAL PRIMARY KEY,
    person_cnic INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (person_cnic) REFERENCES person(person_cnic)
    )'''

    # Execute the SQL commands
    cur.execute(create_person_table)
    cur.execute(create_person_question_table)

    # commit changes to the database
    conn.commit()

    # close the cursor and connection
    cur.close()
    conn.close()


# Define pydantic models for request validation
class Person(BaseModel):
    person_cnic : int
    person_name : str

class PersonQuestions(BaseModel):
    person_cnic : int
    question : str
    answer : str

# API endpoint to add a new person
@app.post('/add_person')
async def add_person(person : Person):
    conn = get_db_connection()
    cur = conn.cursor()

    # inser person inTo the database
    cur.execute('INSERT INTO person(person_cnic, person_name) VALUES (%s, %s)', (person.person_cnic, person.person_name))

    conn.commit()
    cur.close()
    conn.close()

    return {'message' : 'person added successfully', 'person_cnic': person.person_cnic, 'person_name' : person.person_name}


from fastapi import HTTPException
import psycopg2  # Assuming you're using PostgreSQL

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

import random
@app.post('/add_question')
async def add_question(question: PersonQuestions):
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if the person exists in the person table
    cur.execute('SELECT * FROM person WHERE person_cnic = %s', (question.person_cnic,))
    person = cur.fetchone()  # Change "Person" to "person" to match the variable name

    if person is None:  # Check if person is None, not "Person"
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail='Person not found in the table')
    
    # Generate a random response for the question
    random_responses = [
        "That's interesting!",
        "I see what you mean.",
        "Can you tell me more?",
        "That's a great question!",
        "I'm not sure about that."
    ]
    random_answer = random.choice(random_responses)

    # Insert the question and random answer into the database
    cur.execute('INSERT INTO person_questions (person_cnic, question, answer) VALUES (%s, %s, %s)',  # Correct table name
                (question.person_cnic, question.question, random_answer))

    conn.commit()
    cur.close()
    conn.close()
    return {'message': 'Question and answer added successfully', 'question': question.question, 'answer': random_answer}



# initialize the database when the app starts
if __name__ == '__main__': 
    # init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
