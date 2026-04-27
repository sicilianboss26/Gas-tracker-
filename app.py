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
            
            # Migration Logic: Rename old columns if they exist
            rename_map = {"Total_Cost": "Total", "Price_per_L": "Price"}
            df = df.rename(columns=rename_map)
            
            # Ensure all required columns exist
            required_cols = ["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price", "Total"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 0 if col in ["Odometer", "Liters", "Price", "Total"] else ""

            # Ensure columns are numeric
            for col in ["Odometer", "Liters",
