import math


def calculate_geo_distance(lat1, lon1, lat2, lon2) -> float:
    """
    Calculates the distance in meters between two points on the Earth.
    """
    # Radius of the Earth in meters
    R = 6371000 
    
    # Conversion of degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in meters

