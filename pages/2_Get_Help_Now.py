import streamlit as st
import json
from datetime import datetime
import random
import string

from supabase import create_client

def save_voucher(voucher):
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
    supabase.table("vouchers").insert({
        "voucher_id": voucher["voucher_id"],
        "postcode": voucher["postcode"],
        "adults": voucher["adults"],
        "children": voucher["children"],
        "dietary": ", ".join(voucher["dietary"]),
        "issued_at": voucher["issued_at"],
        "valid_days": voucher["valid_days"],
        "total_people": voucher["total_people"]
    }).execute()

st.set_page_config(page_title="Get Help Now", page_icon="📝", layout="wide")

st.title("📝 Get Help Now")
st.subheader("Fill this form to get your free digital food voucher instantly")

st.info(
    "🔒 **Your privacy matters.** This information is only used to "
    "prepare the right food parcel for you. It is never shared or sold."
)

st.markdown("---")

with st.form("referral_form"):
    st.markdown("### About you")

    col1, col2 = st.columns(2)
    with col1:
        postcode = st.text_input(
            "Your postcode *",
            value=st.session_state.get("user_postcode", ""),
            placeholder="e.g. HA1 1AA"
        )
        adults = st.number_input("Number of adults in household *", min_value=1, max_value=10, value=1)
        children = st.number_input("Number of children (under 16)", min_value=0, max_value=10, value=0)

    with col2:
        crisis_reason = st.selectbox(
            "Main reason for needing help * (this helps us support you better)",
            [
                "Select a reason",
                "Benefit delay or issue",
                "Job loss or reduced income",
                "Unexpected bill or expense",
                "Illness or disability",
                "Fleeing domestic abuse",
                "Asylum seeker / refugee",
                "Low income / working poverty",
                "Prefer not to say"
            ]
        )
        collection = st.radio(
            "Can you collect from a food bank?",
            ["Yes, I can collect", "No, I need delivery (elderly/disabled/ill)"]
        )

    st.markdown("### Dietary needs")
    st.write("Tick anything that applies:")

    dcol1, dcol2, dcol3 = st.columns(3)
    with dcol1:
        halal = st.checkbox("Halal")
        vegetarian = st.checkbox("Vegetarian")
        vegan = st.checkbox("Vegan")
    with dcol2:
        gluten_free = st.checkbox("Gluten free")
        dairy_free = st.checkbox("Dairy free")
        nut_allergy = st.checkbox("Nut allergy")
    with dcol3:
        baby_food = st.checkbox("Baby food needed")
        pet_food = st.checkbox("Pet food needed")
        kosher = st.checkbox("Kosher")

    other_dietary = st.text_input("Any other dietary needs or allergies?", placeholder="Optional")

    st.markdown("### Contact (optional)")
    st.write("Only needed if you want delivery confirmation. Leave blank to stay anonymous.")
    contact = st.text_input("Phone number or email (optional)")

    st.markdown("---")
    submitted = st.form_submit_button("🎫 Get My Free Voucher Now", use_container_width=True)

if submitted:
    if not postcode or crisis_reason == "Select a reason":
        st.error("Please fill in your postcode and reason for needing help.")
    else:
        # Generate unique voucher ID
        voucher_id = "CC-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        expiry = datetime.now().strftime("%d/%m/%Y")

        dietary = []
        if halal: dietary.append("Halal")
        if vegetarian: dietary.append("Vegetarian")
        if vegan: dietary.append("Vegan")
        if gluten_free: dietary.append("Gluten free")
        if dairy_free: dietary.append("Dairy free")
        if nut_allergy: dietary.append("Nut allergy")
        if baby_food: dietary.append("Baby food")
        if pet_food: dietary.append("Pet food")
        if kosher: dietary.append("Kosher")
        if other_dietary: dietary.append(other_dietary)

        # Save to session state to pass to voucher page
        st.session_state["voucher"] = {
            "voucher_id": voucher_id,
            "postcode": postcode.upper().replace(" ", ""),
            "adults": adults,
            "children": children,
            "total_people": adults + children,
            "crisis_reason": crisis_reason,
            "collection": collection,
            "dietary": dietary if dietary else ["No specific requirements"],
            "contact": contact,
            "issued_at": datetime.now().strftime("%d %b %Y, %H:%M"),
            "valid_days": 7
        }
        save_voucher(st.session_state["voucher"])

        st.success("✅ Your voucher is ready!")
        st.balloons()
        st.page_link("pages/3_Your_Voucher.py", label="👉 Click here to see your voucher", icon="🎫")