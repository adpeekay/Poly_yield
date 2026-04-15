# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 10:09:06 2026

@author: Martyn
"""

# app.py
import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from model import annual_yield

st.set_page_config(page_title="Thin‑Film PV Yield Calculator", layout="centered")

st.title("Thin‑Film Curved PV Annual Yield Calculator")
st.markdown(
    """
    **Model assumptions**
    - Flexible thin‑film (FLEX‑03‑class)
    - 2‑cell bypass + soft electrical decoupling
    - East–West tunnel ridge
    - Clear‑sky baseline  
    """
)

st.header("Site location")

st.header("Site location (click on the map)")

# Default map start (world view)
default_location = [20, 0]

m = folium.Map(
    location=default_location,
    zoom_start=2,
    control_scale=True,
)

# Allow click to place marker
m.add_child(folium.LatLngPopup())

map_data = st_folium(
    m,
    height=450,
    width=700,
)

# Extract clicked location
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
else:
    lat = 52.205
    lon = 0.1218

st.write(f"**Selected latitude:** {lat:.4f}")
st.write(f"**Selected longitude:** {lon:.4f}")

timezone = st.selectbox(
    "Timezone",
    [
        "UTC",
        "Europe/London",
        "Europe/Paris",
        "Africa/Lagos",
        "Asia/Bahrain",
        "Australia/Hobart",
        "America/New_York",
    ]
)


st.header("Geometry")

module_azimuth = st.selectbox(
    "Tunnel ridge orientation",
    options=[("East–West", 90), ("North–South", 0)],
    format_func=lambda x: x[0]
)[1]

max_cell_tilt = st.slider("Maximum curvature angle (degrees)", 30, 80, 60)
slope_ns = st.slider("North–South land slope (degrees)", 0.0, 10.0, 2.0)
no_panels = st.slider("number of panels", 1, 100, 10)

#st.header("Climate assumptions")

#temp_air = st.slider("Average daytime air temperature (°C)", -10.0, 45.0, 12.0)
#wind_speed = st.slider("Average wind speed (m/s)", 0.0, 10.0, 3.0)

#year = st.number_input("Simulation year", value=2024, step=1)

if st.button("Calculate annual yield"):

    with st.spinner("Running model…"):
        annual_kwh, kwh_per_kwp, daily_kwh = annual_yield(
            no_panels=no_panels,
            lat=lat,
            lon=lon,
            timezone=timezone,
            module_azimuth=module_azimuth,
            max_cell_tilt=max_cell_tilt,
            slope_ns=slope_ns,
            #temp_air=temp_air,
            #wind_speed=wind_speed,
            #year=year,
        )

    st.success("Calculation complete")

    st.metric("Annual energy", f"{annual_kwh:.1f} kWh")
    st.metric("Annual yield", f"{kwh_per_kwp:.0f} kWh/kWp")

    st.subheader("Daily energy profile")
    st.line_chart(daily_kwh)

    csv = daily_kwh.to_csv().encode("utf-8")
    st.download_button(
        "Download daily kWh (CSV)",
        csv,
        "daily_energy.csv",
        "text/csv",
    )
