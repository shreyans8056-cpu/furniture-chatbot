import re
import random
import streamlit as st
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

# ==============================
# FURNITURE CHATBOT
# ==============================

st.set_page_config(
    page_title="Furniture Chatbot",
    page_icon="🛋️",
    layout="centered"
)

st.title("🛋️ Furniture Chatbot")
st.write("Ask me about furniture, prices, materials, rooms, availability and delivery.")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def find_furniture(user_input):
    text = user_input.lower()

    matches = []

    # Detect furniture type
    for item in CATALOGUE:
        furniture = item["furniture"].lower()

        if furniture in text:
            matches.append(item)

    # Detect room
    for room in ROOMS:
        if room.lower() in text:
            room_matches = [
                item for item in CATALOGUE
                if item["room"].lower() == room.lower()
            ]

            if matches:
                matches = [
                    item for item in matches
                    if item["room"].lower() == room.lower()
                ]
            else:
                matches = room_matches

    # Detect material
    for material, synonyms in MATERIAL_SYNONYMS.items():
        if any(word in text for word in synonyms):
            material_matches = [
                item for item in CATALOGUE
                if item["material"].lower() == material.lower()
            ]

            if matches:
                matches = [
                    item for item in matches
                    if item["material"].lower() == material.lower()
                ]
            else:
                matches = material_matches

    # Detect budget
    numbers = re.findall(r"\d+(?:,\d+)*", text)

    if numbers:
        budget = max(int(n.replace(",", "")) for n in numbers)

        budget_matches = [
            item for item in CATALOGUE
            if item["price"] <= budget
        ]

        if matches:
            matches = [
                item for item in matches
                if item["price"] <= budget
            ]
        else:
            matches = budget_matches

    return matches


def chatbot_response(user_input):

    text = user_input.lower()

    # Greeting
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hello! 👋 I can help you find furniture based on price, room, material and availability."

    # Help
    if "help" in text:
        return (
            "You can ask things like:\n\n"
            "• Show me sofas\n"
            "• Show me wooden furniture\n"
            "• Furniture for bedroom\n"
            "• Dining table under 30000\n"
            "• Show available furniture\n"
            "• Show me furniture for living room"
        )

    # Availability request
    if "available" in text or "availability" in text:
        available = [
            item for item in CATALOGUE
            if item["available"]
        ]

        if available:
            response = "Here are the currently available items:\n\n"

            for item in available:
                response += (
                    f"🛋️ **{item['furniture'].title()}**\n"
                    f"💰 ₹{item['price']:,}\n"
                    f"🪵 Material: {item['material']}\n"
                    f"🏠 Room: {item['room']}\n\n"
                )

            return response

    # Search catalogue
    matches = find_furniture(user_input)

    if matches:
        response = f"I found {len(matches)} matching item(s):\n\n"

        for item in matches:
            availability = (
                "Available ✅"
                if item["available"]
                else "Currently unavailable ❌"
            )

            response += (
                f"### 🛋️ {item['furniture'].title()}\n"
                f"💰 **₹{item['price']:,}**\n"
                f"🪵 Material: {item['material']}\n"
                f"🏠 Room: {item['room']}\n"
                f"📦 {availability}\n"
                f"🚚 Delivery: {item['delivery_days']} days\n\n"
            )

        return response

    return (
        "Sorry, I couldn't find a matching furniture item. 😕\n\n"
        "Try asking something like:\n"
        "• Show me sofas\n"
        "• Wooden furniture under 30000\n"
        "• Furniture for bedroom\n"
        "• Dining table"
    )


# Chat input
user_input = st.chat_input("Ask me about furniture...")

if user_input:

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate response
    response = chatbot_response(user_input)

    # Display bot response
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
