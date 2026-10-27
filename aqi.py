"""CPCB PM2.5 sub-index and AQI category helpers."""

BP = [
    (0, 30, 0, 50),
    (31, 60, 51, 100),
    (61, 90, 101, 200),
    (91, 120, 201, 300),
    (121, 250, 301, 400),
    (251, 500, 401, 500),
]

def pm25_subindex(c):
    """Linear interpolation between CPCB PM2.5 breakpoints."""
    if c is None:
        return None
    c = float(c)
    for cl, ch, il, ih in BP:
        if cl <= c <= ch:
            return round((ih - il) / (ch - cl) * (c - cl) + il)
    return 500 if c > 500 else None

def aqi_category(aqi):
    if aqi is None:
        return "Unknown"
    aqi = float(aqi)
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Satisfactory"
    if aqi <= 200: return "Moderate"
    if aqi <= 300: return "Poor"
    if aqi <= 400: return "Very Poor"
    return "Severe"
