import re
import json
import numpy
import pandas
import pathlib
import shapely
import geopy.distance
from matplotlib import pyplot
from shapely.geometry import Polygon
FILES_PATH = str(pathlib.Path(__file__).parent.resolve())
from shapely.geometry import Polygon, Point, LineString, box
def obtener_poligono(b):
    '''Obtener la forma del poligono'''
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

    return numpy.array(l)

def prolongar_recta(linea, poligono):
    '''Prolongar las rectas para ver como cortan con los sectores'''
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

def funcion1():
    for i in datos.keys():
        a = re.split("-", i)

        if a[0] in datos3.keys() and a[1] in datos2.keys():
            L1 = LineString(datos3.get(a[0])[0])
            L2 = LineString(datos2.get(a[1])[0])

            x, y = L1.xy
            pyplot.plot(x, y)
            x, y = L2.xy
            pyplot.plot(x, y)

    x3, y3 = poligono1.exterior.xy
    x4, y4 = poligono2.exterior.xy
    pyplot.plot(x3, y3)
    pyplot.plot(x4, y4)
    pyplot.show()


def funcion2():
    for i in datos.keys():
        a = re.split("-", i)

        if a[0] in datos3.keys() and a[1] in datos2.keys():

            flujo1 = datos3.get(a[0])[0]
            flujo2 = datos2.get(a[1])[0]

            try:
                punto_1_entrada = Point(flujo1[0])
                punto_1_salida = Point(flujo1[1])
                punto_2_entrada = Point(flujo2[0])
                punto_2_salida = Point(flujo2[1])
            except:
                print(a[0])
                print(a[1])

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
                punto_cercano1 = flujo1[0]
                punto_lejano1 = flujo1[1]
            else:
                punto_cercano1 = flujo1[1]
                punto_lejano1 = flujo1[0]

            if d_2_min == distancia2_e:
                punto_cercano2 = flujo2[0]
                punto_lejano2 = flujo2[1]
            else:
                punto_cercano2 = flujo2[1]
                punto_lejano2 = flujo2[0]

            punto_cercano1 = tuple(punto_cercano1)
            punto_cercano2 = tuple(punto_cercano2)
            punto_lejano1 = tuple(punto_lejano1)
            punto_lejano2 = tuple(punto_lejano2)

            l1 = LineString(numpy.array([punto_cercano1, punto_lejano1]))
            l2 = LineString(numpy.array([punto_cercano2, punto_lejano2]))

            if l1.intersects(interseccion) == True and l2.intersects(interseccion) == True:

                media_lat = (punto_cercano1[1] + punto_cercano2[1]) / 2
                media_lon = (punto_cercano1[0] + punto_cercano2[0]) / 2
                t = (media_lon, media_lat)

                punto_cercano1 = tuple(punto_cercano1)
                punto_cercano2 = tuple(punto_cercano2)
                punto_lejano1 = tuple(punto_lejano1)
                punto_lejano2 = tuple(punto_lejano2)

                l1 = LineString(numpy.array([t, punto_lejano1]))
                l2 = LineString(numpy.array([t, punto_lejano2]))

            elif (l1.intersects(interseccion) == False and l2.intersects(interseccion) == True):
                punto_cercano1 = tuple(punto_cercano1)
                punto_cercano2 = tuple(punto_cercano2)
                punto_lejano1 = tuple(punto_lejano1)
                punto_lejano2 = tuple(punto_lejano2)

                l1 = LineString(numpy.array([punto_cercano2, punto_lejano1]))
                l2 = LineString(numpy.array([punto_cercano2, punto_lejano2]))

            elif (l1.intersects(interseccion) == True and l2.intersects(interseccion) == False):
                punto_cercano1 = tuple(punto_cercano1)
                punto_cercano2 = tuple(punto_cercano2)
                punto_lejano1 = tuple(punto_lejano1)
                punto_lejano2 = tuple(punto_lejano2)

                l1 = LineString(numpy.array([punto_cercano1, punto_lejano1]))
                l2 = LineString(numpy.array([punto_cercano1, punto_lejano2]))

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

                elif nuevalinea1.intersects(interseccion) == False and nuevalinea2.intersects(interseccion) == True:
                    l1 = LineString([corte2, punto_lejano1])
                    l2 = LineString([corte2, punto_lejano2])
                elif nuevalinea1.intersects(interseccion) == True and nuevalinea2.intersects(interseccion) == False:
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

            # Lista 1 tiene las coordenadas de entrada
            lista1.append(l1.bounds[0])
            lista1.append(l1.bounds[1])
            lista2.append(l1.bounds[2])
            lista2.append(l1.bounds[3])

            cords1.append(tuple(lista1))
            cords1.append(tuple(lista2))

            # Lista 2 tiene coordenadas de salida
            lista3.append(l2.bounds[0])
            lista3.append(l2.bounds[1])
            lista4.append(l2.bounds[2])
            lista4.append(l2.bounds[3])

            cords2.append(tuple(lista3))
            cords2.append(tuple(lista4))

            info_union = []
            info_union.append(cords1)
            info_union.append(cords2)

            x, y = l1.xy
            pyplot.plot(x, y)
            x2, y2 = l2.xy
            pyplot.plot(x2, y2)

    x3, y3 = poligono1.exterior.xy
    x4, y4 = poligono2.exterior.xy
    pyplot.plot(x3, y3)
    pyplot.plot(x4, y4)
    pyplot.show()


#%%
with open(FILES_PATH + '\\JSON_Uniones\\LECMTLU_LECMCJI_Uniones.json', "r") as f6:
    datos = json.load(f6)
f6.close()
with open(FILES_PATH + '\\Carpeta_JSON\\Clusterizados3_LECMCJI.json', "r") as f6:
    datos2 = json.load(f6)
f6.close()
with open(FILES_PATH + '\\Carpeta_JSON\\Clusterizados3_LECMTLU.json', "r") as f6:
    datos3 = json.load(f6)
f6.close()
numero = 0
path_poligono = FILES_PATH + '\\Archivos\\poligonos_sectores_2D_2.0.csv'
fich = pandas.read_csv(path_poligono, delimiter=';')
a = fich['PolygonToString']
b = re.split(",", a[4])
l = obtener_poligono(b)
poligono1 = Polygon(l)
b = re.split(",", a[8])
l = obtener_poligono(b)
poligono2 = Polygon(l)

interseccion = poligono1.intersection(poligono2)
f = input('Funcion para dibujar: ')
if f == 'funcion1':
    funcion1()
else:
    funcion2()
