import streamlit as st
import pandas as pd
import datetime
import hashlib
import os
import random
import string
import smtplib
from email.message import EmailMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Booking Safety Calculator",
    layout="wide"
)

# -------- REMOVE EXTRA TOP SPACE & SMALLER FONTS --------
st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; }
    .summary-box p { font-size: 12px; margin-bottom: 3px; }
    .summary-box h3 { font-size: 14px; margin-bottom: 5px; }
    .stSelectbox label, .stNumberInput label { font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- SESSION MANAGEMENT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "otp" not in st.session_state:
    st.session_state.otp = ""
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# ---------------- USER DATA ----------------
# Example users: username -> [hashed_password, email]
# Passwords hashed using sha256
users = {
    "jatin": [hashlib.sha256("Jatin@123".encode()).hexdigest(), "jatin@example.com"],
    "rahul": [hashlib.sha256("Rahul@123".encode()).hexdigest(), "rahul@example.com"]
}

LOG_FILE = "calculation_logs.csv"

# ---------------- FUNCTIONS ----------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def generate_otp():
    return "".join(random.choices(string.digits, k=6))

def send_otp_email(email, otp_code):
    # Configure your SMTP here (example Gmail)
    sender_email = "your_email@gmail.com"
    sender_pass = "your_email_app_password"
    msg = EmailMessage()
    msg.set_content(f"Your OTP for password change is: {otp_code}")
    msg['Subject'] = "Booking Calculator OTP Verification"
    msg['From'] = sender_email
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_pass)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"OTP sending failed: {e}")
        return False

def log_calculation(username, data_dict):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_dict["Username"] = username
    data_dict["Timestamp"] = timestamp
    df_new = pd.DataFrame([data_dict])
    if os.path.exists(LOG_FILE):
        df_existing = pd.read_csv(LOG_FILE)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_csv(LOG_FILE, index=False)

def show_logs():
    if os.path.exists(LOG_FILE):
        df_logs = pd.read_csv(LOG_FILE)
        st.subheader("📑 View Logs")
        users_filter = ["All"] + df_logs["Username"].unique().tolist()
        results_filter = ["All"] + df_logs["Result"].unique().tolist()
        suppliers_filter = ["All"] + df_logs["Supplier"].unique().tolist()
        flight_filter = ["All"] + df_logs["Flight Type"].unique().tolist()

        selected_user = st.selectbox("Filter by User", users_filter)
        selected_result = st.selectbox("Filter by Result", results_filter)
        selected_supplier = st.selectbox("Filter by Supplier", suppliers_filter)
        selected_flight = st.selectbox("Filter by Flight Type", flight_filter)
        start_date = st.date_input("Start Date", df_logs["Timestamp"].min().split(" ")[0])
        end_date = st.date_input("End Date", df_logs["Timestamp"].max().split(" ")[0])

        df_logs["DateOnly"] = pd.to_datetime(df_logs["Timestamp"]).dt.date
        df_filtered = df_logs[
            (df_logs["DateOnly"] >= start_date) &
            (df_logs["DateOnly"] <= end_date)
        ]
        if selected_user != "All":
            df_filtered = df_filtered[df_filtered["Username"] == selected_user]
        if selected_result != "All":
            df_filtered = df_filtered[df_filtered["Result"] == selected_result]
        if selected_supplier != "All":
            df_filtered = df_filtered[df_filtered["Supplier"] == selected_supplier]
        if selected_flight != "All":
            df_filtered = df_filtered[df_filtered["Flight Type"] == selected_flight]

        st.dataframe(df_filtered.drop(columns=["DateOnly"]))
        st.download_button("Download Logs as CSV", df_filtered.drop(columns=["DateOnly"]).to_csv(index=False), file_name="logs.csv")
    else:
        st.info("No logs available yet.")

# ---------------- LOGIN/LOGOUT ----------------
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if username_input in users and hash_password(password_input) == users[username_input][0]:
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.success(f"Welcome {username_input}")
        else:
            st.error("Invalid credentials")
    st.stop()

else:
    st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully")
        st.stop()
    if st.sidebar.button("View Logs"):
        show_logs()
        st.stop()
    if st.sidebar.button("Change Password"):
        st.session_state.otp_verified = False
        st.subheader("🔄 Change Password")
        new_password = st.text_input("Enter New Password", type="password")
        if not st.session_state.otp_verified:
            if st.button("Send OTP"):
                email_to = users[st.session_state.username][1]
                st.session_state.otp = generate_otp()
                if send_otp_email(email_to, st.session_state.otp):
                    st.info(f"OTP sent to {email_to}")
        else:
            entered_otp = st.text_input("Enter OTP sent to your email")
            if st.button("Verify OTP & Change Password"):
                if entered_otp == st.session_state.otp:
                    users[st.session_state.username][0] = hash_password(new_password)
                    st.success("Password changed successfully")
                    st.session_state.otp_verified = False
                else:
                    st.error("Incorrect OTP")
        st.stop()

