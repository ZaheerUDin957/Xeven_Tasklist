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

