import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Meta + DI Booking Safety Calculator",
    layout="wide"   # ✅ FULL WIDTH
)

st.title("🧮 Meta + DI Booking Safety Calculator")
st.caption("Operation Team – Safe vs Loss Booking Tool")

# ---------------- DI MASTER ----------------
supplier_di = {
    "TBO Flights Online - BOMA774": 0.0084,
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
    "BTO Bhasin Travels HAP OP7": 0.0184,
    "Bhasin Travel Online HAP 7U63": 0.0184,
    "Travel super Mall (IXBAIU9800)": 0,
    "AirIQ Flights series Supplier": 0,
    "AIR IQ": 0.01,
    "Tripjack Flights": 0.005
}

# ---------------- INPUT ROW 1 ----------------
c1, c2, c3 = st.columns(3)

with c1:
    meta_partner = st.selectbox("Meta Partner", ["None", "Wego", "Wego Ads"])

with c2:
    flight_type = st.selectbox("Flight Type", ["Domestic", "International"])

with c3:
    supplier_name = st.selectbox("Supplier Name", sorted(supplier_di.keys()))

# ---------------- INPUT ROW 2 ----------------
c4, c5, c6, c7 = st.columns(4)

with c4:
    booking_amount = st.number_input("Booking Amount (₹)", min_value=0.0, step=100.0)

with c5:
    purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, step=100.0)

with c6:
    pg_fees = st.number_input("PG Fees (₹)", min_value=0.0, step=10.0)

with c7:
    pax_count = st.number_input("Pax Count", min_value=1, step=1)

# ---------------- FUNCTIONS ----------------
def calculate_meta_fee(meta, flight, amount, pax):
    if meta == "None":
        return 0, 0, 0

    if flight == "Domestic":
        base_fee = 200 if pax <= 2 else 300
    else:
        base_fee = 400 if amount <= 30000 else 600

    ads_fee = 120 if meta == "Wego Ads" else 0
    return base_fee + ads_fee, base_fee, ads_fee

# ---------------- CALCULATE ----------------
st.markdown("###")
if st.button("🧮 Calculate"):
    meta_fee, base_fee, ads_fee = calculate_meta_fee(
        meta_partner, flight_type, purchase_amount, pax_count
    )

    di_rate = supplier_di.get(supplier_name, 0)
    di_amount = round(purchase_amount * di_rate, 2)

    purchase_side = purchase_amount + meta_fee + pg_fees
    sale_side = booking_amount + di_amount
    difference = round(sale_side - purchase_side, 2)

    st.divider()
    st.subheader("📊 Calculation Summary")

    # -------- OUTPUT HORIZONTAL --------
    o1, o2, o3 = st.columns(3)

    with o1:
        st.markdown("### 🏷 Supplier & DI")
        st.write(f"**Supplier:** {supplier_name}")
        st.write(f"**DI %:** {di_rate * 100:.2f}%")
        st.write(f"**DI Amount:** ₹ {di_amount}")

    with o2:
        st.markdown("### 📢 Meta Fees")
        st.write(f"**Meta Partner:** {meta_partner}")
        st.write(f"**Base Meta Fee:** ₹ {base_fee}")
        if meta_partner == "Wego Ads":
            st.write(f"**Wego Ads Fee:** ₹ {ads_fee}")
        st.write(f"**Total Meta Fees:** ₹ {meta_fee}")

    with o3:
        st.markdown("### 💰 Purchase vs Sale")
        st.write(f"**Purchase Side (Purchase + Meta + PG):** ₹ {purchase_side}")
        st.write(f"**Sale Side (Booking + DI):** ₹ {sale_side}")
        st.markdown(f"### 💹 Difference: ₹ {difference}")

        if difference < 0:
            st.error("❌ Loss Booking")
        else:
            st.success("✅ Safe Booking")

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
        Auto-updated via GitHub
    </div>
    """,
    unsafe_allow_html=True
)
