import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import math

st.set_page_config(page_title="Council Dashboard", page_icon="📊", layout="wide")

st.title("📊 Council & Charity Dashboard")
st.subheader("Real-time food bank coverage and crisis data across the UK")

st.info(
    "This dashboard is designed for local councils, charities and policy makers "
    "to understand food bank coverage gaps and demand patterns in their area."
)

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
                "address": item.get("address","").replace("\r\n",", ").replace("\n",", "),
                "postcode": item.get("postcode",""),
                "network": item["foodbank"].get("network","Unknown"),
                "foodbank_name": item["foodbank"].get("name",""),
                "lat": float(lat_str),
                "lng": float(lng_str),
                "constituency": item.get("politics",{}).get("parliamentary_constituency","Unknown"),
                "district": item.get("politics",{}).get("district","Unknown"),
            })
        except:
            continue
    return pd.DataFrame(rows)

with st.spinner("Loading data..."):
    df = load_all_foodbanks()

st.markdown("---")

# --- National Overview ---
st.subheader("🇬🇧 National Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Food Bank Locations", len(df))
c2.metric("Trussell Network", len(df[df["network"]=="Trussell"]))
c3.metric("Independent", len(df[df["network"]=="Independent"]))
c4.metric("Other Networks", len(df[~df["network"].isin(["Trussell","Independent"])]))

# Network breakdown chart
st.markdown("#### Breakdown by Network")
network_counts = df["network"].value_counts().reset_index()
network_counts.columns = ["Network", "Count"]
fig1 = px.bar(
    network_counts,
    x="Network", y="Count",
    color="Network",
    title="Food Banks by Network Type",
    color_discrete_map={"Trussell":"#2ecc71","Independent":"#3498db","Salvation Army":"#e74c3c"}
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# --- Area Analysis ---
st.subheader("🔍 Analyse a Specific Area")

col1, col2 = st.columns([3,1])
with col1:
    area_postcode = st.text_input("Enter a council/area postcode to analyse", placeholder="e.g. HA1 1AA")
with col2:
    area_radius = st.selectbox("Radius (miles)", [5, 10, 15, 20, 30], index=2)

if area_postcode:
    geo = requests.get(
        f"https://api.postcodes.io/postcodes/{area_postcode.strip().replace(' ','')}"
    ).json()

    if geo["status"] == 200:
        lat = geo["result"]["latitude"]
        lng = geo["result"]["longitude"]
        area_name = geo["result"]["admin_district"]

        df_area = df.copy()
        df_area["distance_miles"] = df_area.apply(
            lambda row: haversine(lat, lng, row["lat"], row["lng"]), axis=1
        )
        df_area = df_area[df_area["distance_miles"] <= area_radius].sort_values("distance_miles")

        st.success(f"Found **{len(df_area)} food bank locations** within {area_radius} miles of {area_name}")

        a1, a2, a3 = st.columns(3)
        a1.metric("Total Locations", len(df_area))
        a2.metric("Require Referral (Trussell)", len(df_area[df_area["network"]=="Trussell"]))
        a3.metric("Walk-in Welcome", len(df_area[df_area["network"]!="Trussell"]))

        # Coverage gap warning
        if len(df_area) < 5:
            st.error(
                f"⚠️ **Coverage Gap Detected:** Only {len(df_area)} food banks within "
                f"{area_radius} miles of {area_name}. "
                "This area may be underserved. Consider flagging to your local council."
            )
        elif len(df_area[df_area["network"]!="Trussell"]) == 0:
            st.warning(
                "⚠️ **No walk-in food banks in this area.** "
                "All nearby food banks require a referral — this creates a barrier "
                "for people in immediate crisis."
            )

        # Map
        import folium
        from streamlit_folium import st_folium

        m = folium.Map(location=[lat, lng], zoom_start=11)
        folium.Marker(
            [lat, lng],
            popup=f"📍 {area_name}",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)

        for _, fb in df_area.iterrows():
            pin_color = "green" if fb["network"] == "Trussell" else "blue"
            folium.Marker(
                [fb["lat"], fb["lng"]],
                popup=f"<b>{fb['name']}</b><br>{fb['address']}<br>{fb['network']}",
                tooltip=fb["name"],
                icon=folium.Icon(color=pin_color, icon="info-sign")
            ).add_to(m)

        st_folium(m, width=None, height=450, use_container_width=True)

        # District breakdown
        st.markdown("#### Food Banks by District")
        district_counts = df_area["district"].value_counts().reset_index()
        district_counts.columns = ["District","Count"]
        fig2 = px.bar(district_counts.head(15), x="District", y="Count",
                      title="Food Bank Locations by District")
        st.plotly_chart(fig2, use_container_width=True)

        # Full table
        st.markdown("#### Full List")
        show_df = df_area[["name","address","postcode","network","distance_miles"]].copy()
        show_df["distance_miles"] = show_df["distance_miles"].round(1)
        show_df.columns = ["Name","Address","Postcode","Network","Distance (miles)"]
        st.dataframe(show_df, use_container_width=True, hide_index=True)

        # Download
        csv = show_df.to_csv(index=False)
        st.download_button(
            "📥 Download area report as CSV",
            data=csv,
            file_name=f"foodbanks_{area_name.replace(' ','_')}.csv",
            mime="text/csv"
        )
    else:
        st.error("Postcode not found.")

st.divider()
st.caption("CrisisConnect UK | Data from Give Food API | Built by Shikha Agarwal")