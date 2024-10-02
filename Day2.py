from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # Import BaseModel from Pydantic

app = FastAPI()

# Initial food items data
food_item = {
    'indian': ['Samose', 'Dosa', 'Paneer Butter Masala', 'Tandoori Chicken', 'Naan'],
    'pakistani': ['Biryani', 'Nihari', 'Halwa Puri', 'Kebabs', 'Karahi'],
    'chinese': ['Spring Rolls', 'Dim Sum', 'Sweet and Sour Chicken', 'Chow Mein', 'Fried Rice'],
    'italian': ['Pizza', 'Pasta', 'Lasagna', 'Risotto', 'Gelato'],
    'mexican': ['Tacos', 'Burritos', 'Quesadillas', 'Guacamole', 'Nachos'],
    'american': ['Burgers', 'Hot Dogs', 'Mac and Cheese', 'Buffalo Wings', 'Apple Pie']
}
valid_items = food_item.keys()

# Endpoint to get food items by category
@app.get('/get_food/{food_name}')
async def get_food(food_name: str):
    if food_name not in food_item:
        return {'message': f'Supported food items are {list(valid_items)}'}
    return {'food_items': food_item.get(food_name)}

# Coupon codes for discounts
coupon_code = {
    1: '10%',
    2: '20%',
    3: '30%',
    4: '40%'
}

# Endpoint to get coupon discount
@app.get('/get_coupon/{code}')
async def get_coupon(code: int):
    discount = coupon_code.get(code)
    if discount is None:
        return 'Invalid Coupon Code'
    return {'discount_amount': discount}

# Pydantic model for food items
class FoodItem(BaseModel):
    category: str
    item: str

# Endpoint to add a new food item
@app.post('/add_food')
async def add_food(food: FoodItem):
    if food.category not in valid_items:
        return 'valid food categories are {valid_items}'
    food_item[food.category].append(food.item)
    return {'message': f'Food item {food.item} added to {food.category}'}

# Endpoint to delete a food item
@app.delete('/delete_food')
async def delete_food(food: FoodItem):
    if food.category not in valid_items or food.item not in food_item[food.category]:
        return 'Food item not found'
    food_item[food.category].remove(food.item)
    return {'message': f'Food item {food.item} removed from {food.category}'}

# Endpoint to update a food item
class UpdateFoodItem(BaseModel):
    category: str
    item: str
    new_item: str  # New item name to replace the old one

@app.put('/update_food')
async def update_food(food: UpdateFoodItem):
    if food.category not in valid_items or food.item not in food_item[food.category]:
        return 'Food item not found'

    # Update food item
    food_item[food.category].remove(food.item)
    food_item[food.category].append(food.new_item)  # Replace with the new item name
    return {'message': f'Food item {food.item} updated to {food.new_item} in {food.category}'}
