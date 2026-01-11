import streamlit as st
import pandas as pd
import datetime
import hashlib
import random
import string
import smtplib
from email.message import EmailMessage
import gspread
from google.oauth2.service_account import Credentials

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Booking Safety Calculator", layout="wide")

# -------- STYLING --------
st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.summary-box p { font-size: 12px; margin-bottom: 3px; }
.summary-box h3 { font-size: 14px; margin-bottom: 5px; }
.stSelectbox label, .stNumberInput label { font-size: 13px; }
.footer {position: fixed; left: 10px; bottom: 10px; color: #6c757d; font-size: 12px;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
for key in ["logged_in","username","otp","otp_verified","viewing_logs","admin_panel","back"]:
    if key not in st.session_state:
        st.session_state[key] = False if "logged_in" in key else ""

# ---------------- GOOGLE SHEET CONFIG ----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
gc = gspread.authorize(creds)

# <-- Paste your Google Sheet ID here -->
SHEET_ID = "1gzbcl7nT77Kk42UzCw-RwV5DpJqRRyGQFHQSyp1XC_Q"
sh = gc.open_by_key(SHEET_ID)
LOGS_TAB = "Logs"
USERS_TAB = "Users"

# ---------------- HARD-CODED ADMIN ----------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@123"

# ---------------- FUNCTIONS ----------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def generate_otp():
    return "".join(random.choices(string.digits, k=6))

def send_otp_email(email, otp_code):
    sender_email = "jatinjr11013@gmail.com"           # <--- CHANGE THIS
    sender_pass = "zier gnxf snkr repo"              # <--- CHANGE THIS
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

# ---------------- USERS HANDLING ----------------
def initialize_users():
    """If Users tab is empty, create default admin"""
    try:
        worksheet = sh.worksheet(USERS_TAB)
        all_users = worksheet.get_all_records()
        if len(all_users)==0:
            default_username = "Jatin Yadav"
            default_password = hash_password("jatin@123")
            default_email = "jatinjr11013@gmail.com"
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([default_username, default_password, default_email, "Admin", created_at, "", "", "False"])
    except gspread.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=USERS_TAB, rows="50", cols="20")
        worksheet.append_row(["Username","Password","Email","Role","Created At","Last Login","Temporary Password","OTP Verified"])
        initialize_users()

def get_users():
    try:
        worksheet = sh.worksheet(USERS_TAB)
        data = worksheet.get_all_records()
        users_dict = {}
        for row in data:
            users_dict[row["Username"]] = [row["Password"], row["Email"], row["Role"]]
        return users_dict
    except:
        return {}

def update_user_password(username, new_hashed_pw):
    worksheet = sh.worksheet(USERS_TAB)
    all_users = worksheet.get_all_records()
    for idx, row in enumerate(all_users):
        if row["Username"] == username:
            worksheet.update_cell(idx+2, 2, new_hashed_pw)
            worksheet.update_cell(idx+2, 6, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Last Login
            break

def add_user(username, password, email, role="User"):
    worksheet = sh.worksheet(USERS_TAB)
    hashed_pw = hash_password(password)
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([
        username,
        hashed_pw,
        email,
        role,
        created_at,
        "",
        "",
        "False"
    ])

# ---------------- LOGS HANDLING ----------------
def log_calculation(username, data_dict):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_dict["Username"] = username
    data_dict["Timestamp"] = timestamp
    df_new = pd.DataFrame([data_dict])
    try:
        worksheet = sh.worksheet(LOGS_TAB)
        existing_data = worksheet.get_all_records()
        df_existing = pd.DataFrame(existing_data)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
        worksheet.clear()
        worksheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())
    except gspread.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=LOGS_TAB, rows="100", cols="30")
        worksheet.update([df_new.columns.values.tolist()] + df_new.values.tolist())