# ---------------- CALCULATOR ----------------
st.title("🧮 Booking Safety Calculator")
st.caption("Operation Team – Safe vs Loss Booking Tool")

# ---------------- DI MASTER ----------------
supplier_di = {
    "TBO Flights Online - BOMA774": 0.01,
    "FlyShop Series Online API": 0.01,
    "Flyshop online API": 0.01,
    "Cleartrip Private Limited - AB 2": 0.01,
    "Travelopedia Series": 0.01,
    "Just Click N Pay Series": 0.01,
    "Fly24hrs Holiday Pvt. Ltd": 0.01,
    "Travelopedia": 0.01,
    "Etrave Flights": 0.0075,
    "ETrav Tech Limited": 0.0075,
    "Etrav Series Flights": 0.01,
    "Tripjack Pvt. Ltd.": 0.005,
    "Indigo Corporate Travelport Universal Api (KTBOM278)": 0.0045,
    "Indigo Regular Fare (Corporate)(KTBOM278)": 0.0045,
    "Indigo Retail Chandni (14354255C)": 0.0034,
    "Indigo Regular Corp Chandni (14354255C)": 0.0034,
    "BTO Bhasin Travels HAP OP7": 0.01,
    "Bhasin Travel Online HAP 7U63": 0.0184,
    "AIR IQ": 0.01,
    "Tripjack Flights": 0.005,
    "Etrav HAP 58Y8":0.01,
    "Consulate General of Indonesia-Mumbai": 0,
    "RIYA HAP 6A4T": 0,
    "Consulate Genenal Of Hungary - Visa": 0,
    "MUSAFIR.COM INDIA PVT LTD": 0,
    "MASTER BSP": 0,
    "Japan vfs": 0,
    "VFS Global Georgia - Visa": 0,
    "Akbar Travels HAP 3OT9": 0,
    "GRNConnect": 0,
    "CHINA VFS": 0,
    "FLYCREATIVE ONLINE PVT. LTD (LCC)": 0,
    "Bajaj Allianz General Insurance": 0,
    "South Africa VFS": 0,
    "MakeMyTrip (India) Private Limited": 0,
    "Travelport Universal Api": 0,
    "Deputy High Commission of Bangladesh, Mumbai": 0,
    "Bajaj Allianz General Insurance - Aertrip A/C": 0,
    "Germany Visa": 0,
    "Cleartrip Private Limited - AB 1": 0,
    "CDV HOLIDAYS PRIVATE LIMITED": 0,
    "Rudraa Tours And Travels Jayashree Patil": 0,
    "France Vfs": 0,
    "Vietnam Embassy New Delhi": 0,
    "Srilanka E Visa": 0,
    "Morocco Embassy New Delhi": 0,
    "Regional Passport Office-Mumbai": 0,
    "Klook Travel Tech Ltd Hong Kong HK": 0,
    "VANDANA VISA SERVICES": 0,
    "Consulate General of the Republic of Poland": 0,
    "Akbar Travel online AG43570": 0,
    "Just Click N Pay": 0,
    "IRCTC": 0,
    "Akbar Travels of India Pvt Ltd - (AG004261)": 0,
    "Embassy of Gabon": 0,
    "Go Airlines (India) Limited ( Offline )": 0,
    "UK VFS": 0,
    "GO KITE TRAVELS AND TOURS LLP": 0,
    "Travel super Mall (IXBAIU9800)": 0,
    "AirIQ Flights series Supplier": 0
}

# -------- ADD OTHER OPTION AT TOP --------
supplier_list = sorted(supplier_di.keys())
supplier_list.insert(0, "Other")

# ---------------- INPUT ROWS ----------------
c1, c2, c3, c4 = st.columns(4)
with c1: meta_partner = st.selectbox("Meta Partner", ["None", "Wego", "Wego Ads"])
with c2: flight_type = st.selectbox("Flight Type", ["Domestic", "International"])
with c3: supplier_name = st.selectbox("Supplier Name", supplier_list)
with c4: pax_count = st.number_input("Pax Count", min_value=1, step=1)

