import math

def calculate_d1_d2(
        forward: float,
        strike: float,
        volatility: float,
        time_to_expiry : float
):
    d1 = (math.log(forward / strike)+ 0.5 * volatility ** 2 * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
    d2 = d1 - (volatility - math.sqrt(time_to_expiry))

    return (d1,d2)

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