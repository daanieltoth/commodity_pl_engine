import streamlit as st

from models import MarketState, OptionPosition
from pricing import calculate_position_risk


st.set_page_config(
    page_title="Commodity P&L Engine",
    page_icon="📈",
    layout="wide",
)

st.title("Commodity P&L Engine")
st.caption("Black–76 option valuation and live risk")


with st.sidebar:
    st.header("Position")

    position_id = st.text_input("Position ID", value="POS-001")
    commodity = st.text_input("Commodity", value="WTI")
    option_type = st.selectbox("Option type", options=["call", "put"])
    strike = st.number_input(
        "Strike", min_value=0.0001, value=100.0, step=1.0
    )
    quantity = st.number_input(
        "Quantity",
        value=10,
        step=1,
        help="Positive = long, negative = short",
    )
    contract_size = st.number_input(
        "Contract size",
        min_value=0.0001,
        value=1000.0,
        step=100.0,
    )


st.subheader("Current market")
market_col_1, market_col_2 = st.columns(2)

with market_col_1:
    forward = st.number_input(
        "Forward price", min_value=0.0001, value=102.0, step=1.0
    )
    volatility_percent = st.number_input(
        "Volatility (%)", min_value=0.0001, value=20.0, step=1.0
    )

with market_col_2:
    time_to_expiry = st.number_input(
        "Time to expiry (years)",
        min_value=0.0001,
        value=1.0,
        step=0.01,
    )
    rate_percent = st.number_input(
        "Interest rate (%)", value=3.0, step=0.25
    )


position = OptionPosition(
    position_id=position_id,
    commodity=commodity,
    market_key="LIVE_MARKET",
    strike=strike,
    option_type=option_type,
    quantity=quantity,
    contract_size=contract_size,
)

market = MarketState(
    forward=forward,
    volatility=volatility_percent / 100,
    time_to_expiry=time_to_expiry,
    rate=rate_percent / 100,
)


try:
    risk = calculate_position_risk(position=position, market=market)

    st.subheader("Current position risk")
    value_col, delta_col, gamma_col = st.columns(3)
    value_col.metric("Market value", f"{risk.market_value:,.2f}")
    delta_col.metric("Delta", f"{risk.delta:,.2f}")
    gamma_col.metric("Gamma", f"{risk.gamma:,.2f}")

    vega_col, theta_col = st.columns(2)
    vega_col.metric("Vega per 1pp", f"{risk.vega_1pp:,.2f}")
    theta_col.metric("Theta per day", f"{risk.theta_daily:,.2f}")

    st.info(
        "The numbers refresh automatically when the numbers are changed"
    )
    
except ValueError as error:
    st.error(str(error))
