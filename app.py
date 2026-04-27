import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gas Tracker", layout="wide")

st.title("🚗 Gas Tracker & Garage Hub")

# --- INITIALIZE DATA ---
if 'vehicles' not in st.session_state:
    st.session_state.vehicles = ["2012 GMC Terrain", "2018 Hyundai Kona"]

if 'gas_data' not in st.session_state:
    st.session_state.gas_data = pd.DataFrame(columns=[
        "Vehicle", "Date", "Odometer", "Liters", "Price_per_L", "Total_Cost", "Efficiency"
    ])

# --- SIDEBAR: GARAGE MANAGEMENT ---
st.sidebar.header("🛠️ Manage Garage")

# Add a vehicle
new_vehicle = st.sidebar.text_input("Add New Vehicle")
if st.sidebar.button("Add to Garage"):
    if new_vehicle and new_vehicle not in st.session_state.vehicles:
        st.session_state.vehicles.append(new_vehicle)
        st.rerun()

# Remove a vehicle
vehicle_to_remove = st.sidebar.selectbox("Remove a Vehicle", st.session_state.vehicles)
if st.sidebar.button("Remove Selected"):
    if len(st.session_state.vehicles) > 1:
        st.session_state.vehicles.remove(vehicle_to_remove)
        st.rerun()
    else:
        st.sidebar.error("You need at least one vehicle!")

st.sidebar.markdown("---")

# --- SIDEBAR: LOG GAS ---
st.sidebar.header("⛽ Log Fill-up")
selected_v = st.sidebar.selectbox("Select Vehicle", st.session_state.vehicles)

with st.sidebar.form("input_form", clear_on_submit=True):
    fill_date = st.date_input("Date", date.today())
    odometer = st.number_input("Odometer (km)", min_value=0)
    liters = st.number_input("Liters (L)", min_value=0.0)
    price = st.number_input("Price/L ($)", min_value=0.0, format="%.3f")
    submit = st.form_submit_button("Save Entry")

if submit:
    # Logic to calculate efficiency for the SPECIFIC vehicle
    v_data = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] == selected_v]
    eff = 0.0
    if not v_data.empty:
        prev_odo = v_data["Odometer"].iloc[-1]
        dist = odometer - prev_odo
        if dist > 0:
            eff = round((liters / dist) * 100, 2)
    
    new_row = {
        "Vehicle": selected_v, "Date": fill_date, "Odometer": odometer,
        "Liters": liters, "Price_per_L": price, 
        "Total_Cost": round(liters * price, 2), "Efficiency": eff
    }
    st.session_state.gas_data = pd.concat([st.session_state.gas_data, pd.DataFrame([new_row])], ignore_index=True)
    st.success(f"Logged for {selected_v}!")

# --- MAIN DASHBOARD ---
# Filter view by vehicle
view_v = st.selectbox("View Stats For:", ["All"] + st.session_state.vehicles)

display_df = st.session_state.gas_data
if view_v != "All":
    display_df = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] == view_v]

if not display_df.empty:
    c1, c2 = st.columns(2)
    c1.metric("Total Spent", f"${display_df['Total_Cost'].sum():.2f}")
    c2.metric("Avg Efficiency", f"{display_df[display_df['Efficiency']>0]['Efficiency'].mean():.2f} L/100km")
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No data for this selection.")
