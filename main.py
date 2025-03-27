# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.responses import JSONResponse

# Initialize the FastAPI app
app = FastAPI(
    title="User Management API",
    description="A simple API to manage users with CRUD operations.",
    version="1.0.0"
)

# In-memory storage for users (using a dictionary with id as the key)
users_db = {}

# Pydantic model for user data validation
class User(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier for the user (must be positive)")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the user")
    phone_no: str = Field(..., min_length=10, max_length=15, description="Phone number of the user")
    address: str = Field(..., min_length=1, max_length=200, description="Address of the user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "phone_no": "1234567890",
                "address": "123 Main St"
            }
        }

# Pydantic model for updating user (all fields are optional except id)
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated name of the user")
    phone_no: Optional[str] = Field(None, min_length=10, max_length=15, description="Updated phone number of the user")
    address: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated address of the user")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Updated",
                "phone_no": "9876543210",
                "address": "456 Updated St"
            }
        }

# 1. Create a new user (POST /users/)
@app.post("/users/", response_model=dict, status_code=201)
async def create_user(user: User):
    """
    Create a new user with the provided details.
    - id: Must be unique and positive.
    - Returns: 201 Created with a confirmation message on success.
    - Raises: 400 Bad Request if the user ID already exists.
    """
    if user.id in users_db:
        raise HTTPException(status_code=400, detail="User with this ID already exists")
    
    users_db[user.id] = user.dict()
    return {"message": "User created successfully"}

# 2. Read users by name (GET /users/search?name={name})
# Defined before /users/{id} to avoid routing conflicts
@app.get("/users/search", response_model=List[User], status_code=200)
async def search_users_by_name(name: str = Query(..., min_length=1, description="Name to search for")):
    """
    Search for users by their name (case-insensitive partial match).
    - name: Query parameter to search for users by name.
    - Returns: 200 OK with a list of matching users, or an empty list if none found.
    """
    matching_users = [
        user for user in users_db.values()
        if name.lower() in user["name"].lower()
    ]
    return matching_users

# 3. Read user by ID (GET /users/{id})
@app.get("/users/{id}", response_model=User, status_code=200)
async def get_user_by_id(id: int):
    """
    Retrieve a user by their ID.
    - id: The unique identifier of the user.
    - Returns: 200 OK with the user details if found.
    - Raises: 404 Not Found if the user is not found.
    """
    if id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[id]

# 4. Update user details (PUT /users/{id})
@app.put("/users/{id}", response_model=dict, status_code=200)
async def update_user(id: int, user_update: UserUpdate):
    """
    Update an existing user's details.
    - id: The unique identifier of the user to update.
    - user_update: Fields to update (name, phone_no, address).
    - Returns: 200 OK with a confirmation message on success.
    - Raises: 404 Not Found if the user is not found.
    """
    if id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only the fields that are provided
    updated_user = users_db[id]
    if user_update.name is not None:
        updated_user["name"] = user_update.name
    if user_update.phone_no is not None:
        updated_user["phone_no"] = user_update.phone_no
    if user_update.address is not None:
        updated_user["address"] = user_update.address
    
    users_db[id] = updated_user
    return {"message": "User updated successfully"}

# 5. Delete user by ID (DELETE /users/{id})
@app.delete("/users/{id}", response_model=dict, status_code=200)
async def delete_user(id: int):
    """
    Delete a user by their ID.
    - id: The unique identifier of the user to delete.
    - Returns: 200 OK with a confirmation message on success.
    - Raises: 404 Not Found if the user is not found.
    """
    if id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users_db[id]
    return {"message": "User deleted successfully"}

# Optional: Add a root endpoint for a welcome message
@app.get("/", status_code=200)
async def root():
    """
    Welcome message for the API.
    - Returns: 200 OK with a welcome message.
    """
    return {"message": "Welcome to the User Management API! Access the docs at /docs."}