def show_logs():
    st.session_state.viewing_logs = True
    worksheet = sh.worksheet(LOGS_TAB)
    df_logs = pd.DataFrame(worksheet.get_all_records())
    if df_logs.empty:
        st.info("No logs available yet.")
        return
    users_filter = ["All"] + df_logs["Username"].unique().tolist()
    result_filter = ["All"] + df_logs["Result"].unique().tolist()
    supplier_filter = ["All"] + df_logs["Supplier"].unique().tolist()
    flight_filter = ["All"] + df_logs["Flight Type"].unique().tolist()
    
    selected_user = st.selectbox("Filter by User", users_filter)
    selected_result = st.selectbox("Filter by Result", result_filter)
    selected_supplier = st.selectbox("Filter by Supplier", supplier_filter)
    selected_flight = st.selectbox("Filter by Flight Type", flight_filter)
    start_date = st.date_input("Start Date", pd.to_datetime(df_logs["Timestamp"].min()).date())
    end_date = st.date_input("End Date", pd.to_datetime(df_logs["Timestamp"].max()).date())
    
    df_logs["DateOnly"] = pd.to_datetime(df_logs["Timestamp"]).dt.date
    df_filtered = df_logs[
        (df_logs["DateOnly"] >= start_date) &
        (df_logs["DateOnly"] <= end_date)
    ]
    if selected_user != "All": df_filtered = df_filtered[df_filtered["Username"]==selected_user]
    if selected_result != "All": df_filtered = df_filtered[df_filtered["Result"]==selected_result]
    if selected_supplier != "All": df_filtered = df_filtered[df_filtered["Supplier"]==selected_supplier]
    if selected_flight != "All": df_filtered = df_filtered[df_filtered["Flight Type"]==selected_flight]
    
    st.dataframe(df_filtered.drop(columns=["DateOnly"]))
    st.download_button("Download Logs as CSV", df_filtered.drop(columns=["DateOnly"]).to_csv(index=False), file_name="logs.csv")
    if st.button("⬅ Back to Calculator"):
        st.session_state.viewing_logs = False
        st.experimental_rerun()

# ---------------- INITIALIZE ----------------
initialize_users()
users = get_users()

# ---------------- LOGIN ----------------
if not st.session_state.logged_in and not st.session_state.viewing_logs:
    st.subheader("🔐 Login")

    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):

        # 🔐 ADMIN LOGIN (HARDCODED)
        if username_input == ADMIN_USERNAME and password_input == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = "Admin"
            st.session_state.admin_panel = True
            st.success("Welcome Admin")
            st.experimental_rerun()

        # 👤 NORMAL USER LOGIN (GOOGLE SHEET)
        elif username_input in users and hash_password(password_input) == users[username_input][0]:
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.session_state.admin_panel = False
            update_user_password(username_input, users[username_input][0])
            st.success(f"Welcome {username_input}")
            st.experimental_rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- FORGOT PASSWORD ----------------
if st.session_state.back == "forgot":
    st.subheader("🔄 Forgot Password")
    forgot_user = st.text_input("Enter Username")
    forgot_email = st.text_input("Enter Email")
    if st.button("Send OTP"):
        if forgot_user in users and forgot_email == users[forgot_user][1]:
            st.session_state.otp = generate_otp()
            if send_otp_email(forgot_email, st.session_state.otp):
                st.success(f"OTP sent to {forgot_email}")
                st.session_state.back = "otp"
        else:
            st.error("Username or Email mismatch")
    if st.button("⬅ Back to Login"):
        st.session_state.back = ""
        st.experimental_rerun()
    st.stop()

if st.session_state.back == "otp":
    st.subheader("Enter OTP & Change Password")
    entered_otp = st.text_input("Enter OTP sent to your email")
    new_pw = st.text_input("New Password", type="password")
    new_pw_conf = st.text_input("Confirm New Password", type="password")
    if st.button("Change Password"):
        if entered_otp == st.session_state.otp:
            if new_pw == new_pw_conf:
                hashed = hash_password(new_pw)
                update_user_password(forgot_user, hashed)
                st.success("Password changed successfully")
                st.session_state.back = ""
                st.experimental_rerun()
            else:
                st.error("Passwords do not match")
        else:
            st.error("Incorrect OTP")
    if st.button("⬅ Back to Login"):
        st.session_state.back = ""
        st.experimental_rerun()
    st.stop()

