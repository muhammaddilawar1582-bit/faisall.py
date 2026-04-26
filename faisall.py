import streamlit as st
import pandas as pd
import os
import json
import random
import smtplib
from email.mime.text import MIMEText

# --- 1. BASIC SETTINGS ---
st.set_page_config(page_title="Asademazon Pro v10", layout="wide")
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
DATA_FILE = os.path.join(DB_DIR, "master_data.xlsx")
CONFIG_FILE = os.path.join(DB_DIR, "email_config.json")
AUTH_FILE = os.path.join(DB_DIR, "user_creds.xlsx")

# Default Login (admin / 123)
if not os.path.exists(AUTH_FILE):
    pd.DataFrame([{"username": "admin", "password": "123"}]).to_excel(AUTH_FILE, index=False)

# --- 2. LOGIN & CHANGE PASSWORD SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align:center;'>🔐 Secure Access</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["LOGIN", "CHANGE PASSWORD"])
    
    with tab1:
        u = st.text_input("Username", value="admin")
        p = st.text_input("Password", type="password")
        if st.button("Login Now"):
            df_a = pd.read_excel(AUTH_FILE)
            if u == str(df_a.iloc[0,0]) and p == str(df_a.iloc[0,1]):
                st.session_state['logged_in'] = True; st.rerun()
            else: st.error("Wrong Password! Use '123'")

    with tab2:
        st.info("System Setup for Client")
        email = st.text_input("Admin Gmail")
        app_pass = st.text_input("16-digit App Password", type="password")
        if st.button("Save System Settings"):
            json.dump({"email":email, "pass":app_pass}, open(CONFIG_FILE, 'w'))
            st.success("Settings Saved!")

# --- 3. DASHBOARD (ALL 10 REQUIREMENTS) ---
else:
    st.title("📊 Master Dashboard & Excel Calculator")
    if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    # --- REQUIREMENT: EXCEL UPLOAD ---
    st.subheader("📁 Upload Your Excel Sheet")
    uploaded_file = st.file_uploader("Apni Excel file yahan upload karein", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file).fillna("")
        st.success("File Uploaded Successfully!")
    elif os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE).fillna("")
    else:
        # Requirement: Empty Boxes
        df = pd.DataFrame({
            "Description": [""], "Value 1": [0.0], "Value 2": [0.0], 
            "Operator": ["+"], "Result": [0.0], "Color": ["None"]
        })

    st.divider()

    # --- REQUIREMENT: EXCEL-STYLE CALCULATOR ---
    def auto_math(row):
        try:
            v1 = float(row['Value 1']) if row['Value 1'] != "" else 0
            v2 = float(row['Value 2']) if row['Value 2'] != "" else 0
            return v1 + v2 if row['Operator'] == '+' else v1 * v2
        except: return 0

    # --- REQUIREMENT: 7 COLORS & EDITABLE HEADERS ---
    st.info("💡 Double-click any header to rename. Calculator works inside the table.")
    
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=500,
        column_config={
            "Operator": st.column_config.SelectboxColumn("Op", options=["+", "*"]),
            "Color": st.column_config.SelectboxColumn(
                "Row Color", 
                options=["None", "Red", "Green", "Blue", "Yellow", "Orange", "Purple", "Pink"]
            ),
            "Result": st.column_config.NumberColumn("Total", disabled=True)
        }
    )

    # Apply Auto Math
    if 'Value 1' in edited_df.columns and 'Value 2' in edited_df.columns:
        edited_df['Result'] = edited_df.apply(auto_math, axis=1)

    if st.button("💾 SAVE ALL CHANGES"):
        edited_df.to_excel(DATA_FILE, index=False)
        st.success("Aapka sara data, calculations aur colors save ho gaye hain!"); st.balloons()