import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Meta Fees, DI & Booking Safety Calculator",
    layout="centered"
)

st.title("🧮 Meta Fees, DI & Booking Safety Calculator")
st.caption("Wego / Wego Ads + Supplier DI – Operation Team Tool")

# ---------------- SUPPLIER DI MASTER ----------------
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
    "BTO Bhasin Travels HAP OP7": 0.0184,
    "Bhasin Travel Online HAP 7U63": 0.0184,
    "AIR IQ": 0.01,
    "Tripjack Flights": 0.005
}

# ---------------- INPUTS ----------------
meta_partner = st.selectbox("Meta Partner", ["Wego", "Wego Ads"])
flight_type = st.selectbox("Flight Type", ["Domestic", "International"])

booking_amount = st.number_input("Booking Amount (₹)", min_value=0.0, step=100.0)
purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, step=100.0)
pg_fees = st.number_input("PG Fees (₹)", min_value=0.0, step=10.0)
pax_count = st.number_input("Passenger Count", min_value=1, step=1)

supplier_name = st.selectbox(
    "Supplier Name (type to search)",
    options=sorted(supplier_di.keys())
)

# ---------------- LOGIC FUNCTIONS ----------------
def calculate_meta_fee(meta, flight, amount, pax):
    base_fee = 0
    ads_fee = 0

    if flight == "Domestic":
        base_fee = 200 if pax <= 2 else 300
    else:
        base_fee = 400 if amount <= 30000 else 600

    total_fee = base_fee

    if meta == "Wego Ads":
        ads_fee = 120
        total_fee += ads_fee

    return total_fee, base_fee, ads_fee


def calculate_di(amount, rate):
    return round(amount * rate, 2)

# ---------------- CALCULATE ----------------
if st.button("Calculate"):
    meta_fee, base_fee, ads_fee = calculate_meta_fee(
        meta_partner, flight_type, purchase_amount, pax_count
    )

    di_rate = supplier_di.get(supplier_name, 0)
    di_amount = calculate_di(purchase_amount, di_rate)

    # 🔹 Purchase & Sale Side
    purchase_side = purchase_amount + meta_fee + pg_fees
    sale_side = booking_amount + di_amount

    difference = round(sale_side - purchase_side, 2)

    # ---------------- OUTPUT ----------------
    st.divider()
    st.subheader("📊 Calculation Summary")

    st.write(f"**Booking Amount:** ₹ {booking_amount}")
    st.write(f"**Purchase Amount:** ₹ {purchase_amount}")
    st.write(f"**PG Fees:** ₹ {pg_fees}")

    st.write("---")
    st.write(f"**Base Wego Fee:** ₹ {base_fee}")
    if meta_partner == "Wego Ads":
        st.write(f"**Wego Ads Fee:** ₹ {ads_fee}")
    st.write(f"**Total Meta Fees:** ₹ {meta_fee}")

    st.write("---")
    st.write(f"**Supplier:** {supplier_name}")
    st.write(f"**DI %:** {di_rate * 100:.2f}%")
    st.write(f"**DI Amount:** ₹ {di_amount}")

    st.write("---")
    st.write(f"**Purchase Side (Purchase + Meta + PG):** ₹ {purchase_side}")
    st.write(f"**Sale Side (Booking + DI):** ₹ {sale_side}")

    st.subheader(f"💹 Difference: ₹ {difference}")

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
