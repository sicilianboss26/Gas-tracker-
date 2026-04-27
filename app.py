import streamlit as st
import pandas as pd
from datetime import date
import os

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

# Logic to handle auto-erasing the input box
if "v_input" not in st.session_state:
    st.session_state.v_input = ""

def clear_text():
    st.session_state.v_input = st.session_state.widget_input
    st.session_state.widget_input = ""

# Add a vehicle with the "Year Make Model" placeholder
new_vehicle = st.sidebar.text_input(
    "Add New Vehicle", 
    placeholder="Year Make Model", 
    key="widget_input", 
    on_change=None
)

if st.sidebar.button("Add to Garage"):
    if st.session_state.widget_input:
        vehicle_name = st.session_state.widget_input
        if vehicle_name not in st.session_state.vehicles:
            st.session_state.vehicles.append(vehicle_name)
            # This clears the text box by resetting the widget state
            st.session_state.widget_input = ""
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
        # Calculate efficiency based on last entry for THIS specific vehicle
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
else:
    st.sidebar.info("Add a vehicle above to start logging gas.")

# --- DATA BACKUP SECTION ---
st.sidebar.markdown("---")
st.sidebar.header("💾 Backup Data")
if st.sidebar.button("Download Data as CSV"):
    csv = st.session_state.gas_data.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Confirm Download",
        data=csv,
        file_name='gas_tracker_backup.csv',
        mime='text/csv',
    )

# --- MAIN DASHBOARD ---
if not st.session_state.gas_data.empty:
    view_v = st.selectbox("View Stats For:", ["All"] + st.session_state.vehicles)
    
    display_df = st.session_state.gas_data
    if view_v != "All":
        display_df = st.session_state.gas_data[st.session_state.gas_data["Vehicle"] == view_v]

    col1, col2 = st.columns(2)
    col1.metric("Total Spent", f"${display_df['Total_Cost'].sum():.2f}")
    
    valid_eff = display_df[display_df["Efficiency"] > 0]["Efficiency"]
    avg_eff = valid_eff.mean() if not valid_eff.empty else 0.0
    col2.metric("Avg Efficiency", f"{avg_eff:.2f} L/100km")
    
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("Your garage is empty or no gas has been logged yet.")
