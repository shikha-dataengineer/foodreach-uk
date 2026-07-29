import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Find Food Bank", page_icon="🔍", layout="wide")

st.title("🔍 Find Food Banks Near You")
st.write("Start typing your postcode to see suggestions.")

def haversine(lat1, lng1, lat2, lng2):
    R = 3958.8
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

@st.cache_data(ttl=3600)
def load_all_foodbanks():
    response = requests.get("https://www.givefood.org.uk/api/2/locations/")
    data = response.json()
    rows = []
    for item in data:
        try:
            lat_str, lng_str = item["lat_lng"].split(",")
            rows.append({
                "name": item.get("name", ""),
                "address": item.get("address", "").replace("\r\n", ", ").replace("\n", ", "),
                "postcode": item.get("postcode", ""),
                "network": item["foodbank"].get("network", "Unknown"),
                "foodbank_name": item["foodbank"].get("name", ""),
                "lat": float(lat_str),
                "lng": float(lng_str),
            })
        except:
            continue
    return pd.DataFrame(rows)

@st.cache_data(ttl=60)
def autocomplete_postcode(query):
    if len(query) < 2:
        return []
    try:
        response = requests.get(f"https://api.postcodes.io/postcodes/{query}/autocomplete").json()
        if response["status"] == 200 and response["result"]:
            return response["result"]
    except:
        pass
    return []

with st.spinner("Loading food bank data..."):
    df_all = load_all_foodbanks()

col1, col2 = st.columns([3, 1])
with col1:
    typed = st.text_input("🔍 Type your postcode",
                           value=st.session_state.get("postcode_typed", ""),
                           placeholder="e.g. HA1").strip()
with col2:
    radius = st.selectbox("Search radius (miles)", [5, 10, 15, 20], index=1)

postcode = ""

if typed and len(typed) >= 2:
    suggestions = autocomplete_postcode(typed.replace(" ", ""))
    if suggestions:
        options = ["— Select your postcode —"] + suggestions
        selected = st.selectbox("📍 Select your postcode from the list:", options)
        if selected != "— Select your postcode —":
            postcode = selected.replace(" ", "")
            st.session_state["user_postcode"] = postcode
    else:
        # Try using typed directly if no autocomplete results
        postcode = typed.replace(" ", "")

if postcode:
    geo = requests.get(f"https://api.postcodes.io/postcodes/{postcode}").json()

    if geo["status"] == 200:
        lat = geo["result"]["latitude"]
        lng = geo["result"]["longitude"]
        area = geo["result"]["admin_district"]

        st.success(f"📍 Showing food banks within {radius} miles of **{postcode.upper()}** ({area})")

        df_nearby = df_all.copy()
        df_nearby["distance_miles"] = df_nearby.apply(
            lambda row: haversine(lat, lng, row["lat"], row["lng"]), axis=1
        )
        df_nearby = df_nearby[df_nearby["distance_miles"] <= radius]
        df_nearby = df_nearby.sort_values("distance_miles").reset_index(drop=True)

        if len(df_nearby) > 0:
            trussell = len(df_nearby[df_nearby["network"] == "Trussell"])
            independent = len(df_nearby[df_nearby["network"] != "Trussell"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Food Banks", len(df_nearby))
            c2.metric("Trussell (referral needed)", trussell)
            c3.metric("Independent (walk-in)", independent)

            st.info(
                "ℹ️ **Trussell food banks** need a referral before you visit.\n\n"
                "✅ **Independent food banks** usually accept walk-ins."
            )

            nearest = df_nearby.iloc[0]
            st.success(
                f"✅ **Nearest:** {nearest['name']} — "
                f"{nearest['address']} | "
                f"{round(nearest['distance_miles'], 1)} miles | "
                f"{nearest['network']}"
            )

            m = folium.Map(location=[lat, lng], zoom_start=12)
            folium.Marker(
                [lat, lng],
                popup="📍 Your location",
                tooltip="You are here",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)

            for _, fb in df_nearby.iterrows():
                pin_color = "green" if fb["network"] == "Trussell" else "blue"
                folium.Marker(
                    [fb["lat"], fb["lng"]],
                    popup=f"<b>{fb['name']}</b><br>{fb['address']}<br>{fb['network']}<br>{round(fb['distance_miles'],1)} miles",
                    tooltip=fb["name"],
                    icon=folium.Icon(color=pin_color, icon="info-sign")
                ).add_to(m)

            st_folium(m, width=None, height=500, use_container_width=True)
            st.caption("🟢 Green = Trussell | 🔵 Blue = Independent")

            display_df = df_nearby[["name","address","postcode","network","distance_miles"]].copy()
            display_df["distance_miles"] = display_df["distance_miles"].round(1)
            display_df["referral_needed"] = display_df["network"].apply(
                lambda x: "Yes" if x == "Trussell" else "No — walk-in"
            )
            display_df.columns = ["Name","Address","Postcode","Network","Distance (miles)","Referral Needed?"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.session_state["user_postcode"] = postcode.upper()

            st.divider()
            st.markdown("### Need food urgently?")
            st.page_link("pages/2_Get_Help_Now.py", label="👉 Click here to get a digital voucher now", icon="📝")

        else:
            st.warning("No food banks found. Try increasing the search radius.")
    else:
        st.error("❌ Postcode not found. Please check and try again.")
