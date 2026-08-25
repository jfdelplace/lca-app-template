"""My Emissions App — one sentence on what this app answers.

This is the file you edit. Everything else in this project exists so you don't have to
think about HTTP, containers, or deployment.

Start by changing APP_NAME and APP_DESCRIPTION below, then replace the analysis at the
bottom with your own.
"""

import streamlit as st

import platform_client

APP_NAME = "My Emissions App"
APP_DESCRIPTION = "One sentence on what this app answers."

st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(APP_NAME)
st.caption(APP_DESCRIPTION)

try:
    data = platform_client.load()
except platform_client.PlatformError as error:
    # Anything that goes wrong reaching the platform is reported as a sentence, never as
    # a stack trace: whoever is looking at this app cannot act on a traceback.
    st.error(str(error))
    st.stop()

# Stating the data version makes any figure you publish traceable to the numbers behind it.
st.caption(f"Data version {data.version}")

# --- Your analysis starts here -------------------------------------------------------
#
# Two dataframes are available:
#
#   data.vehicle_parameters   one row per vehicle, keyed by (size, fuel, scenario).
#                             Numeric columns: vehicle_mass, battery_capacity,
#                             battery_mass, wtt, phev_wtt, fuel_cell, road,
#                             road_maintenance, maintenance, tyre_wear, brake_wear.
#                             Tank-to-wheel values are ttw_<indicator>, e.g.
#                             ttw_climate_change. Nulls there are correct for vehicles
#                             with no tailpipe emissions.
#
#   data.emission_factors     one row per named factor, keyed by `index`, with all 16
#                             indicators as columns. Look one up with
#                             data.factor("petrol production", "climate_change").
#
# Only vehicles that actually exist are published, so no filtering is needed.

vehicles = data.vehicle_parameters

left, right = st.columns(2)
with left:
    size = st.selectbox("Size", sorted(vehicles["size"].unique()))
with right:
    fuel = st.selectbox("Fuel", sorted(vehicles["fuel"].unique()))

selection = vehicles[(vehicles["size"] == size) & (vehicles["fuel"] == fuel)]

if selection.empty:
    st.info("That combination is not in the data.")
else:
    st.subheader("Vehicle parameters")
    st.dataframe(selection, use_container_width=True)

    st.subheader("Emission factors")
    st.dataframe(data.emission_factors, use_container_width=True)
