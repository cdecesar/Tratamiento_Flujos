#%%
import re
import json
import pandas
import pathlib
import shapely
import geopy.distance
from matplotlib import pyplot
from shapely.geometry import Polygon
FILES_PATH = str(pathlib.Path(__file__).parent.resolve())
from shapely.geometry import Polygon, Point, LineString, box

def prolongar_recta(linea, poligono):
    minx, miny, maxx, maxy = poligono.bounds
    bounding_box = box(minx, miny, maxx, maxy)

    a, b = linea.boundary
    if a.x == b.x:  # vertical line
        extended_line = LineString([(a.x, miny), (a.x, maxy)])
    elif a.y == b.y:  # horizonthal line
        extended_line = LineString([(minx, a.y), (maxx, a.y)])
    else:
        # linear equation: y = k*x + m
        k = (b.y - a.y) / (b.x - a.x)
        m = a.y - k * a.x
        y0 = k * minx + m
        y1 = k * maxx + m
        x0 = (miny - m) / k
        x1 = (maxy - m) / k
        points_on_boundary_lines = [Point(minx, y0), Point(maxx, y1),
                                    Point(x0, miny), Point(x1, maxy)]
        points_sorted_by_distance = sorted(points_on_boundary_lines, key=bounding_box.distance)
        extended_line = LineString(points_sorted_by_distance[:2])

    return extended_line

'''Estos son los csv que sacamos de la creacion de flujos. Ya estan en cada uno separado por secotres. No hace falta hacer loc del SectorCode'''
base_datos1 = pandas.read_csv("C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\Base_Datos_Principal.csv", delimiter=';')
datos1 = base_datos1.loc[:,['flightkey','routeKey','adep','ades','lat_IN','lat_OUT', 'lng_IN', 'lng_OUT', 'attitud_IN', 'attitud_OUT', 'callsign', 'vel_z_IN', 'vel_z_OUT']]

base_datos2 = pandas.read_csv("C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\Base_Datos_Principal.csv", delimiter=';')
datos2 = base_datos2.loc[:,['flightkey','routeKey','adep','ades','lat_IN','lat_OUT', 'lng_IN', 'lng_OUT', 'attitud_IN', 'attitud_OUT', 'callsign', 'vel_z_IN', 'vel_z_OUT']]

datos2.rename({'Flujo_Original': 'Flujo_Original2', 'Flujo_Clusterizado': 'Flujo_Clusterizado2'}, axis=1)

''' Este es el sector 1
df1 = base_datos1.loc[base_datos1.SectorCode=='LECMCJI',:]

Este es el sector 2
df2 = base_datos2.loc[base_datos2.SectorCode=='LECMPAU',:]'''

'''Puntos de Insignia'''
fichero2 = pandas.read_csv('C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\Puntos.csv', delimiter=',')
nombres = fichero2['IDENT_TXT']
latitud = fichero2['LAT_TXT']
longitud = fichero2['LONG_TXT']

with  open(FILES_PATH + "\\JSON_Cargados\\Barcelona\\Clusterizados_LECBP2R.json", "r") as f6:
    flujos1 = json.load(f6)
f6.close()

with  open(FILES_PATH + "\\JSON_Cargados\\Barcelona\\Clusterizados_LECBP2R.json", "r") as f6:
    flujos2 = json.load(f6)
f6.close()

dataframe_unido = datos1.merge(datos2, left_on=['flightkey'], right_on=['flightkey'], how='inner')

c = 0
n = dataframe_unido['flightkey']
contador = dataframe_unido.index[c]
contador2 = 0

#%%

def obtener_poligono(b):
    l = []
    c = 0
    while c < len(b):
        if c == 0:
            p = b[0][10:]
            k = re.split("\s", p)
            k[0] = float(k[0])
            k[1] = float(k[1])
            k = tuple(k)
            l.append(k)
        elif c < (len(b) - 1):
            p = b[c]
            k = re.split("\s", p)
            k.pop(0)
            k[0] = float(k[0])
            k[1] = float(k[1])
            k = tuple(k)
            l.append(k)
        else:
            p = b[c][:-2]
            k = re.split("\s", p)
            k.pop(0)
            k[0] = float(k[0])
            k[1] = float(k[1])
            k = tuple(k)
            l.append(k)
        c += 1

    return l

path_poligono = 'C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\poligonos_sectores_2D_2.0.csv'

fich = pandas.read_csv(path_poligono, delimiter=';')
a = fich['PolygonToString']

'''Primer Sector'''
b = re.split(",", a[4])
l = obtener_poligono(b)
poligono1 = Polygon(l)
b = re.split(",", a[4])
l = obtener_poligono(b)
poligono2 = Polygon(l)

bloc = open(FILES_PATH + "\\ola.txt", "w")

parejas_flujos = []

while contador2 < n.size:
    f1 = dataframe_unido['Flujo_Clusterizado'][contador]
    f2 = dataframe_unido['Flujo_Clusterizado2'][contador]

    l = []
    l.append(f1)
    l.append(f2)
    l = tuple(l)

    if l not in parejas_flujos:
        parejas_flujos.append(l)
        bloc.write("Nueva pareja de flujos entre sectores -> " + str(l) + "\n")

    if (contador2 + 1) == n.size:
        break
    else:
        c += 1
        contador = dataframe_unido.index[c]
        contador2 += 1
