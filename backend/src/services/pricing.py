def suggested_price(cost: float, margin_percent: float) -> float:
    return round((cost or 0) * (1 + (margin_percent or 0) / 100), 2)
