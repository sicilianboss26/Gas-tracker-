import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gas Tracker", layout="wide")

st.title("🚗 Gas Tracker")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Add New Fill-up")
with st.sidebar.form("input_form", clear_on_submit=True):
    fill_date = st.date_input("Date", date.today())
    odometer = st.number_input("Odometer Reading (km)", min_value=0, step=1)
    liters = st.number_input("Liters Filled (L)", min_value=0.0, step=0.1)
    price_per_l = st.number_input("Price per Liter ($)", min_value=0.0, step=0.001, format="%.3f")
    
    submit = st.form_submit_button("Log Fill-up")

# --- DATA PROCESSING ---
# In a full version, we would load from a CSV or Database
if 'gas_data' not in st.session_state:
    st.session_state.gas_data = pd.DataFrame(columns=[
        "Date", "Odometer", "Liters", "Price_per_L", "Total_Cost", "Efficiency"
    ])

if submit:
    total_cost = liters * price_per_l
    
    # Calculate efficiency based on previous entry
    efficiency = 0.0
    if not st.session_state.gas_data.empty:
        prev_odo = st.session_state.gas_data["Odometer"].iloc[-1]
        distance = odometer - prev_odo
        if distance > 0:
            efficiency = (liters / distance) * 100
    
    new_entry = {
        "Date": fill_date,
        "Odometer": odometer,
        "Liters": liters,
        "Price_per_L": price_per_l,
        "Total_Cost": total_cost,
        "Efficiency": round(efficiency, 2)
    }
    
    st.session_state.gas_data = pd.concat([st.session_state.gas_data, pd.DataFrame([new_entry])], ignore_index=True)
    st.success("Entry logged successfully!")

# --- DASHBOARD ---
if not st.session_state.gas_data.empty:
    col1, col2, col3 = st.columns(3)
    avg_eff = st.session_state.gas_data[st.session_state.gas_data["Efficiency"] > 0]["Efficiency"].mean()
    
    col1.metric("Avg Efficiency", f"{avg_eff:.2f} L/100km")
    col2.metric("Total Spent", f"${st.session_state.gas_data['Total_Cost'].sum():.2f}")
    col3.metric("Last Odometer", f"{st.session_state.gas_data['Odometer'].iloc[-1]} km")

    st.dataframe(st.session_state.gas_data, use_container_width=True)
else:
    st.info("No data logged yet. Use the sidebar to add your first fill-up.")
