import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gas Tracker", layout="wide")

st.title("🚗 Gas Tracker & Garage Hub")

# --- INITIALIZE DATA ---
if 'vehicles' not in st.session_state:
    st.session_state.vehicles = []

if 'gas_data' not in st.session_state:
    st.session_state.gas_data = pd.DataFrame(columns=[
        "Vehicle", "Date", "Odometer", "Liters", "Price_per_L", "Total_Cost", "Efficiency"
    ])

# --- SIDEBAR: GARAGE MANAGEMENT ---
st.sidebar.header("🛠️ Manage Garage")

# We use a form for the vehicle entry to handle the "Auto-Erase" safely
with st.sidebar.form("vehicle_form", clear_on_submit=True):
    vehicle_name = st.text_input("Add New Vehicle", placeholder="Year Make Model")
    add_btn = st.form_submit_button("Add to Garage")
    
    if add_btn:
        if vehicle_name and vehicle_name not in st.session_state.vehicles:
            st.session_state.vehicles.append(vehicle_name)
            st.rerun()

# Remove a vehicle logic
if st.session_state.vehicles:
    vehicle_to_remove = st.sidebar.selectbox("Remove a Vehicle", st.session_state.vehicles)
    if st.sidebar.button("Remove Selected"):
        st.session_state.vehicles.remove(vehicle_to_remove)
        st.session_state.gas_data = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != vehicle_to_remove]
        st.rerun()

st.sidebar.markdown("---")

# --- SIDEBAR: LOG GAS ---
if st.session_state.vehicles:
    st.sidebar.header("⛽ Log Fill-up")
    selected_v = st.sidebar.selectbox("Select Vehicle", st.session_state.vehicles)

    with st.sidebar.form("input_form", clear_on_submit=True):
        fill_date = st.date_input("Date", date.today())
        odometer = st.number_input("Odometer (km)", min_value=0)
        liters = st.number_input("Liters (L)", min_value=0.0)
        price = st.number_input("Price/L ($)", min_value=0.0, format="%.3f")
        submit = st.form_submit_button("Save Entry")

    if submit:
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
            "Total_Cost": round(lit
