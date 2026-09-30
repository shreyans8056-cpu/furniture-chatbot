import re
import random

CATALOGUE = [
    {"furniture": "sofa",         "category": "seating", "material": "leather",        "price": 45000, "room": "living room", "available": True,  "delivery_days": 7},
    {"furniture": "sofa",         "category": "seating", "material": "fabric",         "price": 25000, "room": "living room", "available": True,  "delivery_days": 5},
    {"furniture": "bed",          "category": "sleeping","material": "wood",           "price": 30000, "room": "bedroom",     "available": True,  "delivery_days": 10},
    {"furniture": "bed",          "category": "sleeping","material": "engineered wood","price": 18000, "room": "bedroom",     "available": False, "delivery_days": 14},
    {"furniture": "dining table", "category": "dining",  "material": "wood",           "price": 35000, "room": "dining room", "available": True,  "delivery_days": 12},
    {"furniture": "dining table", "category": "dining",  "material": "glass",          "price": 22000, "room": "dining room", "available": True,  "delivery_days": 8},
    {"furniture": "wardrobe",     "category": "storage",  "material": "wood",           "price": 28000, "room": "bedroom",     "available": True,  "delivery_days": 15},
    {"furniture": "bookshelf",    "category": "storage",  "material": "metal",          "price": 8000,  "room": "office",      "available": True,  "delivery_days": 4},
    {"furniture": "office desk",  "category": "study",    "material": "wood",           "price": 12000, "room": "office",      "available": True,  "delivery_days": 6},
    {"furniture": "coffee table", "category": "seating",  "material": "glass",          "price": 6000,  "room": "living room", "available": True,  "delivery_days": 3},
    {"furniture": "recliner",     "category": "seating",  "material": "leather",        "price": 32000, "room": "living room", "available": False, "delivery_days": 20},
    {"furniture": "tv unit",      "category": "storage",  "material": "engineered wood","price": 9000,  "room": "living room", "available": True,  "delivery_days": 5},
]

# Vocabulary used for entity extraction (ENTITY LOOKUP TABLES)
FURNITURE_ITEMS = sorted(set(item["furniture"] for item in CATALOGUE))
MATERIALS       = sorted(set(item["material"]  for item in CATALOGUE))
ROOMS           = sorted(set(item["room"]      for item in CATALOGUE))
CATEGORIES      = sorted(set(item["category"]  for item in CATALOGUE))

MATERIAL_SYNONYMS = {
    "wood":  ["wood", "wooden"],
    "metal": ["metal", "metallic"],
}

# --- add these prints so you actually SEE output in this cell ---
print("Catalogue loaded:", len(CATALOGUE), "items")
print("Furniture types :", FURNITURE_ITEMS)
print("Materials       :", MATERIALS)
print("Rooms           :", ROOMS)
print("Categories      :", CATEGORIES)
