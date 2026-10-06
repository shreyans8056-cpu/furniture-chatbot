import base64
import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st

# =====================================================================
# PAGE SETUP
# =====================================================================
st.set_page_config(page_title="Furniture Chatbot", page_icon="🛋️", layout="wide")

# =====================================================================
# DATA
# =====================================================================
RAW_CATALOGUE = [
    {"furniture": "sofa",         "category": "seating",  "material": "leather",         "price": 45000, "room": "living room", "available": True,  "delivery_days": 7},
    {"furniture": "sofa",         "category": "seating",  "material": "fabric",          "price": 25000, "room": "living room", "available": True,  "delivery_days": 5},
    {"furniture": "bed",          "category": "sleeping", "material": "wood",            "price": 30000, "room": "bedroom",     "available": True,  "delivery_days": 10},
    {"furniture": "bed",          "category": "sleeping", "material": "engineered wood", "price": 18000, "room": "bedroom",     "available": False, "delivery_days": 14},
    {"furniture": "dining table", "category": "dining",   "material": "wood",            "price": 35000, "room": "dining room", "available": True,  "delivery_days": 12},
    {"furniture": "dining table", "category": "dining",   "material": "glass",           "price": 22000, "room": "dining room", "available": True,  "delivery_days": 8},
    {"furniture": "wardrobe",     "category": "storage",  "material": "wood",            "price": 28000, "room": "bedroom",     "available": True,  "delivery_days": 15},
    {"furniture": "bookshelf",    "category": "storage",  "material": "metal",           "price": 8000,  "room": "office",      "available": True,  "delivery_days": 4},
    {"furniture": "office desk",  "category": "study",    "material": "wood",            "price": 12000, "room": "office",      "available": True,  "delivery_days": 6},
    {"furniture": "coffee table", "category": "seating",  "material": "glass",           "price": 6000,  "room": "living room", "available": True,  "delivery_days": 3},
    {"furniture": "recliner",     "category": "seating",  "material": "leather",         "price": 32000, "room": "living room", "available": False, "delivery_days": 20},
    {"furniture": "tv unit",      "category": "storage",  "material": "engineered wood", "price": 9000,  "room": "living room", "available": True,  "delivery_days": 5},
]
CATALOGUE = [{**item, "id": i} for i, item in enumerate(RAW_CATALOGUE)]
DF = pd.DataFrame(CATALOGUE)

FURNITURE_ITEMS = sorted(DF["furniture"].unique())
MATERIALS = sorted(DF["material"].unique())
ROOMS = sorted(DF["room"].unique())
CATEGORIES = sorted(DF["category"].unique())
MIN_PRICE, MAX_PRICE = int(DF["price"].min()), int(DF["price"].max())
MAX_DELIVERY = int(DF["delivery_days"].max())

# =====================================================================
# IMAGES  (drawn as SVG so the app never depends on external image links)
# Drop your own photos in an "images" folder named like "sofa.jpg" to override.
# =====================================================================
MATERIAL_COLORS = {
    "leather": "#8B5A2B", "fabric": "#5F86A8", "wood": "#A0724A",
    "engineered wood": "#C49A6C", "glass": "#7CC3DD", "metal": "#6B7280",
}


def _mix(hex_color, target, t):
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    out = [round(c + (target - c) * t) for c in rgb]
    return "#%02x%02x%02x" % tuple(out)


