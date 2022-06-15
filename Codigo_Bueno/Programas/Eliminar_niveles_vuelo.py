#%%
'''Eliminamos la evolucion de vuelo de cualquier sector (si es que los flujos tienen)'''
import os
import re
import json
import numpy
import geopy
import pandas
import pathlib
from geopy import distance
import shapely.geometry
from matplotlib import pyplot
from shapely.geometry import Polygon, Point, LineString, box

FILES_PATH = str(pathlib.Path(__file__).parent.resolve())

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

fich = pandas.read_csv(FILES_PATH + '\\Archivos\\poligonos_sectores_2D_2.0.csv', delimiter=';')
a = fich['PolygonToString']

b = re.split(",", a[5])
l = obtener_poligono(b)
poligono = Polygon(l)

j = input('Sector a cambiar: ')

with open(FILES_PATH + '\\JSON_Uniones\\LECMTLU_LECMCJI_Uniones.json', "r") as f6:
    datos = json.load(f6)
f6.close()

asociaciones = {}
datos_finales = {}
contador_flujos = 1

R = 1.86 * 15

for i in datos.keys():

    info = datos.get(i)[0]


    linea = LineString(numpy.array(info))
    nueva_linea = prolongar_recta(linea, poligono)
    intersecciones = nueva_linea.intersection(poligono.exterior)

    i1 = intersecciones[0]
    i1_x = i1.x
    i1_y = i1.y
    i1c = (i1_x, i1_y)

    i2 = intersecciones[len(intersecciones) - 1]
    i2_x = i2.x
    i2_y = i2.y
    i2c = (i2_x, i2_y)

    lis = []
    lis.append(i1c)
    lis.append(i2c)

    if len(datos_finales.keys()) == 0:
        contador_flujos += 1
        datos_finales.update({i: lis})
        listaa = []
        listaa.append(i)
        asociaciones.update({i: listaa})
    else:
        coordenadas_nuevas_entrada = []
        coordenadas_nuevas_salida = []

        coordenadas_nuevas_entrada.append(lis[0][1])
        coordenadas_nuevas_entrada.append(lis[0][0])
        coordenadas_nuevas_salida.append(lis[1][1])
        coordenadas_nuevas_salida.append(lis[1][0])
        coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)
        coordenadas_nuevas_salida = tuple(coordenadas_nuevas_salida)

        comprobacion = 0
        posibles_f = None
        de_max = -1
        ds_max = -1

        for L in datos_finales.keys():

            linea = LineString(numpy.array(datos_finales.get(L)))
            nueva_linea = prolongar_recta(linea, poligono)
            intersecciones2 = nueva_linea.intersection(poligono.exterior)

            i1 = intersecciones2[0]
            i1_x = i1.x
            i1_y = i1.y
            i1c = (i1_x, i1_y)

            i2 = intersecciones2[len(intersecciones2) - 1]
            i2_x = i2.x
            i2_y = i2.y
            i2c = (i2_x, i2_y)

            lis2 = []
            lis2.append(i1c)
            lis2.append(i2c)

            c_n_e = []
            c_n_s = []

            c_n_e.append(lis2[0][1])
            c_n_e.append(lis2[0][0])
            c_n_s.append(lis2[1][1])
            c_n_s.append(lis2[1][0])

            c_n_e = tuple(c_n_e)
            c_n_s = tuple(c_n_s)

            d_e = geopy.distance.distance(c_n_e, coordenadas_nuevas_entrada).km
            d_s = geopy.distance.distance(c_n_s, coordenadas_nuevas_salida).km
            if d_e < R and d_s < R:
                if (de_max == -1 and ds_max == -1) or (d_e < de_max and d_s < ds_max):
                    de_max = d_e
                    ds_max = d_s
                    posibles_f = L

        if posibles_f == None:
            coordenadas = info
            contador_flujos += 1
            datos_finales.update({i: coordenadas})
            listaa = []
            listaa.append(i)
            asociaciones.update({i: listaa})
        else:
            flujo_nuevo = datos_finales.get(posibles_f)
            c_n_e = []
            c_n_s = []

            c_n_e.append(flujo_nuevo[0][1])
            c_n_e.append(flujo_nuevo[0][0])
            c_n_s.append(flujo_nuevo[1][1])
            c_n_s.append(flujo_nuevo[1][0])

            c_n_e = tuple(c_n_e)
            c_n_s = tuple(c_n_s)

            entrada_media_1 = (c_n_e[1] + coordenadas_nuevas_entrada[1]) / 2
            entrada_media_2 = (c_n_e[0] + coordenadas_nuevas_entrada[0]) / 2
            salida_media_1 = (c_n_s[1] + coordenadas_nuevas_salida[1]) / 2
            salida_media_2 = (c_n_s[0] + coordenadas_nuevas_salida[0]) / 2

            d1 = []
            d1.append(entrada_media_1)
            d1.append(entrada_media_2)
            d2 = []
            d2.append(salida_media_1)
            d2.append(salida_media_2)
            d1 = tuple(d1)
            d2 = tuple(d2)

            tupla = (d1, d2)
            datos_finales[posibles_f] = tupla
            lista = asociaciones.get(posibles_f)
            lista.append(i)
            asociaciones[posibles_f] = lista


print(len(datos.keys()))
print(len(datos_finales.keys()))

with  open(FILES_PATH + "\\Carpeta_JSON\\Clusterizados_SinEv_" + j + ".json", "w") as f6:
    json.dump(datos_finales, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\Carpeta_JSON\\Reestructurados_" + j + ".json", "w") as f6:
    json.dump(asociaciones, f6, indent=4)
f6.close()
