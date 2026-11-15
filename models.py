from dataclasses import dataclass

@dataclass
class OptionPosition:
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