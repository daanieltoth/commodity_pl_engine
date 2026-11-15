import math
from models import *
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


def value_position(
    position: OptionPosition,
    market: MarketState,
) -> float:
    unit_price = black76_price(
        forward=market.forward,
        strike=position.strike,
        volatility=market.volatility,
        time_to_expiry=market.time_to_expiry,
        rate=market.rate,
        option_type=position.option_type,
    )

    position_multiplier = (
        position.quantity
        * position.contract_size
    )

    return unit_price * position_multiplier

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

def normal_pdf(x: float) -> float:
    return (
        1 / math.sqrt(2 * math.pi)
        * math.exp(-0.5 * x ** 2)
    )

def black76_gamma(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, _ = calculate_d1_d2(
        forward,
        strike,
        volatility,
        time_to_expiry,
    )

    discount_factor = math.exp(-rate * time_to_expiry)

    gamma = (
        discount_factor
        * normal_pdf(d1)
        / (
            forward
            * volatility
            * math.sqrt(time_to_expiry)
        )
    )

    return gamma

def black76_vega(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, _ = calculate_d1_d2(
        forward,
        strike,
        volatility,
        time_to_expiry,
    )

    discount_factor = math.exp(-rate * time_to_expiry)

    vega = (
        discount_factor
        * forward
        * normal_pdf(d1)
        * math.sqrt(time_to_expiry)
    )

    return vega

def black76_theta(
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

    option_price = black76_price(
        forward,
        strike,
        volatility,
        time_to_expiry,
        rate,
        option_type,
    )

    discount_factor = math.exp(-rate * time_to_expiry)

    theta = (
        rate * option_price
        - (
            discount_factor
            * forward
            * normal_pdf(d1)
            * volatility
        )
        / (2 * math.sqrt(time_to_expiry))
    )

    return theta


