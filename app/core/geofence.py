from shapely.geometry import Point, Polygon

from app.core.config import settings


if settings.REGION_POINTS and len(settings.REGION_POINTS) >= 3:
    REGION_POLYGON = Polygon(settings.REGION_POINTS)
else:
    REGION_POLYGON = None

def is_inside_region(lon: float | None, lat: float | None) -> bool:
    if (lon is None) or (lat is None) or (REGION_POLYGON is None):
        return False

    point = Point(lon, lat)
    return REGION_POLYGON.contains(point)