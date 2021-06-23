import pandas
import csv
from pyproj import Proj
import geopy.distance
from math import sin, cos, sqrt, atan2, radians

R = 6373.0


#data = pandas.read_excel("D:\\Trabajo_Universidad\\Ficheros\\flujos2.xlsx")
#n = data['avg_latIN']
#m = data['avg_lngIN']

p = Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=False)
x , y = p(1.92482, 40.6927861)
p2 = Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=False)
xx, yy = p2(1.894738056, 40.76441639)
print(x ,y)
print(xx, yy)
pos = ((xx - x) ** 2 + (yy - y) ** 2) ** 0.5
print(pos/1000)

print('----------------')

c1 = (40.6927861, 1.92482)
c2 = (40.76441639, 1.894738556)

print(geopy.distance.distance(c1, c2).km)

print('----------------')

lat1 = radians(40.6927861)
lon1 = radians(1.92482)
lat2 = radians(40.76441639)
lon2 = radians(1.894738556)

dlat = lat2 - lat1
dlon = lon2 - lon1

a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
c = 2*atan2(sqrt(a), sqrt(1-a))

distance = R * c

print(distance)