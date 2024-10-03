# Task 1
import psycopg2

conn = psycopg2.connect(
    dbname='Db1',
    user="postgres",
    password='7887',
    host="localhost",
    port=5432
)

cur = conn.cursor()

def create_company(company_name , email):
    cur.execute(
        """
insert into companies (company_name, email)
values(%s, %s) returning CR_number
""", (company_name, email)
    )
    new_company_id = cur.fetchone()[0]
    conn.commit()
    return new_company_id

def get_company(cr_number):
    cur.execute('select * from companies where CR_number = %s', (cr_number,))
    company = cur.fetchone()
    return company

def update_company(cr_number, new_name, new_email):
    cur.execute(
        '''
update companies
set company_name = %s, email = %s
where CR_number = %s
''', (new_name, new_email, cr_number)
    )
    conn.commit()
    return cur.rowcount

def delete_company(cr_number):
    cur.execute('Delete from companies where cr_number = %s',(cr_number,))
    conn.commit()
    return cur.rowcount
    

# new_company_id = create_company('xyz', 'info@xyz.com')
# print(f'New company added with CR_number : {new_company_id}')

# company_details = get_company(6)
# print(f'company details: {company_details}')

# row_updated = update_company(6, 'Technistani', 'info@technistani.com')
# print(f'rows updated : {row_updated}')

row_deleted = delete_company(6)
print(f'row deleted : {row_deleted}')

cur.close()
conn.close()


# Task 2
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2 import sql

app = FastAPI()

def get_db_conn():
    conn = psycopg2.connect(
        dbname = 'Db1',
        user = 'postgres',
        password = '7887',
        host = 'localhost',
        port = 5432
    )
    return conn

class company(BaseModel):
    company_name : str
    email : str
conn = get_db_conn()
cur = conn.cursor()

@app.post('/companies/')
def create_company(company: company):
    cur.execute('''
insert into companies (company_name, email)
                values (%s, %s) returning cr_number
                ''',(company.company_name, company.email))
    new_company_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {'CR_number': new_company_id}

@app.get('/companies/{cr_number}')
def get_company(cr_number: int):
    conn = get_db_conn()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM companies WHERE cr_number = %s', (cr_number,))
    company = cur.fetchone()
    cur.close()
    conn.close()
    
    if company is None:
        # Raise a 404 error if no company is found with the given CR_number
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        'CR_number': company[0], 
        'company_name': company[1], 
        'email': company[2]
    }

from fastapi import HTTPException

@app.put('/companies/{cr_number}')
def update_company(cr_number: int, company: company):
    conn = get_db_conn()  # Create a new database connection
    cur = conn.cursor()
    
    # Check if the company exists
    cur.execute('SELECT * FROM companies WHERE cr_number = %s', (cr_number,))
    existing_company = cur.fetchone()
    
    if existing_company is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")

    # Proceed to update the company if it exists
    cur.execute('''
                UPDATE companies
                SET company_name = %s, email = %s
                WHERE cr_number = %s
                ''', (company.company_name, company.email, cr_number))
    
    conn.commit()  # Commit the transaction
    cur.close()  # Close the cursor
    conn.close()  # Close the connection
    
    return {'message': f'Company with CR_number {cr_number} updated successfully'}

@app.delete('/companies/{cr_number}')
def delete_company(cr_number: int):
    cur.execute('Delete from companies where CR_number = %s', (cr_number,))
    conn.commit()
    return {'message': f'Company with CR_number : {cr_number} deleted'}



# Task4

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
