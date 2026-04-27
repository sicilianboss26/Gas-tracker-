import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Gas Tracker", layout="wide")

# --- FILE PATHS ---
DATA_FILE = "gas_data.csv"
VEHICLE_FILE = "vehicles.csv"

# --- LOAD DATA ---
def load_all():
    if 'vehicles' not in st.session_state:
        if os.path.exists(VEHICLE_FILE):
            try:
                st.session_state.vehicles = pd.read_csv(VEHICLE_FILE)["Vehicle"].tolist()
            except:
                st.session_state.vehicles = []
        else:
            st.session_state.vehicles = []
            
    if 'gas_data' not in st.session_state:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            
            # --- MIGRATION LOGIC: Rename old columns if they exist ---
            rename_map = {
                "Total_Cost": "Total",
                "Price_per_L": "Price"
            }
            df = df.rename(columns=rename_map)
            
            # Ensure all required columns exist
            required_cols = ["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price", "Total"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 0 if col in ["Odometer", "Liters", "Price", "Total"] else ""

            # Ensure columns are numeric for math
            for col in ["Odometer", "Liters", "Price", "Total"]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
            st.session_state.gas_data = df
        else:
            st.session_state.gas_data = pd.DataFrame(columns=["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price", "Total"])

def save_all():
    st.session_state.gas_data.to_csv(DATA_FILE, index=False)
    pd.DataFrame(st.session_state.vehicles, columns=["Vehicle"]).to_csv(VEHICLE_FILE, index=False)

# Run the loader
load_all()

st.title("⛽ Gas Tracker")

# --- SIDEBAR ---
st.sidebar.header("🛠️ Manage Garage")

with st.sidebar.form("vehicle_form", clear_on_submit=True):
    v_name = st.text_input("Add New Vehicle", placeholder="Year Make Model")
    if st.form_submit_button("Add to Garage") and v_name:
        if v_name not in st.session_state.vehicles:
            st.session_state.vehicles.append(v_name)
            save_all()
            st.rerun()

if st.session_state.vehicles:
    v_del = st.sidebar.selectbox("Remove Vehicle", st.session_state.vehicles)
    if st.sidebar.button("Remove Selected"):
        st.session_state.vehicles.remove(v_del)
        st.session_state.gas_data = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != v_del]
        save_all()
        st.rerun()

st.sidebar.markdown("---")
edit_mode = st.sidebar.toggle("📝 Enable Edit Mode")

if st.session_state.vehicles and not edit_mode:
    st.sidebar.header("⛽ Log Fill-up")
    sel_v = st.sidebar.selectbox("Select Vehicle", st.session_state.vehicles)
    grade = st.sidebar.selectbox("Grade", ["Regular (87)", "Plus (89)", "Premium (91)", "Ultra (93/94)", "Diesel"])

    with st.sidebar.form("log_form", clear_on_submit=True):
        d = st.date_input("Date", date.today())
        odo = st.number_input("Odometer (km
