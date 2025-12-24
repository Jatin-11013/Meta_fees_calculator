import streamlit as st

st.set_page_config(page_title="Meta Fees Calculator", layout="centered")
st.title("🧮 Meta Fees Calculator")
st.write("Wego & TripSaverz – Operation Team Tool")

# Inputs
meta_partner = st.selectbox("Meta Partner", ["Wego", "TripSaverz"])
flight_type = st.selectbox("Flight Type", ["Domestic", "International"])
booking_amount = st.number_input("Booking Amount (₹)", min_value=0.0, step=100.0)
pax_count = st.number_input("Passenger Count", min_value=1, step=1)

# Fees logic
def calculate_meta_fee(meta, flight, amount, pax):
    fee = 0
    if meta == "Wego":
        if flight == "Domestic":
            fee = 200 if pax <= 2 else 300
        elif flight == "International":
            fee = 400 if amount <= 30000 else 600
    elif meta == "TripSaverz":
        if flight == "Domestic":
            fee = amount * 0.01
        elif flight == "International":
            fee = amount * 0.015
    return fee

meta_fee = calculate_meta_fee(meta_partner, flight_type, booking_amount, pax_count)
net_amount = booking_amount - meta_fee

# Output
st.divider()
st.subheader("📊 Calculation Result")
st.write(f"Meta Fee: ₹{meta_fee:.2f}")
st.write(f"Net Amount After Fees: ₹{net_amount:.2f}")

if net_amount < 0:
    st.error("⚠️ NEGATIVE BOOKING")
else:
    st.success("✅ SAFE BOOKING")
