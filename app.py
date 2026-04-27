import streamlit as st
import pandas as pd
from datetime import date
import os

# App Configuration
st.set_page_config(page_title="Gas Tracker", layout="wide")

# File Management
DATA_FILE = "gas_data.csv"
VEHICLE_FILE = "vehicles.csv"

def load_data():
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
            try:
                df = pd.read_csv(DATA_FILE)
                # Standardize column names
                df = df.rename(columns={"Total_Cost": "Total", "Price_per_L": "Price"})
                cols = ["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price", "Total"]
                for c in cols:
                    if c not in df.columns:
                        df[c] = 0 if c in ["Odometer", "Liters", "Price", "Total"] else ""
                st.session_state.gas_data = df
            except:
                st.session_state.gas_data = pd.DataFrame(columns=["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price", "Total"])
        else:
            st.session_state.gas_data = pd.DataFrame(columns=["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price", "Total"])

def save_data():
    st.session_state.gas_data.to_csv(DATA_FILE, index=False)
    pd.DataFrame(st.session_state.vehicles, columns=["Vehicle"]).to_csv(VEHICLE_FILE, index=False)

load_data()

st.title("⛽ Gas Tracker")

# --- SIDEBAR ---
st.sidebar.header("🛠️ Management")

with st.sidebar.form("v_form", clear_on_submit=True):
    new_v = st.text_input("Add Vehicle")
    if st.form_submit_button("Add") and new_v:
        if new_v not in st.session_state.vehicles:
            st.session_state.vehicles.append(new_v)
            save_data()
            st.rerun()

if st.session_state.vehicles:
    del_v = st.sidebar.selectbox("Remove Vehicle", st.session_state.vehicles)
    if st.sidebar.button("Delete Selected"):
        st.session_state.vehicles.remove(del_v)
        st.session_state.gas_data = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != del_v]
        save_data()
        st.rerun()

st.sidebar.markdown("---")
edit_mode = st.sidebar.toggle("📝 Edit Mode")

if st.session_state.vehicles and not edit_mode:
    st.sidebar.header("⛽ Log Gas")
    v_sel = st.sidebar.selectbox("Vehicle", st.session_state.vehicles)
    grd = st.sidebar.selectbox("Grade", ["Regular", "Plus", "Premium", "Diesel"])
    
    with st.sidebar.form("log_form", clear_on_submit=True):
        dt = st.date_input("Date", date.today())
        km = st.number_input("Odometer", min_value=0.0)
        lt = st.number_input("Liters", min_value=0.0)
        pr = st.number_input("Price/L", min_value=0.0, format="%.3f")
        
        if st.form_submit_button("Save"):
            if pr > 0 and lt > 0:
                tot = round(lt * pr, 2)
                row = pd.DataFrame([{"Vehicle": v_sel, "Date": str(dt), "Grade": grd, "Odometer": km, "Liters": lt, "Price": pr, "Total": tot}])
                st.session_state.gas_data = pd.concat([st.session_state.gas_data, row], ignore_index=True)
                save_data()
                st.rerun()
            else:
                st.error("Enter Price & Liters")

# --- MAIN DASHBOARD ---
if not st.session_state.gas_data.empty:
    view = st.selectbox("Filter", ["All"] + st.session_state.vehicles)
    df = st.session_state.gas_data if view == "All" else st.session_state.gas_data[st.session_state.gas_data["Vehicle"] == view]
    
    st.metric("Total Spent", f"${pd.to_numeric(df['Total']).sum():.2f}")
    
    if edit_mode:
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Apply Changes"):
            edited["Total"] = (pd.to_numeric(edited["Liters"]) * pd.to_numeric(edited["Price"])).round(2)
            st.session_state.gas_data = edited if view == "All" else pd.concat([st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != view], edited])
            save_data()
            st.rerun()
    else:
        st.dataframe(df, use_container_width=True)
else:
    st.info("Garage is empty.")
