import shapely
from shapely.geometry import Polygon

p = [(4.0, 2.0), (2.0, 5.0), (7.0, 8.0), (0.0, 10.0)]
poligono = shapely.geometry.Polygon([[4.0, 2.0], [2.0, 5.0], [7.0, 8.0], [0.0, 10.0]])

print(poligono.area)