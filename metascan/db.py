from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os

# MongoDB connection URL (local)
MONGO_URI = "mongodb://localhost:27017/"

# Database name
DB_NAME = "metascan_db"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collection
papers_col = db["papers"]

def add_paper(data: dict):
    """
    Insert one research paper document into MongoDB.
    Automatically adds created_at timestamp.
    """
    data["created_at"] = datetime.utcnow().isoformat()
    result = papers_col.insert_one(data)
    return str(result.inserted_id)

def get_paper(paper_id: str):
    """
    Fetch a single paper using its ObjectId.
    """
    try:
        return papers_col.find_one({"_id": ObjectId(paper_id)})
    except:
        return None

def search_papers(query: str):
    """
    Basic text search using regex across title, abstract, and keywords.
    """
    return list(papers_col.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"abstract": {"$regex": query, "$options": "i"}},
            {"keywords": {"$regex": query, "$options": "i"}}
        ]
    }))

def get_all_papers():
    """
    Return all documents from the collection.
    """
    return list(papers_col.find())

def delete_paper(paper_id: str) -> bool:
    """
    Delete paper from DB and remove PDF file if exists.
    """
    paper = papers_col.find_one({"_id": ObjectId(paper_id)})
    if not paper:
        return False

    # Delete PDF file
    file_path = paper.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print("Failed to delete PDF:", e)

    # Delete DB record
    papers_col.delete_one({"_id": ObjectId(paper_id)})
    return True

# ... (Keep your existing imports and paper functions) ...

# NEW: Users Collection
users_col = db["users"]

def create_user(username, password):
    """Registers a new user. Returns True if successful, False if username exists."""
    if users_col.find_one({"username": username}):
        return False
    users_col.insert_one({
        "username": username,
        "password": password,  # In a real app, hash this!
        "role": "user",
        "created_at": datetime.utcnow()
    })
    return True

def verify_user(username, password):
    """Checks credentials. Returns user dict or None."""
    return users_col.find_one({"username": username, "password": password})

def get_papers_by_user(username):
    """Fetches papers uploaded by a specific user."""
    return list(papers_col.find({"uploaded_by": username}))