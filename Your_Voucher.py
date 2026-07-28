import streamlit as st
import qrcode
from PIL import Image
import io
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import math
from supabase import create_client

st.set_page_config(page_title="Your Voucher", page_icon="🎫", layout="wide")

def haversine(lat1, lng1, lat2, lng2):
    R = 3958.8
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def get_voucher(voucher_id):
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
    result = supabase.table("vouchers").select("*").eq("voucher_id", voucher_id).execute()
    if result.data:
        row = result.data[0]
        return {
            "voucher_id": row["voucher_id"],
            "postcode": row["postcode"],
            "adults": row["adults"],
            "children": row["children"],
            "dietary": row["dietary"].split(", "),
            "issued_at": row["issued_at"],
            "valid_days": row["valid_days"],
            "total_people": row["total_people"]
        }
    return None

@st.cache_data(ttl=3600)
def load_walkin_foodbanks():
    response = requests.get("https://www.givefood.org.uk/api/2/locations/")
    data = response.json()
    rows = []
    for item in data:
        try:
            if item["foodbank"].get("network") == "Trussell":
                continue
            lat_str, lng_str = item["lat_lng"].split(",")
            rows.append({
                "name": item.get("name", ""),
                "address": item.get("address","").replace("\r\n", ", ").replace("\n", ", "),
                "postcode": item.get("postcode",""),
                "phone": item.get("phone",""),
                "email": item.get("email",""),
                "lat": float(lat_str),
                "lng": float(lng_str),
            })
        except:
            continue
    return pd.DataFrame(rows)

st.title("🎫 Your Digital Food Voucher")

# Check URL for voucher ID (when scanning QR code)
params = st.query_params
voucher_id_param = params.get("id", None)

if voucher_id_param:
    v = get_voucher(voucher_id_param)
    if v:
        st.session_state["voucher"] = v
    else:
        st.error("❌ Voucher not found!")
        st.stop()
elif "voucher" not in st.session_state:
    st.warning("No voucher found. Please fill in the form first.")
    st.page_link("pages/2_Get_Help_Now.py", label="👉 Go to the form", icon="📝")
    st.stop()
else:
    v = st.session_state["voucher"]

issued = datetime.strptime(v["issued_at"], "%d %b %Y, %H:%M")
expiry = issued + timedelta(days=v["valid_days"])
expiry_str = expiry.strftime("%d %b %Y")

# Generate QR code pointing to the live app with voucher ID
qr_data = f"https://foodreach-uk.streamlit.app/Your_Voucher?id={v['voucher_id']}"
qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data(qr_data)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white")
buf = io.BytesIO()
qr_img.save(buf, format="PNG")
buf.seek(0)