def furniture_svg(furn, material):
    c = MATERIAL_COLORS.get(material, "#888888")
    d, l = _mix(c, 0, 0.3), _mix(c, 255, 0.25)
    bg, floor = _mix(c, 255, 0.82), _mix(c, 255, 0.65)
    op = "0.6" if material == "glass" else "1"
    leg = "#3b3b3b"
    shapes = {
        "sofa": (
            f'<rect x="35" y="45" width="130" height="45" rx="12" fill="{c}"/>'
            f'<rect x="25" y="65" width="28" height="45" rx="10" fill="{d}"/>'
            f'<rect x="147" y="65" width="28" height="45" rx="10" fill="{d}"/>'
            f'<rect x="45" y="75" width="110" height="35" rx="8" fill="{l}"/>'
            f'<rect x="35" y="110" width="6" height="12" fill="{leg}"/><rect x="159" y="110" width="6" height="12" fill="{leg}"/>'
        ),
        "recliner": (
            f'<rect x="60" y="30" width="60" height="62" rx="14" fill="{c}"/>'
            f'<rect x="50" y="62" width="22" height="48" rx="9" fill="{d}"/>'
            f'<rect x="55" y="80" width="80" height="28" rx="10" fill="{l}"/>'
            f'<rect x="125" y="95" width="48" height="14" rx="7" fill="{d}"/>'
            f'<rect x="62" y="108" width="6" height="14" fill="{leg}"/><rect x="125" y="108" width="6" height="14" fill="{leg}"/>'
        ),
        "bed": (
            f'<rect x="28" y="30" width="16" height="82" rx="4" fill="{d}"/>'
            f'<rect x="28" y="76" width="146" height="28" rx="6" fill="{l}"/>'
            f'<rect x="75" y="76" width="99" height="28" rx="6" fill="#e9eaf2"/>'
            f'<rect x="48" y="66" width="30" height="14" rx="6" fill="#ffffff"/>'
            f'<rect x="28" y="104" width="6" height="14" fill="{leg}"/><rect x="168" y="104" width="6" height="14" fill="{leg}"/>'
        ),
        "dining table": (
            f'<rect x="30" y="58" width="140" height="14" rx="4" fill="{c}" fill-opacity="{op}" stroke="{d}"/>'
            f'<rect x="40" y="72" width="7" height="48" fill="{d}"/><rect x="153" y="72" width="7" height="48" fill="{d}"/>'
            f'<rect x="60" y="86" width="22" height="6" rx="3" fill="{l}"/><rect x="118" y="86" width="22" height="6" rx="3" fill="{l}"/>'
        ),
        "coffee table": (
            f'<rect x="45" y="75" width="110" height="12" rx="4" fill="{c}" fill-opacity="{op}" stroke="{d}"/>'
            f'<rect x="55" y="87" width="6" height="30" fill="{d}"/><rect x="139" y="87" width="6" height="30" fill="{d}"/>'
            f'<rect x="90" y="62" width="18" height="13" rx="3" fill="#ffffff"/>'
        ),
        "wardrobe": (
            f'<rect x="50" y="18" width="100" height="98" rx="5" fill="{c}"/>'
            f'<line x1="100" y1="18" x2="100" y2="116" stroke="{d}" stroke-width="2"/>'
            f'<circle cx="92" cy="68" r="3" fill="{l}"/><circle cx="108" cy="68" r="3" fill="{l}"/>'
            f'<rect x="56" y="116" width="8" height="6" fill="{leg}"/><rect x="136" y="116" width="8" height="6" fill="{leg}"/>'
        ),
        "bookshelf": (
            f'<rect x="55" y="16" width="90" height="104" rx="3" fill="{d}"/>'
            f'<rect x="60" y="21" width="80" height="94" fill="{bg}"/>'
            f'<rect x="60" y="52" width="80" height="4" fill="{c}"/><rect x="60" y="84" width="80" height="4" fill="{c}"/>'
            f'<rect x="64" y="30" width="8" height="22" fill="#c0553e"/><rect x="74" y="26" width="8" height="26" fill="#3e7cc0"/>'
            f'<rect x="84" y="32" width="8" height="20" fill="#d6a93e"/><rect x="108" y="29" width="10" height="23" fill="#4aa37a"/>'
            f'<rect x="66" y="62" width="10" height="22" fill="#7a55c0"/><rect x="100" y="64" width="8" height="20" fill="#c0553e"/>'
            f'<rect x="70" y="94" width="12" height="21" fill="#3e7cc0"/><rect x="112" y="98" width="9" height="17" fill="#d6a93e"/>'
        ),
        "office desk": (
            f'<rect x="30" y="58" width="140" height="10" rx="3" fill="{c}"/>'
            f'<rect x="36" y="68" width="6" height="50" fill="{d}"/>'
            f'<rect x="130" y="68" width="36" height="50" rx="3" fill="{d}"/>'
            f'<rect x="136" y="76" width="24" height="3" fill="{l}"/><rect x="136" y="92" width="24" height="3" fill="{l}"/>'
            f'<rect x="70" y="30" width="46" height="26" rx="3" fill="#2b2f3a"/><rect x="90" y="56" width="6" height="2" fill="#2b2f3a"/>'
        ),
        "tv unit": (
            f'<rect x="30" y="82" width="140" height="30" rx="4" fill="{c}"/>'
            f'<line x1="100" y1="82" x2="100" y2="112" stroke="{d}" stroke-width="2"/>'
            f'<rect x="55" y="30" width="90" height="46" rx="3" fill="#1f2330"/>'
            f'<rect x="60" y="35" width="80" height="36" fill="#324a6b"/>'
            f'<rect x="40" y="112" width="6" height="8" fill="{leg}"/><rect x="154" y="112" width="6" height="8" fill="{leg}"/>'
        ),
    }
    body = shapes.get(furn, "")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 140">'
        f'<rect width="200" height="140" fill="{bg}"/><rect y="118" width="200" height="22" fill="{floor}"/>'
        f'{body}</svg>'
    )


