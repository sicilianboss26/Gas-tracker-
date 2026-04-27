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
        "Vehicle", "Date", "Odometer", "Liters", "Price_per_L", "Total_Cost"
    ])

# --- SIDEBAR: GARAGE MANAGEMENT ---
st.sidebar.header("🛠️ Manage Garage")

with st.sidebar.form("vehicle_form", clear_on_submit=True):
    vehicle_name = st.text_input("Add New Vehicle", placeholder="Year Make Model")
    add_btn = st.form_submit_button("Add to Garage")
    
    if add_btn:
        if vehicle_name and vehicle_name not in st.session_state.vehicles:
            st.session_state.vehicles.append(vehicle_name)
            st.rerun()

if st.session_state.vehicles:
    vehicle_to_remove = st.sidebar.selectbox("Remove a Vehicle", st.session_state.vehicles)
    if st.sidebar.button("Remove Selected"):
        st.session_state.vehicles.remove(vehicle_to_remove)
        st.session_state.gas_data = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != vehicle_to_remove]
        st.rerun()

st.sidebar.markdown("---")

# --- SIDEBAR: EDIT MODE TOGGLE ---
edit_mode = st.sidebar.toggle("📝 Enable Edit Mode")

st.sidebar.markdown("---")

# --- SIDEBAR: LOG GAS ---
if st.session_state.vehicles and not edit_mode:
    st.sidebar.header("⛽ Log Fill-up")
    selected_v = st.sidebar.selectbox("Select Vehicle", st.session_state.vehicles)

    with st.sidebar.form("input_form", clear_on_submit=True):
