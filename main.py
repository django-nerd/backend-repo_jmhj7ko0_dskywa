import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Plant

app = FastAPI(title="Houseplant Comparison API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Houseplant Comparison Backend is running"}

# Public schema endpoint so the UI/DB viewer can introspect
@app.get("/schema")
def get_schema():
    return {
        "plant": Plant.model_json_schema(),
    }

class PlantQuery(BaseModel):
    q: Optional[str] = None
    light: Optional[str] = None
    water: Optional[str] = None
    care_level: Optional[str] = None
    pet_friendly: Optional[bool] = None
    size: Optional[str] = None
    tags: Optional[List[str]] = None

@app.get("/plants")
def list_plants(
    q: Optional[str] = None,
    light: Optional[str] = None,
    water: Optional[str] = None,
    care_level: Optional[str] = None,
    pet_friendly: Optional[bool] = None,
    size: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
):
    """List plants with optional filters and search."""
    if db is None:
        # Still allow demo by returning curated seed data if DB not configured
        return _seed_plants()[:limit]

    filt = {}
    if q:
        filt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"scientific_name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    if light:
        filt["light"] = light
    if water:
        filt["water"] = water
    if care_level:
        filt["care_level"] = care_level
    if pet_friendly is not None:
        filt["pet_friendly"] = pet_friendly
    if size:
        filt["size"] = size
    if tag:
        filt["tags"] = {"$in": [tag]}

    docs = get_documents("plant", filt, limit)
    # Convert ObjectId and datetimes to strings
    for d in docs:
        d["_id"] = str(d.get("_id"))
        if d.get("created_at"): d["created_at"] = str(d["created_at"]) 
        if d.get("updated_at"): d["updated_at"] = str(d["updated_at"]) 
    return docs

@app.post("/plants")
def create_plant(plant: Plant):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    plant_id = create_document("plant", plant)
    return {"id": plant_id}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Seed data for demo/preview when DB is not configured

def _seed_plants():
    return [
        {
            "name": "Monstera Deliciosa",
            "scientific_name": "Monstera deliciosa",
            "description": "Iconic split leaves, fast grower and forgiving.",
            "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop",
            "light": "bright",
            "water": "moderate",
            "care_level": "easy",
            "pet_friendly": False,
            "size": "large",
            "tags": ["statement", "fast-growing"]
        },
        {
            "name": "Snake Plant",
            "scientific_name": "Sansevieria trifasciata",
            "description": "Thrives on neglect, great for low light.",
            "image_url": "https://images.unsplash.com/photo-1587300003388-59208cc962cb?q=80&w=1200&auto=format&fit=crop",
            "light": "low",
            "water": "low",
            "care_level": "easy",
            "pet_friendly": False,
            "size": "medium",
            "tags": ["air-purifier", "beginner"]
        },
        {
            "name": "ZZ Plant",
            "scientific_name": "Zamioculcas zamiifolia",
            "description": "Glossy leaves, tolerates low light and infrequent watering.",
            "image_url": "https://images.unsplash.com/photo-1620916566398-579615a6df65?q=80&w=1200&auto=format&fit=crop",
            "light": "low",
            "water": "low",
            "care_level": "easy",
            "pet_friendly": False,
            "size": "medium",
            "tags": ["hardy", "office"]
        },
        {
            "name": "Pothos",
            "scientific_name": "Epipremnum aureum",
            "description": "Vining plant that adapts to many conditions.",
            "image_url": "https://images.unsplash.com/photo-1601482256584-5f934a95a204?q=80&w=1200&auto=format&fit=crop",
            "light": "medium",
            "water": "moderate",
            "care_level": "easy",
            "pet_friendly": False,
            "size": "medium",
            "tags": ["trailing", "versatile"]
        },
        {
            "name": "Parlor Palm",
            "scientific_name": "Chamaedorea elegans",
            "description": "Pet-friendly palm that tolerates low light.",
            "image_url": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=1200&auto=format&fit=crop",
            "light": "low",
            "water": "moderate",
            "care_level": "moderate",
            "pet_friendly": True,
            "size": "medium",
            "tags": ["pet-safe", "palm"]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
