import streamlit as st
import pandas as pd
import math

# --- Page config ---
st.set_page_config(
    page_title="Capiz Lantern Shipping Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Capiz Lantern Shipping Calculator – Dynamic, Colorful & Visual")

# --- Sidebar for Inputs ---
st.sidebar.header("Shipping Scenario Inputs")

exchange_rate_cad_php = st.sidebar.number_input("Exchange Rate (1 CAD → PHP)", min_value=0.0, value=42.0)
freight_usd = st.sidebar.number_input("Sea Freight Amount (USD)", min_value=0.0, value=769.0)
freight_cbm = st.sidebar.number_input("Freight Covers How Many CBM?", min_value=0.1, value=5.0)
container_cbm = st.sidebar.number_input("Container Volume (CBM)", min_value=0.1, value=5.0)

length_in = st.sidebar.number_input("Lantern Length (inches)", min_value=0.1, value=10.0)
width_in = st.sidebar.number_input("Lantern Width (inches)", min_value=0.1, value=25.0)
height_in = st.sidebar.number_input("Lantern Height (inches)", min_value=0.1, value=25.0)
quantity = st.sidebar.number_input("Number of Lanterns to Ship", min_value=1, value=3, step=1)

# --- Initialize history ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Formatting functions ---
def money_usd(amount):
    return f"${amount:,.2f} USD"

def money_php(amount):
    return f"₱{amount:,.2f}"

# --- Calculations ---
cbm_per_lantern = (length_in * width_in * height_in) / 61023
total_cbm_needed = cbm_per_lantern * quantity
freight_per_cbm = freight_usd / freight_cbm
freight_per_lantern_usd = cbm_per_lantern * freight_per_cbm
freight_per_lantern_php = freight_per_lantern_usd * exchange_rate_cad_php
total_freight_usd = freight_per_cbm * total_cbm_needed
total_freight_php = total_freight_usd * exchange_rate_cad_php
lanterns_per_container = int(container_cbm / cbm_per_lantern)
full_containers = quantity // lanterns_per_container
leftover_lanterns = quantity % lanterns_per_container

warning_msg = ""
if quantity > lanterns_per_container:
    warning_msg = f"⚠️ Quantity exceeds single container capacity! You need {full_containers} full container(s) + {leftover_lanterns} lantern(s) leftover."

# --- Main Display ---
st.header("Scenario Overview")
st.markdown(f"""
**Exchange rate:** $1 CAD = {money_php(exchange_rate_cad_php)}  
**Sea freight:** {money_usd(freight_usd)} per {freight_cbm} CBM  
**Lantern dimensions:** {height_in}h × {width_in}w × {length_in}l inches  
**Quantity:** {quantity}  

**CBM per lantern:** {cbm_per_lantern:.4f} CBM  
**Total CBM:** {total_cbm_needed:.4f} CBM  

**Freight per CBM:** {money_usd(freight_per_cbm)} ≈ {money_php(freight_per_cbm * exchange_rate_cad_php)}  
**Freight per lantern:** {money_usd(freight_per_lantern_usd)} ≈ {money_php(freight_per_lantern_php)}  
**Total freight:** {money_usd(total_freight_usd)} ≈ {money_php(total_freight_php)}  

**Lanterns per container:** {lanterns_per_container}  
{warning_msg}
""")

# --- Save Scenario ---
if st.button("Save This Scenario"):
    result = {
        "Length (in)": length_in,
        "Width (in)": width_in,
        "Height (in)": height_in,
        "CBM/Lantern": round(cbm_per_lantern, 4),
        "Quantity": quantity,
        "Total CBM": round(total_cbm_needed, 4),
        "Freight/Lantern (PHP)": money_php(freight_per_lantern_php),
        "Freight/Lantern (CAD)": money_usd(freight_per_lantern_usd),
        "Total Freight (PHP)": money_php(total_freight_php),
        "Total Freight (CAD)": money_usd(total_freight_usd)
    }
    st.session_state.history.append(result)
    if len(st.session_state.history) > 5:
        st.session_state.history.pop(0)
    st.success("Scenario saved!")

# --- History Table ---
if st.session_state.history:
    st.header("Last 5 Saved Scenarios")
    df = pd.DataFrame(st.session_state.history)

    def color_money(val):
        if "₱" in str(val) or "$" in str(val):
            return 'background-color: #d4edda; color: #155724; font-weight: bold'
        return ''

    def highlight_quantity(val):
        if isinstance(val, int) and val > 1:
            return 'background-color: #cce5ff; color: #004085; font-weight: bold'
        return ''

    styled_df = df.style.applymap(color_money, subset=["Freight/Lantern (PHP)", "Freight/Lantern (CAD)",
                                                       "Total Freight (PHP)", "Total Freight (CAD)"]) \
                        .applymap(highlight_quantity, subset=["Quantity"]) \
                        .set_properties(**{'text-align': 'center'}) \
                        .set_table_styles([
                            {'selector': 'th', 'props': [('background-color', '#343a40'),
                                                         ('color', 'white'),
                                                         ('text-align', 'center')]}
                        ])
    
    st.dataframe(styled_df, height=300)

# --- Container Fill Chart ---
st.header("Container Fill Visualization")
st.markdown("Shows container fill vs leftover lanterns")
fill_percent = min(quantity / lanterns_per_container, 1.0) * 100
leftover = max(quantity - lanterns_per_container, 0)
st.bar_chart(pd.DataFrame({
    "Container Fill (%)": [fill_percent],
    "Leftover Lanterns": [leftover]
}))

# --- Cheat Sheet ---
st.header("Quick Shipping Formula (Cheat Sheet)")
st.markdown("""
1. CBM per lantern: `(length_in × width_in × height_in) / 61,023`  
2. Total CBM = `CBM per lantern × quantity`  
3. Freight per CBM (USD): `freight_usd / freight_cbm`  
4. Freight per lantern (USD): `CBM_per_lantern × freight_per_CBM`  
5. Total freight (USD): `CBM_total × freight_per_CBM`  
6. Freight in PHP: `freight_usd × exchange_rate`  
7. Lanterns per container: `container_cbm / CBM_per_lantern`  
8. If quantity > container capacity, calculate full containers + leftover lanterns.
""")