# ---------------- CALCULATOR ----------------
if st.session_state.logged_in and not st.session_state.viewing_logs:
    st.title("🧮 Booking Safety Calculator")
    st.caption("Operation Team – Safe vs Loss Booking Tool")
    
    # ---------------- ADMIN PANEL ----------------
    if st.session_state.admin_panel:
        st.subheader("🛠 Admin Panel – Add User")

        new_user = st.text_input("New Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["User", "Admin"])

        if st.button("➕ Add User"):
            if new_user and new_password and new_email:
                add_user(new_user, new_password, new_email, new_role)
                st.success("User added successfully")
                st.experimental_rerun()
            else:
                st.error("All fields are required")

        st.divider()

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

    # ---------------- CALCULATION ----------------
    def calculate_meta_fee(meta, flight, amount, pax):
        if meta == "None": return 0,0,0
        if flight=="Domestic": base_fee = 200 if pax<=2 else 300
        else: base_fee = 400 if amount<=30000 else 600
        ads_fee = 120 if meta=="Wego Ads" else 0
        return base_fee+ads_fee, base_fee, ads_fee

    if st.button("🧮 Calculate"):
        meta_fee, base_fee_calc, ads_fee = calculate_meta_fee(meta_partner, flight_type, purchase_amount, pax_count)
        di_rate = 0 if supplier_name=="Other" else supplier_di.get(supplier_name,0)
        di_amount = round(purchase_amount*di_rate,2)

        plb_amount = 0
        plb_percent_text="0%"
        if supplier_name in ["Indigo Corporate Travelport Universal Api (KTBOM278)","Indigo Regular Fare (Corporate)(KTBOM278)"]:
            plb_amount = base_fare*(0.0075 if flight_type=="Domestic" else 0.015)
            plb_percent_text = "0.75%" if flight_type=="Domestic" else "1.50%"
        elif supplier_name in ["Indigo Regular Corp Chandni (14354255C)","Indigo Retail Chandni (14354255C)"]:
            plb_amount = base_fare*(0.0125 if flight_type=="Domestic" else 0.0185)
            plb_percent_text = "1.25%" if flight_type=="Domestic" else "1.85%"
        plb_amount = round(plb_amount,2)

        purchase_side = purchase_amount + meta_fee + pg_fees
        sale_side = booking_amount + di_amount + handling_fees + plb_amount
        difference = round(sale_side - purchase_side,2)
        result_text = "Safe" if difference>=0 else "Loss"

        # ---------------- LOGGING ----------------
        log_calculation(st.session_state.username,{
            "Supplier": supplier_name,
            "Flight Type": flight_type,
            "Pax Count": pax_count,
            "Base Fare": base_fare,
            "Purchase Amount": purchase_amount,
            "Booking Amount": booking_amount,
            "Handling Fees": handling_fees,
            "PG Fees": pg_fees,
            "DI %": di_rate*100,
            "DI Amount": di_amount,
            "PLB %": plb_percent_text,
            "PLB Amount": plb_amount,
            "Meta Partner": meta_partner,
            "Base Fee": base_fee_calc,
            "Ads Fee": ads_fee,
            "Total Meta Fee": meta_fee,
            "Purchase Side": purchase_side,
            "Sale Side": sale_side,
            "Difference": difference,
            "Result": result_text
        })

        # ---------------- DISPLAY ----------------
        st.divider()
        st.subheader("📊 Calculation Summary")
        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        o1,o2,o3,o4 = st.columns(4)
        with o1:
            st.markdown("### 🏷 Supplier & DI")
            st.write(f"**Supplier:** {supplier_name}")
            st.write(f"**DI %:** {di_rate*100:.2f}%")
            st.write(f"**DI Amount:** ₹ {di_amount}")
        with o2:
            st.markdown("### 📢 Meta Fees")
            st.write(f"**Meta Partner:** {meta_partner}")
            st.write(f"**Base Fee:** ₹ {base_fee_calc}")
            st.write(f"**Ads Fee:** ₹ {ads_fee}")
            st.write(f"**Total Meta Fee:** ₹ {meta_fee}")
        with o3:
            st.markdown("### 💰 PLB")
            st.write(f"**PLB %:** {plb_percent_text}")
            st.write(f"**PLB Amount:** ₹ {plb_amount}")
        with o4:
            st.markdown("### ⚖ Result")
            st.write(f"**Purchase Side:** ₹ {purchase_side}")
            st.write(f"**Sale Side:** ₹ {sale_side}")
            st.write(f"**Difference:** ₹ {difference}")
            st.write(f"**Result:** {result_text}")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("📂 View Logs"):
        show_logs()

st.markdown('<div class="footer">Auto-updated via GitHub | Last updated on 11 Jan 2026</div>', unsafe_allow_html=True)
