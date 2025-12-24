import streamlit as st

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Meta Fees Calculator",
    page_icon="🧮",
    layout="centered"
)

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
    <h2 style="text-align:center;">🧮 Meta Fees Calculator</h2>
    <p style="text-align:center; color:gray;">
        Wego & TripSaverz – Operation Team Tool
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# INPUT SECTION
# =====================================================
col1, col2 = st.columns(2)

with col1:
    meta_partner = st.selectbox(
        "Meta Partner",
        ["Wego", "TripSaverz"]
    )

    flight_type = st.selectbox(
        "Flight Type",
        ["Domestic", "International"]
    )

with col2:
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

# =====================================================
# FEES LOGIC
# =====================================================
def calculate_meta_fee(meta, flight, amount, pax):
    fee = 0.0

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

# =====================================================
# CALCULATE BUTTON & RESULT
# =====================================================
st.divider()

center_col = st.columns([1, 2, 1])[1]
with center_col:
    calculate_clicked = st.button("Calculate Meta Fees", use_container_width=True)

if calculate_clicked:
    meta_fee = calculate_meta_fee(
        meta_partner,
        flight_type,
        booking_amount,
        pax_count
    )

    st.markdown(
        f"""
        <div style="
            background-color:#f8f9fa;
            padding:20px;
            border-radius:10px;
            text-align:center;
            margin-top:15px;
            border:1px solid #e0e0e0;
        ">
            <p style="color:gray; margin-bottom:5px;">Meta Fees</p>
            <h2 style="margin:0;">₹ {meta_fee}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# FIXED FOOTER (LEFT BOTTOM)
# =====================================================
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 12px;
        bottom: 10px;
        color: #6c757d;
        font-size: 12px;
        z-index: 999;
    }
    </style>

    <div class="footer">
        Auto-updated via GitHub
    </div>
    """,
    unsafe_allow_html=True
)
