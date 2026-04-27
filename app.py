import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Gas Tracker", layout="wide")

# --- FILE PATHS FOR PERSISTENCE ---
DATA_FILE = "gas_data.csv"
VEHICLE_FILE = "vehicles.csv"

# --- HELPER FUNCTIONS ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Safety Fix: Force numeric types so math works
            df["Liters"] = pd.to_numeric(df["Liters"], errors='coerce')
            df["Price_per_L"] = pd.to_numeric(df["Price_per_L"], errors='coerce')
            df["Total_Cost"] = pd.to_numeric(df["Total_Cost"], errors='coerce')
            return df
        except:
            pass
    return pd.DataFrame(columns=["Vehicle", "Date", "Grade", "Odometer", "Liters", "Price_per_L", "Total_Cost"])

def load_vehicles():
    if os.path.exists(VEHICLE_FILE):
        try:
            return pd.read_csv(VEHICLE_FILE)["Vehicle"].tolist()
        except:
            pass
    return []

def save_all():
    st.session_state.gas_data.to_csv(DATA_FILE, index=False)
    pd.DataFrame(st.session_state.vehicles, columns=["Vehicle"]).to_csv(VEHICLE_FILE, index=False)

# --- INITIALIZE DATA ---
if 'vehicles' not in st.session_state:
    st.session_state.vehicles = load_vehicles()

if 'gas_data' not in st.session_state:
    st.session_state.gas_data = load_data()

st.title("⛽ Gas Tracker")

# --- SIDEBAR: GARAGE MANAGEMENT ---
st.sidebar.header("🛠️ Manage Garage")

with st.sidebar.form("vehicle_form", clear_on_submit=True):
    vehicle_name = st.text_input("Add New Vehicle", placeholder="Year Make Model")
    add_btn = st.form_submit_button("Add to Garage")
    
    if add_btn:
        if vehicle_name and vehicle_name not in st.session_state.vehicles:
            st.session_state.vehicles.append(vehicle_name)
            save_all()
            st.rerun()

if st.session_state.vehicles:
    vehicle_to_remove = st.sidebar.selectbox("Remove a Vehicle", st.session_state.vehicles)
    if st.sidebar.button("Remove Selected"):
        st.session_state.vehicles.remove(vehicle_to_remove)
        st.session_state.gas_data = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != vehicle_to_remove]
        save_all()
        st.rerun()

st.sidebar.markdown("---")

# --- SIDEBAR: EDIT MODE ---
edit_mode = st.sidebar.toggle("📝 Enable Edit Mode")

st.sidebar.markdown("---")

# --- SIDEBAR: LOG GAS ---
if st.session_state.vehicles and not edit_mode:
    st.sidebar.header("⛽ Log Fill-up")
    selected_v = st.sidebar.selectbox("Select Vehicle", st.session_state.vehicles)
    gas_grade = st.sidebar.selectbox("Gas Grade", ["Regular (87)", "Plus (89)", "Premium (91)", "Ultra (93/94)", "Diesel"])

    with st.sidebar.form("input_form", clear_on_submit=True):
        fill_date = st.date_input("Date", date.today())
        odometer = st.number_input("Odometer (km)", min_value=0.0, step=1.0)
        liters = st.number_input("Liters (L)", min_value=0.0, step=0.1)
        price = st.number_input("Price/L ($)", min_value=0.0, format="%.3f", step=0.001)
        submit = st.form_submit_button("Save Entry")

        if submit:
            # Force calculation to be precise
            calc_total = round(float(liters) * float(price), 2)
            
            new_row = {
                "Vehicle": selected_v, 
                "Date": str(fill_date), 
                "Grade": gas_grade,
                "Odometer": odometer,
                "Liters": liters, 
                "Price_per_L": price, 
                "Total_Cost": calc_total
            }
            st.session_state.gas_data = pd.concat([st.session_state.gas_data, pd.DataFrame([new_row])], ignore_index=True)
            save_all()
            st.success(f"Logged ${calc_total} for {selected_v}!")

elif edit_mode:
    st.sidebar.info("Edit Mode active.")
else:
    st.sidebar.info("Add a vehicle to start logging.")

# --- MAIN DASHBOARD ---
if not st.session_state.gas_data.empty:
    view_v = st.selectbox("View Stats For:", ["All"] + st.session_state.vehicles)
    
    display_df = st.session_state.gas_data.copy()
    if view_v != "All":
        display_df = display_df[display_df["Vehicle"] == view_v]

    # Force Total_Cost to be numeric for the sum metric
    total_sum = pd.to_numeric(display_df['Total_Cost'], errors='coerce').sum()
    st.metric("Total Spent", f"${total_sum:.2f}")
    
    if edit_mode:
        edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Changes"):
            # Recalculate Total_Cost in case Liters or Price were edited manually
            edited_df["Total_Cost"] = round(edited_df["Liters"] * edited_df["Price_per_L"], 2)
            
            if view_v == "All":
                st.session_state.gas_data = edited_df
            else:
                other_v = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] != view_v]
                st.session_state.gas_data = pd.concat([other_v, edited_df], ignore_index=True)
            save_all()
            st.success("Changes Saved!")
            st.rerun()
    else:
        st.dataframe(display_df, use_container_width=True)
else:
    st.info("Garage empty or no logs yet.")
