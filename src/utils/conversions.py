

def ms_to_kmh(meters_per_second: float) -> float:
    """
    Converts a speed from meters per second to kilometers per hour.

    Parameters:
        meters_per_second : float (The speed in meters per second)

    Returns
        float (The equivalent speed in kilometers per hour.)

    Examples
    --------
    >>> ms_to_kmh(10)
    36.0
    """
    return ((meters_per_second * 60) * 60) / 1000

if __name__ == "__main__":
    print(ms_to_kmh(10))