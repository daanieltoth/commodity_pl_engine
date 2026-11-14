import math

def calculate_d1_d2(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
) -> tuple[float, float]:
    d1 = (
        math.log(forward / strike)
        + 0.5 * volatility ** 2 * time_to_expiry
    ) / (volatility * math.sqrt(time_to_expiry))

    d2 = d1 - volatility * math.sqrt(time_to_expiry)

    return d1, d2

def normal_cdf(x: float) -> float:
    return 1/2*(1 + math.erf(x/math.sqrt(2)))

def black76_call(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, d2 = calculate_d1_d2(forward, strike, volatility, time_to_expiry)
    discount_factor = math.exp(-rate * time_to_expiry)

    call_price = discount_factor * (
        forward * normal_cdf(d1)
        - strike * normal_cdf(d2)
    )

    return call_price

def black76_put(
        forward:float,
        strike:float,
        volatility: float,
        time_to_expiry: float,
        rate: float
) -> float:
    d1, d2 = calculate_d1_d2(forward, strike, volatility, time_to_expiry)
    discount_factor = math.exp(-rate * time_to_expiry)
    put_price = discount_factor*((strike*normal_cdf(-d2)) - (forward*normal_cdf(-d1)))

    return put_price

def black76_price(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
    option_type: str,
) -> float:
    option_type = option_type.lower()

    if option_type == "call":
        return black76_call(forward, strike, volatility, time_to_expiry, rate)
        
    elif option_type == "put":
         return black76_put(forward, strike, volatility, time_to_expiry, rate)
    else:
        raise ValueError("option_type must be 'call' or 'put'")


def position_value(
        forward: float,
        strike: float,
        volatility: float,
        time_to_expiry: float,
        rate: float,
        option_type: str,
        quantity: int,
        contract_size: float,
) -> float:
    option_price = black76_price(forward, strike, volatility, time_to_expiry, rate, option_type)

    return option_price*quantity*contract_size

value = position_value(
    forward=100,
    strike=100,
    volatility=0.20,
    time_to_expiry=1.0,
    rate=0.0,
    option_type="call",
    quantity=10,
    contract_size=1000,
)

def calculate_pnl(
        old_value: float,
        new_value: float,
) -> float:
    return old_value - new_value

def black76_delta(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
    option_type: str,
) -> float:
    d1, _ = calculate_d1_d2(
        forward,
        strike,
        volatility,
        time_to_expiry,
    )

    discount_factor = math.exp(-rate * time_to_expiry)
    option_type = option_type.lower()

    if option_type == "call":
        return discount_factor * normal_cdf(d1)

    if option_type == "put":
        return -discount_factor * normal_cdf(-d1)

    raise ValueError("option_type must be 'call' or 'put'")