# ── SECTION 1: Voucher + QR ──────────────────────────────
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
    ### 🎫 Your Voucher

    | | |
    |---|---|
    | **Voucher ID** | `{v['voucher_id']}` |
    | **Valid until** | {expiry_str} |
    | **Your area** | {v['postcode']} |
    | **People** | {v['adults']} adult(s), {v['children']} child(ren) |
    | **Food needs** | {', '.join(v['dietary'])} |
    """)

    st.success(
        "✅ **How to use this voucher:**\n\n"
        "1. Pick a food bank below\n"
        "2. Go there during opening hours\n"
        "3. Show this screen or the QR code\n"
        "4. Collect your food — that's it!"
    )

with col2:
    st.markdown("### 📱 Show this at the food bank")
    st.image(buf, width=280)
    st.caption(f"ID: {v['voucher_id']} | Valid until {expiry_str}")
    buf.seek(0)
    st.download_button(
        label="📥 Save to phone",
        data=buf,
        file_name=f"voucher_{v['voucher_id']}.png",
        mime="image/png"
    )

# ── SECTION 2: Walk-in Food Banks Only ───────────────────
st.markdown("---")
st.subheader("📍 Food Banks Near You — Just Walk In")
st.success(
    "✅ All food banks shown below are **walk-in only** — "
    "no phone calls, no codes, no waiting. Just show up with your voucher."
)

with st.spinner("Finding food banks near you..."):
    df_all = load_walkin_foodbanks()

    geo = requests.get(
        f"https://api.postcodes.io/postcodes/{v['postcode'].replace(' ','')}"
    ).json()

    if geo["status"] == 200:
        lat = geo["result"]["latitude"]
        lng = geo["result"]["longitude"]

        df_nearby = df_all.copy()
        df_nearby["distance_miles"] = df_nearby.apply(
            lambda row: haversine(lat, lng, row["lat"], row["lng"]), axis=1
        )
        df_nearby = df_nearby[df_nearby["distance_miles"] <= 10].sort_values("distance_miles").reset_index(drop=True)

        if len(df_nearby) > 0:
            st.write(f"Found **{len(df_nearby)} walk-in food banks** within 10 miles of {v['postcode']}")

            # Top 3 cards
            top3 = df_nearby.head(3)
            for i, (_, fb) in enumerate(top3.iterrows()):
                rank = ["🥇", "🥈", "🥉"][i]
                phone_text = fb['phone'] if fb["phone"] else "Search name online for opening hours"
                maps_url = f"https://www.google.com/maps/search/?api=1&query={fb['address'].replace(' ', '+')}"

                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {rank} {fb['name']}")
                    with c2:
                        st.success("🚶 WALK IN")

                    st.markdown(f"📍 **Address:** {fb['address']}")
                    st.markdown(f"📏 **Distance:** {round(fb['distance_miles'], 1)} miles away")
                    st.markdown(f"📞 **Phone:** {phone_text}")
                    st.markdown(f"[🗺️ Get directions on Google Maps]({maps_url})")
                    st.success(
                        f"✅ Just walk in and say:\n\n"
                        f"*\"I have a CrisisConnect voucher, ID: {v['voucher_id']}\"*\n\n"
                        f"They will prepare food for {v['total_people']} person(s) "
                        f"with these needs: {', '.join(v['dietary'])}"
                    )

            # Map
            st.markdown("#### 🗺️ Map")
            m = folium.Map(location=[lat, lng], zoom_start=12)
            folium.Marker(
                [lat, lng],
                popup="📍 You are here",
                tooltip="You are here",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)

            for j, (_, fb) in enumerate(df_nearby.iterrows()):
                color = "orange" if j < 3 else "green"
                folium.Marker(
                    [fb["lat"], fb["lng"]],
                    popup=f"<b>{fb['name']}</b><br>{fb['address']}<br>{round(fb['distance_miles'],1)} miles",
                    tooltip=fb["name"],
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(m)

            st_folium(m, width=None, height=400, use_container_width=True)
            st.caption("⭐ Orange = Your nearest 3 | 🟢 Green = Other walk-in food banks")

            with st.expander("📋 See full list of walk-in food banks nearby"):
                show_df = df_nearby[["name","address","postcode","distance_miles"]].copy()
                show_df["distance_miles"] = show_df["distance_miles"].round(1)
                show_df["access"] = "🚶 Just walk in"
                show_df.columns = ["Name","Address","Postcode","Distance (miles)","Access"]
                st.dataframe(show_df, use_container_width=True, hide_index=True)

        else:
            st.warning(
                "⚠️ No walk-in food banks found within 10 miles. "
                "Please use the **free home delivery** option below — "
                "a volunteer will bring food to your door within 24 hours."
            )

# ── SECTION 3: Home Delivery ─────────────────────────────
st.markdown("---")
st.subheader("🚚 Prefer Home Delivery? Request It Free")
st.write(
    "Can't travel? Elderly, disabled, no transport, or simply prefer delivery? "
    "Fill this form and a volunteer will deliver food to your door — completely free."
)

with st.form("delivery_form"):
    st.markdown("#### Your delivery details")

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        delivery_name = st.text_input("Your name *", placeholder="First name is fine")
        delivery_address = st.text_area(
            "Delivery address *",
            placeholder="House number, Street, Town, Postcode"
        )
        delivery_phone = st.text_input(
            "Phone number *",
            placeholder="So the volunteer can confirm arrival time"
        )

    with dcol2:
        delivery_time = st.selectbox(
            "Best time for delivery *",
            ["Morning (9am-12pm)", "Afternoon (12pm-5pm)", "Evening (5pm-7pm)", "Any time"]
        )
        delivery_days = st.multiselect(
            "Which days suit you? *",
            ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            default=["Monday","Tuesday","Wednesday","Thursday","Friday"]
        )
        delivery_reason = st.selectbox(
            "Why do you need delivery? *",
            [
                "Select",
                "Elderly — difficulty travelling",
                "Disability or health condition",
                "No transport",
                "Caring for someone at home",
                "Mental health — difficulty leaving home",
                "No childcare",
                "Prefer not to say"
            ]
        )

    delivery_notes = st.text_area(
        "Notes for the volunteer (optional)",
        placeholder="e.g. ground floor, ring doorbell twice, gate code 1234..."
    )

    st.caption("🔒 Your details are only shared with your local food bank volunteer. Never sold or shared.")
    delivery_submit = st.form_submit_button("📦 Request Free Home Delivery", use_container_width=True)

if delivery_submit:
    if not delivery_name or not delivery_address or not delivery_phone or delivery_reason == "Select" or not delivery_days:
        st.error("Please fill in all fields marked with *")
    else:
        st.session_state["delivery_request"] = {
            "voucher_id": v["voucher_id"],
            "name": delivery_name,
            "address": delivery_address,
            "phone": delivery_phone,
            "time": delivery_time,
            "days": ", ".join(delivery_days),
            "reason": delivery_reason,
            "notes": delivery_notes,
            "dietary": ", ".join(v["dietary"]),
            "people": v["total_people"],
            "requested_at": datetime.now().strftime("%d %b %Y, %H:%M")
        }
        dr = st.session_state["delivery_request"]

        st.success("✅ Delivery request submitted!")
        st.balloons()

        with st.container(border=True):
            st.markdown(f"""
            ### 📋 Delivery Confirmation

            | | |
            |---|---|
            | **Voucher ID** | `{dr['voucher_id']}` |
            | **Name** | {dr['name']} |
            | **Delivery address** | {dr['address']} |
            | **Phone** | {dr['phone']} |
            | **Delivery time** | {dr['time']} |
            | **Days** | {dr['days']} |
            | **Food needs** | {dr['dietary']} |
            | **People** | {dr['people']} |
            | **Requested** | {dr['requested_at']} |
            """)

        st.info(
            "📞 **What happens next:**\n\n"
            "1. Your nearest food bank receives this request automatically\n"
            "2. A volunteer will call **" + dr['phone'] + "** within 24 hours to confirm\n"
            "3. They bring food to your door — free, no questions asked\n\n"
            "If you don't hear back within 24 hours:\n"
            "Call Citizens Advice FREE: **0800 144 8848**"
        )

# ── SECTION 4: Summary ───────────────────────────────────
st.markdown("---")
with st.container(border=True):
    st.markdown("""
    ### 📋 Your two options — both completely free

    **Option A — Collect yourself 🚶**
    Pick any food bank above → go during opening hours →
    show your voucher → collect your food. Done.

    **Option B — Home delivery 🚚**
    Fill the form above → volunteer calls within 24hrs →
    food comes to your door. No travel needed.
    """)

st.divider()
st.caption("CrisisConnect UK | Free & Open Source | Built by Shikha Agarwal | Data from Give Food API")