@st.cache_data(show_spinner=False)
def image_uri(furn, material):
    """Return a data-URI for the item image (your own photo if provided, else the SVG)."""
    import os
    for ext, mime in (("jpg", "jpeg"), ("jpeg", "jpeg"), ("png", "png"), ("webp", "webp")):
        for name in (f"{furn}_{material}".replace(" ", "_"), furn.replace(" ", "_")):
            path = os.path.join("images", f"{name}.{ext}")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()
    svg = furniture_svg(furn, material)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def card_html(item, small=False):
    ok = item["available"]
    badge = (
        '<span class="badge ok">In stock</span>' if ok else '<span class="badge no">Out of stock</span>'
    )
    return (
        '<div class="card">'
        f'<img src="{image_uri(item["furniture"], item["material"])}" alt="{item["furniture"]}"/>'
        '<div class="body">'
        f'<div class="ttl">{item["furniture"].title()}</div>'
        f'<div class="price">₹{item["price"]:,}</div>'
        f'<div class="meta">{item["material"].title()} · {item["room"].title()}</div>'
        f'<div>{badge}<span class="badge">{item["delivery_days"]} day delivery</span></div>'
        '</div></div>'
    )


# =====================================================================
# STYLE
# =====================================================================
st.markdown(
    """
<style>
.hero{background:#17332c;color:#f3efe6;padding:2.2rem 2.4rem;border-radius:16px;margin-bottom:1rem}
.hero h1{margin:0 0 .4rem 0;font-size:2.4rem;color:#f3efe6;padding:0}
.hero p{margin:0;font-size:1.05rem;color:#cfe0d8;max-width:46rem}
.step{border-left:4px solid #d6a85c;padding:.2rem .9rem;margin-bottom:.6rem}
.step b{display:block;font-size:1.02rem}
.step span{opacity:.8;font-size:.92rem}
.card{border:1px solid rgba(128,128,128,.3);border-radius:12px;overflow:hidden;
      background:rgba(128,128,128,.07);margin-bottom:.4rem}
.card img{width:100%;display:block}
.card .body{padding:.65rem .85rem .8rem .85rem}
.card .ttl{font-weight:600;font-size:1.02rem}
.card .price{font-size:1.2rem;font-weight:700;color:#d6a85c}
.card .meta{opacity:.75;font-size:.85rem;margin-bottom:.4rem}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.74rem;
       margin-right:5px;background:rgba(128,128,128,.22)}
.badge.ok{background:rgba(34,197,94,.25)}
.badge.no{background:rgba(239,68,68,.25)}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# SESSION STATE
# =====================================================================
ss = st.session_state
ss.setdefault("messages", [])
ss.setdefault("chat_ctx", {})
ss.setdefault("wishlist", [])
ss.setdefault("quotes", [])


def toggle_wish(item_id):
    if item_id in ss.wishlist:
        ss.wishlist.remove(item_id)
    else:
        ss.wishlist.append(item_id)


def reset_filters():
    ss.f_search = ""
    ss.f_room = "All rooms"
    ss.f_materials = []
    ss.f_categories = []
    ss.f_price = (MIN_PRICE, MAX_PRICE)
    ss.f_available = False
    ss.f_delivery = MAX_DELIVERY
    ss.f_sort = "Price: low to high"


# =====================================================================
# CHATBOT BRAIN  (rule-based, but remembers context for follow-ups)
# =====================================================================
ALIASES = {
    "couch": "sofa", "settee": "sofa", "cupboard": "wardrobe", "closet": "wardrobe",
    "desk": "office desk", "shelf": "bookshelf", "shelves": "bookshelf",
    "tv stand": "tv unit", "television unit": "tv unit", "dining": None,
    "center table": "coffee table", "centre table": "coffee table",
}
MATERIAL_WORDS = [
    ("engineered wood", ["engineered", "mdf", "plywood", "particle"]),
    ("wood", ["wood", "wooden", "teak", "oak"]),
    ("leather", ["leather"]),
    ("fabric", ["fabric", "cloth"]),
    ("glass", ["glass"]),
    ("metal", ["metal", "metallic", "steel", "iron"]),
]
ROOM_ALIASES = {"hall": "living room", "drawing room": "living room", "study": "office", "bed room": "bedroom"}


def _to_amount(num, suffix):
    value = float(num.replace(",", ""))
    if suffix in ("k", "K"):
        value *= 1_000
    elif suffix and suffix.lower().startswith("lakh"):
        value *= 100_000
    return int(value)


def parse_query(text):
    t = text.lower()
    q = {}

    found = [f for f in FURNITURE_ITEMS if re.search(rf"\b{re.escape(f)}s?\b", t)]
    for alias, target in ALIASES.items():
        if target and re.search(rf"\b{re.escape(alias)}s?\b", t) and target not in found:
            found.append(target)
    if "table" in t and not any("table" in f for f in found):
        found += ["dining table", "coffee table"]
    if found:
        q["furniture"] = found

    for room in ROOMS:
        if room in t:
            q["room"] = room
    for alias, room in ROOM_ALIASES.items():
        if re.search(rf"\b{alias}\b", t):
            q["room"] = room

    for material, words in MATERIAL_WORDS:
        if any(re.search(rf"\b{w}\b", t) for w in words):
            q["material"] = material
            break

    m = re.search(
        r"(?:under|below|less than|within|upto|up to|budget|max(?:imum)?|around|<)\s*(?:of\s*)?"
        r"(?:₹|rs\.?|inr)?\s*(\d[\d,]*(?:\.\d+)?)\s*(k|lakhs?)?", t)
    if m and not re.match(r"\s*days?", t[m.end():]):
        q["max_price"] = _to_amount(m.group(1), m.group(2))
    else:
        m = re.search(r"(?:₹|rs\.?|inr)\s*(\d[\d,]*)\s*(k|lakhs?)?|\b(\d[\d,]*)\s*(k|lakhs?)\b", t)
        if m:
            q["max_price"] = _to_amount(m.group(1) or m.group(3), m.group(2) or m.group(4))
        else:
            nums = re.findall(r"\b\d{4,}\b", t.replace(",", ""))
            if nums:
                q["max_price"] = int(nums[-1])

    if re.search(r"\b(in stock|available|availability)\b", t) and not re.search(r"\b(unavailable|not available)\b", t):
        q["available"] = True

    d = re.search(r"(?:within|in|under)\s*(\d+)\s*days?", t)
    if d:
        q["max_delivery"] = int(d.group(1))
        q.pop("max_price", None) if q.get("max_price") == int(d.group(1)) else None
    elif re.search(r"\b(fast|quick|quickest|fastest|urgent|asap)\b", t):
        q["max_delivery"] = 7

    if re.search(r"\b(cheapest|lowest price)\b", t):
        q["sort"], q["top1"] = "asc", True
    elif re.search(r"\b(cheap|affordable|budget friendly|cheaper)\b", t):
        q["sort"] = "asc"
    elif re.search(r"\b(costliest|most expensive|priciest|premium|luxury)\b", t):
        q["sort"], q["top1"] = "desc", True
    return q


def run_query(q):
    out = []
    for it in CATALOGUE:
        if q.get("furniture") and it["furniture"] not in q["furniture"]:
            continue
        if q.get("room") and it["room"] != q["room"]:
            continue
        if q.get("material") and it["material"] != q["material"]:
            continue
        if q.get("max_price") and it["price"] > q["max_price"]:
            continue
        if q.get("available") and not it["available"]:
            continue
        if q.get("max_delivery") and it["delivery_days"] > q["max_delivery"]:
            continue
        out.append(it)
    if q.get("sort") == "asc":
        out.sort(key=lambda x: x["price"])
    elif q.get("sort") == "desc":
        out.sort(key=lambda x: -x["price"])
    if q.get("top1"):
        out = out[:1]
    return out


def describe(q):
    bits = []
    if q.get("furniture"):
        bits.append(", ".join(q["furniture"]))
    if q.get("material"):
        bits.append(q["material"])
    if q.get("room"):
        bits.append(f"for {q['room']}")
    if q.get("max_price"):
        bits.append(f"under ₹{q['max_price']:,}")
    if q.get("max_delivery"):
        bits.append(f"delivered within {q['max_delivery']} days")
    if q.get("available"):
        bits.append("in stock")
    return " · ".join(bits) if bits else "everything"


HELP_TEXT = (
    "Try things like:\n\n"
    "- *Show me sofas*\n- *Wooden furniture under 30k*\n- *Something for the bedroom*\n"
    "- *Cheapest dining table*\n- *Available items delivered within 7 days*\n"
    "- Then follow up with *what about leather?* or *only in stock*\n\n"
    "Say **reset** to clear what I remember."
)


def respond(text):
    """Returns (reply_text, list_of_item_ids)."""
    t = text.lower().strip()

    if re.search(r"\b(hi|hello|hey|namaste)\b", t) and len(t.split()) <= 4:
        return "Hello! 👋 Tell me what you're looking for. I can filter by price, room, material, stock and delivery time.", []
    if re.search(r"\b(help|what can you do)\b", t):
        return HELP_TEXT, []
    if re.search(r"\b(reset|clear|start over|new search)\b", t):
        ss.chat_ctx = {}
        return "Done. I've cleared my memory of your search. What would you like to look at?", []
    if re.search(r"\b(thanks|thank you)\b", t):
        return "You're welcome! Add anything you like to your wishlist, then request a quote in the **Quote** tab.", []

    q = parse_query(text)
    if not q:
        return "I couldn't pick out a furniture type, room, material or budget from that.\n\n" + HELP_TEXT, []

    follow_up = ss.chat_ctx and re.search(
        r"\b(what about|how about|also|those|them|these|instead|only|and|cheaper|but)\b", t)
    if follow_up:
        merged = {**ss.chat_ctx, **q}
        if "cheaper" in t and "max_price" not in q:
            merged["sort"] = "asc"
        q = merged
    ss.chat_ctx = {k: v for k, v in q.items() if k not in ("top1",)}

    results = run_query(q)
    if results:
        return f"I found **{len(results)}** match{'es' if len(results) != 1 else ''} for *{describe(q)}*:", [r["id"] for r in results]

    relaxed = {k: v for k, v in q.items() if k not in ("max_price", "max_delivery", "available")}
    near = run_query({**relaxed, "sort": "asc"})[:3]
    if near:
        return (f"Nothing matches *{describe(q)}* exactly. Here are the closest options if you relax the budget, "
                "stock or delivery limit:"), [r["id"] for r in near]
    return f"Nothing matches *{describe(q)}*. Say **reset** and try a broader search.", []


def render_items(ids, key_prefix):
    items = [CATALOGUE[i] for i in ids]
    for row_start in range(0, len(items), 3):
        cols = st.columns(3)
        for col, it in zip(cols, items[row_start:row_start + 3]):
            with col:
                st.markdown(card_html(it), unsafe_allow_html=True)
                wished = it["id"] in ss.wishlist
                st.button(
                    "❤️ Saved" if wished else "🤍 Save",
                    key=f"{key_prefix}_{it['id']}", on_click=toggle_wish, args=(it["id"],),
                    use_container_width=True,
                )


# =====================================================================
# SIDEBAR FILTERS  (live, every change re-runs the app)
# =====================================================================
with st.sidebar:
    st.header("Filter furniture")
    st.text_input("Search by name", key="f_search", placeholder="e.g. sofa, glass, bedroom")
    st.selectbox("Room", ["All rooms"] + ROOMS, key="f_room")
    st.multiselect("Material", MATERIALS, key="f_materials", placeholder="Any material")
    st.multiselect("Category", CATEGORIES, key="f_categories", placeholder="Any category")
    st.slider("Budget (₹)", MIN_PRICE, MAX_PRICE, (MIN_PRICE, MAX_PRICE), step=500, key="f_price")
    st.slider("Delivery within (days)", 1, MAX_DELIVERY, MAX_DELIVERY, key="f_delivery")
    st.checkbox("Only show items in stock", key="f_available")
    st.selectbox("Sort by", ["Price: low to high", "Price: high to low", "Fastest delivery"], key="f_sort")
    st.button("Reset filters", on_click=reset_filters, use_container_width=True)

    st.divider()
    st.subheader(f"❤️ Wishlist ({len(ss.wishlist)})")
    if ss.wishlist:
        total = 0
        for i in ss.wishlist:
            it = CATALOGUE[i]
            total += it["price"]
            st.write(f"{it['furniture'].title()} ({it['material']}): ₹{it['price']:,}")
        st.markdown(f"**Total: ₹{total:,}**")
        st.button("Clear wishlist", on_click=ss.wishlist.clear)
    else:
        st.caption("Tap 🤍 Save on any item to add it here.")

# =====================================================================
# HERO + "WHAT THIS APP DOES"
# =====================================================================
st.markdown(
    '<div class="hero"><h1>🛋️ Furniture Chatbot</h1>'
    "<p>Find the right furniture for any room. Filter by budget, material and delivery time, "
    "chat in plain English, save favourites and request a quote.</p></div>",
    unsafe_allow_html=True,
)

showcase = [("sofa", "leather", "Living room"), ("bed", "wood", "Bedroom"),
            ("dining table", "glass", "Dining room"), ("office desk", "wood", "Office")]
img_cols = st.columns(4)
for col, (furn, mat, label) in zip(img_cols, showcase):
    with col:
        st.markdown(
            f'<div class="card"><img src="{image_uri(furn, mat)}" alt="{furn}"/>'
            f'<div class="body"><div class="ttl">{label}</div></div></div>',
            unsafe_allow_html=True,
        )

h1, h2, h3 = st.columns(3)
h1.markdown('<div class="step"><b>1. Filter</b><span>Use the sidebar to narrow by room, material, budget and stock.</span></div>', unsafe_allow_html=True)
h2.markdown('<div class="step"><b>2. Chat</b><span>Ask in plain English, then follow up with "what about leather?".</span></div>', unsafe_allow_html=True)
h3.markdown('<div class="step"><b>3. Save and quote</b><span>Save favourites, then send a quote request with your details.</span></div>', unsafe_allow_html=True)

# =====================================================================
# APPLY SIDEBAR FILTERS
# =====================================================================
view = DF.copy()
if ss.f_search.strip():
    s = ss.f_search.strip().lower()
    mask = (view["furniture"].str.contains(s) | view["material"].str.contains(s)
            | view["room"].str.contains(s) | view["category"].str.contains(s))
    view = view[mask]
if ss.f_room != "All rooms":
    view = view[view["room"] == ss.f_room]
if ss.f_materials:
    view = view[view["material"].isin(ss.f_materials)]
if ss.f_categories:
    view = view[view["category"].isin(ss.f_categories)]
view = view[view["price"].between(*ss.f_price)]
view = view[view["delivery_days"] <= ss.f_delivery]
if ss.f_available:
    view = view[view["available"]]
sort_map = {"Price: low to high": ("price", True), "Price: high to low": ("price", False),
            "Fastest delivery": ("delivery_days", True)}
col_name, asc = sort_map[ss.f_sort]
view = view.sort_values(col_name, ascending=asc)

# =====================================================================
# TABS
# =====================================================================
tab_browse, tab_chat, tab_insights, tab_quote = st.tabs(["🛍️ Browse", "💬 Chat", "📊 Insights", "📝 Quote"])

# ---------------------------- BROWSE ---------------------------------
with tab_browse:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Items found", len(view))
    m2.metric("Average price", f"₹{int(view['price'].mean()):,}" if len(view) else "-")
    m3.metric("Lowest price", f"₹{int(view['price'].min()):,}" if len(view) else "-")
    m4.metric("Fastest delivery", f"{int(view['delivery_days'].min())} days" if len(view) else "-")

    if view.empty:
        st.info("No furniture matches these filters. Widen the budget or delivery range, or press **Reset filters** in the sidebar.")
    else:
        render_items(view["id"].tolist(), "browse")

# ----------------------------- CHAT ----------------------------------
with tab_chat:
    st.caption("I remember your last search, so you can follow up with things like *what about leather?* or *only in stock*.")

    chips = ["Show me sofas", "Wooden furniture under 30k", "Cheapest dining table",
             "Furniture for bedroom", "Available items within 7 days"]
    chip_cols = st.columns(len(chips))
    for col, chip in zip(chip_cols, chips):
        if col.button(chip, key=f"chip_{chip}", use_container_width=True):
            ss.pending_prompt = chip

    history = st.container()
    typed = st.chat_input("Ask me about furniture...")
    prompt = typed or ss.pop("pending_prompt", None)

    if prompt:
        ss.messages.append({"role": "user", "content": prompt, "items": []})
        reply, ids = respond(prompt)
        ss.messages.append({"role": "assistant", "content": reply, "items": ids})

    with history:
        if not ss.messages:
            with st.chat_message("assistant"):
                st.write("Hello! 👋 Ask me about furniture, prices, materials, rooms, availability or delivery. Tap a suggestion above to start.")
        for n, msg in enumerate(ss.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["items"]:
                    render_items(msg["items"], f"chat{n}")

    if ss.messages and st.button("Clear chat"):
        ss.messages, ss.chat_ctx = [], {}
        st.rerun()

# --------------------------- INSIGHTS --------------------------------
with tab_insights:
    if view.empty:
        st.info("Nothing to chart yet. Adjust the sidebar filters.")
    else:
        chart_df = view.assign(label=view["furniture"].str.title() + " (" + view["material"] + ")")
        left, right = st.columns(2)
        with left:
            st.subheader("Price by item (₹)")
            st.bar_chart(chart_df.set_index("label")["price"])
        with right:
            st.subheader("Delivery time (days)")
            st.bar_chart(chart_df.set_index("label")["delivery_days"])
        st.subheader("Average price by room")
        st.bar_chart(view.groupby("room")["price"].mean())
        st.subheader("Matching items")
        st.dataframe(
            view[["furniture", "material", "room", "category", "price", "available", "delivery_days"]],
            use_container_width=True, hide_index=True,
        )

# ----------------------------- QUOTE ---------------------------------
with tab_quote:
    st.subheader("Request a quote")
    labels = {f"{it['furniture'].title()} · {it['material']} · ₹{it['price']:,}": it["id"] for it in CATALOGUE}
    default_label = None
    if ss.wishlist:
        wid = ss.wishlist[-1]
        default_label = next(k for k, v in labels.items() if v == wid)
    label_list = list(labels.keys())

    with st.form("quote_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name *")
        phone = c2.text_input("Phone number *", placeholder="10-digit mobile number")
        email = c1.text_input("Email")
        city = c2.text_input("City / PIN code *")
        item_label = c1.selectbox("Item *", label_list, index=label_list.index(default_label) if default_label else 0)
        qty = c2.number_input("Quantity", min_value=1, max_value=20, value=1, step=1)
        want_date = c1.date_input("Preferred delivery date", min_value=date.today() + timedelta(days=1),
                                  value=date.today() + timedelta(days=14))
        payment = c2.radio("Payment", ["UPI", "Card", "Cash on delivery"], horizontal=True)
        assembly = st.checkbox("Include assembly (₹500 per item)")
        notes = st.text_area("Notes", placeholder="Colour preference, floor number, lift access...")
        submitted = st.form_submit_button("Send quote request", type="primary")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Enter your name.")
        if not re.fullmatch(r"[6-9]\d{9}", phone.strip().replace(" ", "")):
            errors.append("Enter a valid 10-digit Indian mobile number.")
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            errors.append("Enter a valid email address or leave it blank.")
        if not city.strip():
            errors.append("Enter your city or PIN code.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            it = CATALOGUE[labels[item_label]]
            total = it["price"] * qty + (500 * qty if assembly else 0)
            earliest = date.today() + timedelta(days=it["delivery_days"])
            ss.quotes.append({
                "Name": name.strip(), "Item": f"{it['furniture'].title()} ({it['material']})",
                "Qty": qty, "Total (₹)": total, "City": city.strip(), "Payment": payment,
            })
            st.success(f"Thanks {name.strip()}! Your quote request is saved.")
            q1, q2, q3 = st.columns(3)
            q1.metric("Estimated total", f"₹{total:,}")
            q2.metric("Earliest delivery", earliest.strftime("%d %b %Y"))
            q3.metric("Stock", "In stock" if it["available"] else "Backorder")
            if not it["available"]:
                st.warning("This item is currently out of stock, so delivery may take longer than shown.")
            if want_date < earliest:
                st.warning(f"Your preferred date is earlier than the earliest delivery date ({earliest.strftime('%d %b %Y')}).")

    if ss.quotes:
        st.subheader("Your requests this session")
        st.dataframe(pd.DataFrame(ss.quotes), use_container_width=True, hide_index=True)
