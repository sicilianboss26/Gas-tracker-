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
            st.session_state.vehicles = pd.read_csv(VEHICLE_FILE)["Vehicle"].tolist()
        else:
            st.session_state.vehicles = []
            
    if 'gas_data' not in st.session_state:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            # Ensure columns are numeric
            for col in ["Odometer", "Liters", "Price_per_L", "Total_Cost"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            st.session_state.gas_data = df
        else:
            st.session_state.gas_data = pd.DataFrame(columns=["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price_per_L", "Total_Cost"])

def save_all():
    st.session_state.gas_data.to_csv(DATA_FILE, index=False)
    pd.DataFrame(st.session_state.vehicles, columns=["Vehicle"]).to_csv(VEHICLE_FILE, index=False)

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
        odo = st.number_input("Odometer (km)", min_value=0.0, step=1.0)
        lits = st.number_input("Liters (L)", min_value=0.0, step=0.01)
        prc = st.number_input("Price/L ($)", min_value=0.0, format="%.3f", step=0.001)
        if st.form_submit_button("Save Entry"):
            cost = round(lits * prc, 2)
            new_row = pd.DataFrame([{"Vehicle": sel_v, "Date": str(d), "Grade": grade, "Odometer": odo, "Liters": lits, "Price_per_L": prc, "Total_Cost": cost}])
            st.session_state.gas_data = pd.concat([st.session_state.gas_data, new_row], ignore_index=True)
            save_all()
            st.rerun()

# --- MAIN VIEW ---
if not st.session_state.gas_data.empty:
    view_v = st.selectbox("View Stats For:", ["All"] + st.session_state.vehicles)
    df_view = st.session_state.gas_data if view_v == "All" else st.session_state.gas_data[st.session_state.gas_data["Vehicle"] == view_v]

    # Calculate Total
    total = pd.to_numeric(df_view["Total_Cost"], errors='coerce').sum()
    st.metric("Total Spent", f"${total:.2f}")

    if edit_mode:
        edited = st.data_editor(df_view, num_rows="dynamic", use_container_width=True)
        if st.button("Save Changes"):
            edited["Total_Cost"] = round(edited["Liters"] * edited["Price_per_L"], 2)
            if view_v == "All":
                st.session_state.gas_data = edited
            else:
                other = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != view_v]
                st.session_state.gas_data = pd.concat([other, edited], ignore_index=True)
            save_all()
            st.rerun()
    else:
        st.dataframe(df_view, use_container_width=True)
else:
    st.info("No data logged yet.")