#%%
uniones = {}
interseccion = poligono1.intersection(poligono2)
for i in parejas_flujos:
    a = i[0]
    b = i[1]

    f1 = flujos1.get(a)[0]
    f2 = flujos2.get(b)[0]

    clave = str(a) + '_' + str(b)

    punto_1_entrada = Point(f1[0])
    punto_1_salida = Point(f1[1])
    punto_2_entrada = Point(f2[0])
    punto_2_salida = Point(f2[1])

    distancia1_e = punto_1_entrada.distance(interseccion)
    distancia1_s = punto_1_salida.distance(interseccion)
    distancia2_e = punto_2_entrada.distance(interseccion)
    distancia2_s = punto_2_salida.distance(interseccion)
    d_1_min = min(distancia1_e, distancia1_s)
    d_2_min = min(distancia2_e, distancia2_s)

    punto_cercano1 = None
    punto_lejano1 = None
    punto_cercano2 = None
    punto_lejano2 = None

    if d_1_min == distancia1_e:
        punto_cercano1 = f1[0]
        punto_lejano1 = f1[1]
    else:
        punto_cercano1 = f1[1]
        punto_lejano1 = f1[0]

    if d_2_min == distancia2_e:
        punto_cercano2 = f2[0]
        punto_lejano2 = f2[1]
    else:
        punto_cercano2 = f2[1]
        punto_lejano2 = f2[0]

    l1 = LineString(punto_cercano1, punto_lejano1)
    l2 = LineString(punto_cercano2, punto_lejano2)

    if l1.intersects(interseccion) == True and l2.intersects(interseccion) == True:

        media_lat = (punto_cercano1[1] + punto_cercano2[1]) / 2
        media_lon = (punto_cercano1[0] + punto_cercano2[0]) / 2
        t = (media_lon, media_lat)

        l1 = LineString(t, punto_lejano1)
        l2 = LineString(t, punto_lejano2)

    elif (l1.intersects(interseccion) == False and l2.intersects(interseccion) == True):
        l1 = LineString(punto_cercano2, punto_lejano1)
        l2 = LineString(punto_cercano2, punto_lejano2)
    elif (l1.intersects(interseccion) == True and l2.intersects(interseccion) == False):
        l1 = LineString(punto_cercano1, punto_lejano1)
        l2 = LineString(punto_cercano1, punto_lejano2)
    else:

        nuevalinea1 = prolongar_recta(l1, poligono1)
        nuevalinea2 = prolongar_recta(l2, poligono2)
        corte1 = nuevalinea1.intersection(interseccion)
        corte2 = nuevalinea2.intersection(interseccion)

        punto_1_entrada = nuevalinea1.boundary[0]
        punto_1_salida = nuevalinea1.boundary[1]
        punto_2_entrada = nuevalinea2.boundary[0]
        punto_2_salida = nuevalinea2.boundary[1]

        distancia1_e = punto_1_entrada.distance(corte1)
        distancia1_s = punto_1_salida.distance(corte1)
        distancia2_e = punto_2_entrada.distance(corte2)
        distancia2_s = punto_2_salida.distance(corte2)
        d_1_min = min(distancia1_e, distancia1_s)
        d_2_min = min(distancia2_e, distancia2_s)

        punto_lejano1 = None
        punto_lejano2 = None

        if d_1_min == distancia1_e:
            punto_lejano1 = punto_1_salida
        else:
            punto_lejano1 = punto_1_entrada

        if d_2_min == distancia2_e:
            punto_lejano2 = punto_2_salida
        else:
            punto_lejano2 = punto_2_entrada

        if nuevalinea1.intersects(interseccion) == True and nuevalinea2.intersects(interseccion) == True:

            media_lat = (corte1.y + corte2.y) / 2
            media_lon = (corte1.x + corte2.x) / 2
            t = (media_lon, media_lat)

            l1 = LineString([t, punto_lejano1])
            l2 = LineString([t, punto_lejano2])

        elif (nuevalinea1.intersects(interseccion) == False and nuevalinea2.intersects(interseccion) == True):
            l1 = LineString([corte2, punto_lejano1])
            l2 = LineString([corte2, punto_lejano2])
        elif (nuevalinea1.intersects(interseccion) == True and nuevalinea2.intersects(interseccion) == False):
            l1 = LineString([corte1, punto_lejano1])
            l2 = LineString([corte1, punto_lejano2])
        else:
            pass

    cords1 = []
    cords2 = []
    lista1 = []
    lista2 = []
    lista3 = []
    lista4 = []

    lista1.append(l1.bounds[0])
    lista1.append(l1.bounds[1])
    lista2.append(l1.bounds[2])
    lista2.append(l1.bounds[3])

    cords1.append(lista1)
    cords1.append(lista2)

    lista3.append(l2.bounds[0])
    lista3.append(l2.bounds[1])
    lista4.append(l2.bounds[2])
    lista4.append(l2.bounds[3])

    cords2.append(lista3)
    cords2.append(lista4)

    info_union = []
    info_union.append(cords1)
    info_union.append(cords2)

    uniones.update({clave: info_union})

    x,y = l1.xy
    pyplot.plot(x,y)
    x2, y2 = l2.xy
    pyplot.plot(x2, y2)


    x3, y3 = poligono1.exterior.xy
    x4, y4 = poligono2.exterior.xy
    pyplot.plot(x3, y3)
    pyplot.plot(x4, y4)

    pyplot.show()


with  open(FILES_PATH + "\\JSON_Cargados\\Canarias\\Tipo1_GCCCRNE.json", "w") as f7:
    json.dump(uniones, f7, indent=4)
f7.close()