c5, c6, c7, c8, c9 = st.columns(5)
with c5: base_fare = st.number_input("Base Fare (₹)", min_value=0.0, step=100.0)
with c6: purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, step=100.0)
with c7: booking_amount = st.number_input("Booking Amount (₹)", min_value=0.0, step=100.0)
with c8: handling_fees = st.number_input("Handling Fees (₹)", min_value=0.0, step=10.0)
with c9: pg_fees = st.number_input("PG Fees (₹)", min_value=0.0, step=10.0)

def calculate_meta_fee(meta, flight, amount, pax):
    if meta == "None": return 0, 0, 0
    if flight == "Domestic": base_fee = 200 if pax <= 2 else 300
    else: base_fee = 400 if amount <= 30000 else 600
    ads_fee = 120 if meta == "Wego Ads" else 0
    return base_fee + ads_fee, base_fee, ads_fee

# ---------------- CALCULATE ----------------
st.markdown("###")
if st.button("🧮 Calculate"):
    meta_fee, base_fee_calc, ads_fee = calculate_meta_fee(meta_partner, flight_type, purchase_amount, pax_count)
    di_rate = 0 if supplier_name == "Other" else supplier_di.get(supplier_name, 0)
    di_amount = round(purchase_amount * di_rate, 2)
    plb_amount = 0
    plb_percent_text = "0%"

    if supplier_name in ["Indigo Corporate Travelport Universal Api (KTBOM278)", "Indigo Regular Fare (Corporate)(KTBOM278)"]:
        plb_amount = base_fare * (0.0075 if flight_type=="Domestic" else 0.015)
        plb_percent_text = "0.75%" if flight_type=="Domestic" else "1.50%"
    elif supplier_name in ["Indigo Regular Corp Chandni (14354255C)", "Indigo Retail Chandni (14354255C)"]:
        plb_amount = base_fare * (0.0125 if flight_type=="Domestic" else 0.0185)
        plb_percent_text = "1.25%" if flight_type=="Domestic" else "1.85%"

    plb_amount = round(plb_amount, 2)
    purchase_side = purchase_amount + meta_fee + pg_fees
    sale_side = booking_amount + di_amount + handling_fees + plb_amount
    difference = round(sale_side - purchase_side, 2)
    result_text = "Safe" if difference >=0 else "Loss"

    # ---------------- LOGGING ----------------
    log_calculation(st.session_state.username, {
        "Supplier": supplier_name,
        "Flight Type": flight_type,
        "Booking Amount": booking_amount,
        "Purchase Amount": purchase_amount,
        "PLB Amount": plb_amount,
        "DI Amount": di_amount,
        "Meta Fees": meta_fee,
        "Difference": difference,
        "Result": result_text
    })

    # ---------------- DISPLAY ----------------
    st.divider()
    st.subheader("📊 Calculation Summary")
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    o1, o2, o3, o4 = st.columns(4)

    with o1:
        st.markdown("### 🏷 Supplier & DI")
        st.write(f"**Supplier:** {supplier_name}")
        st.write(f"**DI %:** {di_rate*100:.2f}%")
        st.write(f"**DI Amount:** ₹ {di_amount}")

    with o2:
        st.markdown("### 📢 Meta Fees")
        st.write(f"**Meta Partner:** {meta_partner}")
        st.write(f"**Base Fee:** ₹ {base_fee_calc}")
        if meta_partner == "Wego Ads":
            st.write(f"**Ads Fee:** ₹ {ads_fee}")
        st.write(f"**Total Meta Fees:** ₹ {meta_fee}")

    with o3:
        st.markdown("### 🎯 PLB")
        st.write(f"**Base Fare:** ₹ {base_fare}")
        st.write(f"**PLB % Applied:** {plb_percent_text}")
        st.write(f"**PLB Amount:** ₹ {plb_amount}")

    with o4:
        st.markdown("### 💰 Purchase vs Sale")
        st.write(f"**Purchase Side (Purchase + Meta + PG):** ₹ {purchase_side}")
        st.write(f"**Sale Side (Booking + DI + Handling + PLB):** ₹ {sale_side}")
        st.markdown(f"### 💹 Difference: ₹ {difference}")
        if difference < 0: st.error("❌ Loss Booking")
        else: st.success("✅ Safe Booking")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 10px;
        bottom: 10px;
        color: #6c757d;
        font-size: 12px;
    }
    </style>
    <div class="footer">
        Auto-updated via GitHub | Last updated on 11 Jan 2026
    </div>
    """,
    unsafe_allow_html=True
)
