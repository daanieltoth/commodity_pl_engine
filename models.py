from dataclasses import dataclass


@dataclass
class OptionPosition:
    position_id: str
    commodity: str
    market_key: str
    strike: float
    option_type: str
    quantity: int
    contract_size: float


@dataclass
class MarketState:
    forward: float
    volatility: float
    time_to_expiry: float
    rate: float


@dataclass
class PnLReport:
    previous_value: float
    current_value: float
    exact_pnl: float
    delta_pnl: float
    gamma_pnl: float
    vega_pnl: float
    theta_pnl: float
    explained_pnl: float
    unexplained_pnl: float


@dataclass
class RiskReport:
    market_value: float
    delta: float
    gamma: float
    vega_1pp: float
    theta_daily: float


@dataclass
class PositionRiskRow:
    position_id: str
    commodity: str
    market_key: str
    market_value: float
    delta: float
    gamma: float
    vega_1pp: float
    theta_daily: float


@dataclass
class PortfolioRiskReport:
    rows: list[PositionRiskRow]
    market_value: float
    delta: float
    gamma: float
    vega_1pp: float
    theta_daily: float
