import math

from models import (
    MarketState,
    OptionPosition,
    PnLReport,
    PortfolioRiskReport,
    PositionRiskRow,
    RiskReport,
)


def calculate_d1_d2(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
) -> tuple[float, float]:
    if forward <= 0:
        raise ValueError("forward must be positive")
    if strike <= 0:
        raise ValueError("strike must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    if time_to_expiry <= 0:
        raise ValueError("time_to_expiry must be positive")

    volatility_time = volatility * math.sqrt(time_to_expiry)
    d1 = (
        math.log(forward / strike)
        + 0.5 * volatility**2 * time_to_expiry
    ) / volatility_time
    d2 = d1 - volatility_time
    return d1, d2


def normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


def black76_call(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, d2 = calculate_d1_d2(
        forward, strike, volatility, time_to_expiry
    )
    discount_factor = math.exp(-rate * time_to_expiry)
    return discount_factor * (
        forward * normal_cdf(d1) - strike * normal_cdf(d2)
    )


def black76_put(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, d2 = calculate_d1_d2(
        forward, strike, volatility, time_to_expiry
    )
    discount_factor = math.exp(-rate * time_to_expiry)
    return discount_factor * (
        strike * normal_cdf(-d2) - forward * normal_cdf(-d1)
    )


def black76_price(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
    option_type: str,
) -> float:
    normalized_type = option_type.strip().lower()
    if normalized_type == "call":
        return black76_call(
            forward, strike, volatility, time_to_expiry, rate
        )
    if normalized_type == "put":
        return black76_put(
            forward, strike, volatility, time_to_expiry, rate
        )
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
    return unit_price * position.quantity * position.contract_size


def calculate_pnl(old_value: float, new_value: float) -> float:
    return new_value - old_value


def black76_delta(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
    option_type: str,
) -> float:
    d1, _ = calculate_d1_d2(
        forward, strike, volatility, time_to_expiry
    )
    discount_factor = math.exp(-rate * time_to_expiry)
    normalized_type = option_type.strip().lower()

    if normalized_type == "call":
        return discount_factor * normal_cdf(d1)
    if normalized_type == "put":
        return -discount_factor * normal_cdf(-d1)
    raise ValueError("option_type must be 'call' or 'put'")


def black76_gamma(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, _ = calculate_d1_d2(
        forward, strike, volatility, time_to_expiry
    )
    discount_factor = math.exp(-rate * time_to_expiry)
    return (
        discount_factor
        * normal_pdf(d1)
        / (forward * volatility * math.sqrt(time_to_expiry))
    )


def black76_vega(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
) -> float:
    d1, _ = calculate_d1_d2(
        forward, strike, volatility, time_to_expiry
    )
    discount_factor = math.exp(-rate * time_to_expiry)
    return (
        discount_factor
        * forward
        * normal_pdf(d1)
        * math.sqrt(time_to_expiry)
    )


def black76_theta(
    forward: float,
    strike: float,
    volatility: float,
    time_to_expiry: float,
    rate: float,
    option_type: str,
) -> float:
    d1, _ = calculate_d1_d2(
        forward, strike, volatility, time_to_expiry
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
    time_decay = (
        discount_factor
        * forward
        * normal_pdf(d1)
        * volatility
        / (2 * math.sqrt(time_to_expiry))
    )
    return rate * option_price - time_decay


def calculate_pnl_report(
    position: OptionPosition,
    previous_market: MarketState,
    current_market: MarketState,
) -> PnLReport:
    position_multiplier = position.quantity * position.contract_size
    previous_value = value_position(position, previous_market)
    current_value = value_position(position, current_market)
    exact_pnl = current_value - previous_value

    position_delta = black76_delta(
        previous_market.forward,
        position.strike,
        previous_market.volatility,
        previous_market.time_to_expiry,
        previous_market.rate,
        position.option_type,
    ) * position_multiplier
    position_gamma = black76_gamma(
        previous_market.forward,
        position.strike,
        previous_market.volatility,
        previous_market.time_to_expiry,
        previous_market.rate,
    ) * position_multiplier
    position_vega = black76_vega(
        previous_market.forward,
        position.strike,
        previous_market.volatility,
        previous_market.time_to_expiry,
        previous_market.rate,
    ) * position_multiplier
    position_theta = black76_theta(
        previous_market.forward,
        position.strike,
        previous_market.volatility,
        previous_market.time_to_expiry,
        previous_market.rate,
        position.option_type,
    ) * position_multiplier

    forward_change = current_market.forward - previous_market.forward
    volatility_change = (
        current_market.volatility - previous_market.volatility
    )
    elapsed_time = (
        previous_market.time_to_expiry
        - current_market.time_to_expiry
    )

    delta_pnl = position_delta * forward_change
    gamma_pnl = 0.5 * position_gamma * forward_change**2
    vega_pnl = position_vega * volatility_change
    theta_pnl = position_theta * elapsed_time
    explained_pnl = delta_pnl + gamma_pnl + vega_pnl + theta_pnl
    unexplained_pnl = exact_pnl - explained_pnl

    return PnLReport(
        previous_value=previous_value,
        current_value=current_value,
        exact_pnl=exact_pnl,
        delta_pnl=delta_pnl,
        gamma_pnl=gamma_pnl,
        vega_pnl=vega_pnl,
        theta_pnl=theta_pnl,
        explained_pnl=explained_pnl,
        unexplained_pnl=unexplained_pnl,
    )


def calculate_position_risk(
    position: OptionPosition,
    market: MarketState,
) -> RiskReport:
    position_multiplier = position.quantity * position.contract_size
    market_value = value_position(position, market)
    delta = black76_delta(
        market.forward,
        position.strike,
        market.volatility,
        market.time_to_expiry,
        market.rate,
        position.option_type,
    ) * position_multiplier
    gamma = black76_gamma(
        market.forward,
        position.strike,
        market.volatility,
        market.time_to_expiry,
        market.rate,
    ) * position_multiplier
    raw_vega = black76_vega(
        market.forward,
        position.strike,
        market.volatility,
        market.time_to_expiry,
        market.rate,
    ) * position_multiplier
    annual_theta = black76_theta(
        market.forward,
        position.strike,
        market.volatility,
        market.time_to_expiry,
        market.rate,
        position.option_type,
    ) * position_multiplier

    return RiskReport(
        market_value=market_value,
        delta=delta,
        gamma=gamma,
        vega_1pp=raw_vega / 100,
        theta_daily=annual_theta / 365,
    )


def calculate_portfolio_risk(
    positions: list[OptionPosition],
    markets: dict[str, MarketState],
) -> PortfolioRiskReport:
    rows: list[PositionRiskRow] = []
    total_market_value = 0.0
    total_delta = 0.0
    total_gamma = 0.0
    total_vega_1pp = 0.0
    total_theta_daily = 0.0

    for position in positions:
        if position.market_key not in markets:
            raise ValueError(
                f"Missing market data for {position.market_key}"
            )

        risk = calculate_position_risk(
            position=position,
            market=markets[position.market_key],
        )
        rows.append(
            PositionRiskRow(
                position_id=position.position_id,
                commodity=position.commodity,
                market_key=position.market_key,
                market_value=risk.market_value,
                delta=risk.delta,
                gamma=risk.gamma,
                vega_1pp=risk.vega_1pp,
                theta_daily=risk.theta_daily,
            )
        )
        total_market_value += risk.market_value
        total_delta += risk.delta
        total_gamma += risk.gamma
        total_vega_1pp += risk.vega_1pp
        total_theta_daily += risk.theta_daily

    return PortfolioRiskReport(
        rows=rows,
        market_value=total_market_value,
        delta=total_delta,
        gamma=total_gamma,
        vega_1pp=total_vega_1pp,
        theta_daily=total_theta_daily,
    )
