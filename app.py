import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Meta Fees Calculator",
    layout="centered"
)

st.title("🧮 Meta Fees Calculator")
st.caption("Wego & TripSaverz – Operation Team Tool")

# ---------------- INPUTS ----------------
meta_partner = st.selectbox(
    "Meta Partner",
    ["Wego", "TripSaverz"]
)

flight_type = st.selectbox(
    "Flight Type",
    ["Domestic", "International"]
)

booking_amount = st.number_input(
    "Booking Amount (₹)",
    min_value=0.0,
    step=100.0
)

pax_count = st.number_input(
    "Passenger Count",
    min_value=1,
    step=1
)

# ---------------- FEES LOGIC ----------------
def calculate_meta_fee(meta, flight, amount, pax):
    fee = 0

    # WEGO LOGIC
    if meta == "Wego":
        if flight == "Domestic":
            fee = 200 if pax <= 2 else 300
        elif flight == "International":
            fee = 400 if amount <= 30000 else 600

    # TRIPSAVERZ LOGIC
    elif meta == "TripSaverz":
        if flight == "Domestic":
            fee = amount * 0.01
        elif flight == "International":
            fee = amount * 0.015

    return round(fee, 2)

# ---------------- CALCULATE BUTTON ----------------
if st.button("Calculate Meta Fees"):
    meta_fee = calculate_meta_fee(
        meta_partner,
        flight_type,
        booking_amount,
        pax_count
    )

    st.divider()
    st.subheader("💰 Meta Fees")
    st.write(f"₹ {meta_fee}")

# ---------------- FIXED FOOTER (LEFT BOTTOM) ----------------
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
        Auto-updated via GitHub | Updated on 24 Dec 2025
    </div>
    """,
    unsafe_allow_html=True
)
