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
    """
    Returns meta fee per booking
    """
    fee = 0

    # WEGO LOGIC
    if meta == "Wego":
        if flight == "Domestic":
            if pax <= 2:
                fee = 200
            else:
                fee = 300

        elif flight == "International":
            if amount <= 30000:
                fee = 400
            else:
                fee = 600

    # TRIPSAVERZ LOGIC
    elif meta == "TripSaverz":
        if flight == "Domestic":
            fee = amount * 0.01
        elif flight == "International":
            fee = amount * 0.015

    return round(fee, 2)

meta_fee = calculate_meta_fee(
    meta_partner,
    flight_type,
    booking_amount,
    pax_count
)

net_amount = round(booking_amount - meta_fee, 2)

# ---------------- OUTPUT ----------------
st.divider()
st.subheader("📊 Calculation Result")

st.write(f"**Meta Fee:** ₹ {meta_fee}")
st.write(f"**Net Amount After Fees:** ₹ {net_amount}")

if net_amount < 0:
    st.error("⚠️ NEGATIVE BOOKING – Do not proceed")
else:
    st.success("✅ SAFE BOOKING")

# ---------------- FOOTER ----------------
st.caption("Auto-updated via GitHub | Same link for Ops Team")
