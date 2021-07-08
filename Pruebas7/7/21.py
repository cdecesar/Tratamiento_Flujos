import pandas
import geopy.distance
import re

import shapely
from matplotlib import pyplot
from shapely.geometry import Polygon, Point, LineString, box
#from PATH import PATH

fichero1 = pandas.read_excel("C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Documento_Flujos.xlsx")
fichero2 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Puntos.xlsx')
fichero3 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Radioayudas.xlsx')
fichero4 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Poligono_Pamplona.xlsx')
fichero_tabla1 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Tabla1.xlsx')
fichero_tabla2 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Tabla2.xlsx')

def buscar_corte_cercano(d1, flujo, inter, n, d2, coordenadas, modo):

    contador_cortes = 0
    p = d1.get(flujo[0])
    primero = []
    primero.append(p[1])
    primero.append(p[0])
    primero = tuple(primero)

    u = d1.get(flujo[len(flujo) - 1])
    ultimo = []
    ultimo.append(u[1])
    ultimo.append(u[0])
    ultimo = tuple(ultimo)

    cerca_primero = 0
    cerca_ultimo = 0

    d_cerca_p = 0
    d_cerca_u = 0

    if isinstance(inter, shapely.geometry.multipoint.MultiPoint):
        g = len(inter)
    else:
        g = 1

    while contador_cortes < g:
        if isinstance(inter, shapely.geometry.multipoint.MultiPoint):
            c = inter[contador_cortes]
        else:
            c = inter
        punto = []
        punto.append(c.y)
        punto.append(c.x)
        punto = tuple(punto)

        d_primero = geopy.distance.distance(primero, punto).km
        d_ultimo = geopy.distance.distance(ultimo, punto).km
        if cerca_primero == 0 or d_cerca_p > d_primero:
            cerca_primero = punto
            d_cerca_p = d_primero
        if cerca_ultimo == 0 or d_cerca_u > d_ultimo:
            cerca_ultimo = punto
            d_cerca_u = d_ultimo

        contador_cortes += 1

    cerca_primero2 = []
    cerca_primero2.append(cerca_primero[1])
    cerca_primero2.append(cerca_primero[0])
    cerca_primero2 = tuple(cerca_primero2)
    cerca_ultimo2 = []
    cerca_ultimo2.append(cerca_ultimo[1])
    cerca_ultimo2.append(cerca_ultimo[0])
    cerca_ultimo2 = tuple(cerca_ultimo2)

    if modo == 2:
        coordenadas.append("Punto" + str(n))
        diccionario2.update({"Punto" + str(n): cerca_primero2})
        n += 1
        coordenadas.append("Punto" + str(n))
        diccionario2.update({"Punto" + str(n): cerca_ultimo2})
        n += 1
    elif modo == 1:
        coordenadas.append("Punto" + str(n))
        diccionario2.update({"Punto" + str(n): cerca_primero2})
        n += 1
    else:
        coordenadas.append("Punto" + str(n))
        diccionario2.update({"Punto" + str(n): cerca_ultimo2})
        n += 1
    datos = {routeKey: coordenadas}
    d2.update(datos)
    return n


def determinar_punto_entrada_salida(puntos, entrada):

    x1 = puntos[0].x
    y1 = puntos[0].y
    tupla1 = (y1, x1)

    x2 = puntos[1].x
    y2 = puntos[1].y
    tupla2 = (y2, x2)

    ent = []
    ent.append(entrada[1])
    ent.append(entrada[0])
    ent = tuple(ent)

    distancia_1 = geopy.distance.distance(ent, tupla1).km
    distancia_2 = geopy.distance.distance(ent, tupla2).km

    if distancia_1 < distancia_2:
        return puntos[0]
    else:
        return puntos[1]

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

def sacar_coordenadas(nombres, latitud, longitud, c, lista, diccionario):

    contador = c
    for nombre in nombres:

        if nombre in lista:
            lat = 0
            lon = 0

            g = 0
            m = 0
            s = 0
            s2 = ""
            l = ""

            if latitud[contador][0] != 0:
                g = float(latitud[contador][:2])
                m = float(latitud[contador][2:4])
                s = (latitud[contador][4:len(latitud[contador]) - 1])
                l = latitud[contador][-1]
            else:
                g = float(latitud[contador][:3])
                m = float(latitud[contador][3:5])
                s = (latitud[contador][5:len(latitud[contador]) - 1])
                l = latitud[contador][-1]

            for i in s:
                if i == ",":
                    i = "."
                s2 += i

            s2 = float(s2)

            lat = g + (m / 60) + (s2 / 3600)
            if (l == "W") or (l == "S"):
                lat *= -1

            g = 0
            m = 0
            s = 0
            l = ""
            s2 = ""
            if len(longitud[contador]) == 7:
                g = float(longitud[contador][:2])
                m = float(longitud[contador][2:4])
                s = (longitud[contador][4:6])
                l = longitud[contador][-1]
            else:
                g = float(longitud[contador][:3])
                m = float(longitud[contador][3:5])
                s = (longitud[contador][5:len(longitud[contador]) - 1])
                l = longitud[contador][-1]

            for i in s:
                if i == ",":
                    i = "."
                s2 += i

            s2 = float(s2)

            lon = g + (m / 60) + (s2 / 3600)
            if (l == "W") or (l == "S"):
                lon *= -1

            datos = {nombre: [lon, lat]}
            diccionario.update(datos)

        contador += 1

def sacar_coordenadas_2(lista, diccionario):

    for cord in lista:
        if len(cord) > 6:
            lat = cord[:5]
            lon = cord[5:]
            s = ""
            indice = 0
            for caracter in lat:
                if indice == 1:
                    s += caracter
                    s += "."
                    indice += 1
                else:
                    s += caracter
                    indice += 1
            lat = s

            s = ""
            indice = 0
            si = False
            for caracter in lon:
                if si == False:
                    if caracter == "0":
                        s += caracter
                        indice += 1
                    else:
                        if indice == 2:
                            s += caracter
                            s += "."
                            si = True
                        if indice == 3:
                            s += "."
                            s += caracter
                            si = True
                else:
                    s += caracter
            lon = s

            sig_lat = lat[-1]
            lat = lat[:4]
            lat = float(lat)

            sig_lon = lon[-1]
            lon = lon[:len(lon) - 1]
            lon = float(lon)

            if sig_lon == "W":
                lon = lon * (-1)
            if sig_lat == "S":
                lat = lat * (-1)

            datos = {cord: [lon, lat]}
            diccionario.update(datos)

def sacar_coordenadas_poligono(puntos, dicct, lista):
    contador_vertices = 0
    for point in puntos:
        lat = 0
        lon = 0

        g = 0
        m = 0
        s = 0
        s2 = ""
        l = ""

        if latitud_P[contador_vertices][0] != 0:
            g = float(latitud_P[contador_vertices][:2])
            m = float(latitud_P[contador_vertices][2:4])
            s = (latitud_P[contador_vertices][4:len(latitud_P[contador_vertices]) - 1])
            l = latitud_P[contador_vertices][-1]
        else:
            g = float(latitud_P[contador_vertices][:3])
            m = float(latitud_P[contador_vertices][3:5])
            s = (latitud_P[contador_vertices][5:len(latitud_P[contador_vertices]) - 1])
            l = latitud_P[contador_vertices][-1]

        for i in s:
            if i == ",":
                i = "."
            s2 += i

        s2 = float(s2)

        lat = g + (m / 60) + (s2 / 3600)
        if (l == "W") or (l == "S"):
            lat *= -1

        g = 0
        m = 0
        s = 0
        l = ""
        s2 = ""
        if len(longitud_P[contador_vertices]) == 7:
            g = float(longitud_P[contador_vertices][:2])
            m = float(longitud_P[contador_vertices][2:4])
            s = (longitud_P[contador_vertices][4:6])
            l = longitud_P[contador_vertices][-1]
        else:
            g = float(longitud_P[contador_vertices][:3])
            m = float(longitud_P[contador_vertices][3:5])
            s = (longitud_P[contador_vertices][5:len(longitud_P[contador_vertices]) - 1])
            l = longitud_P[contador_vertices][-1]

        for i in s:
            if i == ",":
                i = "."
            s2 += i

        s2 = float(s2)

        lon = g + (m / 60) + (s2 / 3600)
        if (l == "W") or (l == "S"):
            lon *= -1

        datos_vertice = {point: [lon, lat]}
        lista.append(tuple([lon, lat]))
        dicct.update(datos_vertice)
        contador_vertices += 1

rutas = fichero1['routeKey']
fila_nombres = fichero1['rutaExtend']
sector = fichero1['SectorCode']
forma_entrada = fichero1['attitud_IN']
forma_salida = fichero1['attitud_OUT']
puntos_no_queremos = ['HERMI', 'D104', 'MITUM', 'ADEDI']
lista_mal = []

contador_1 = 0
lista_nombres = []
dicct_flujo_puntos_clave = {}

while contador_1 < fila_nombres.size:
    if sector[contador_1] == 'LECMPAU':
        flujo_completo = fila_nombres[contador_1]
        palabra = re.split("-", flujo_completo)
        lista_aux = []
        #lista_aux.append(palabra)
        for i in palabra:
            if i not in puntos_no_queremos:
                lista_aux.append(i)

        if len(lista_aux) > 1:
            info = {rutas[contador_1]: lista_aux}
            dicct_flujo_puntos_clave.update(info)
            for n in palabra:
                if n not in lista_nombres:
                    lista_nombres.append(n)

    contador_1 += 1

nombres = fichero2['IDENT_TXT']
latitud = fichero2['LAT_TXT']
longitud = fichero2['LONG_TXT']
contador2 = 0
diccionario = {}
sacar_coordenadas(nombres, latitud, longitud, contador2, lista_nombres, diccionario)
print(diccionario.get("DONOS"))
print(diccionario.get("BANEV"))
for i in lista_nombres:
    if i not in diccionario.keys():
        lista_mal.append(i)

radioayudas = fichero3['IDENT_TXT']
lat_radioayudas = fichero3['LAT_TXT']
lon_radioayudas = fichero3['LONG_TXT']
contador3 = 0

sacar_coordenadas(radioayudas,lat_radioayudas, lon_radioayudas, contador3, lista_mal, diccionario)

for i in lista_mal:
    if i in diccionario.keys():
        lista_mal.remove(i)

sacar_coordenadas_2(lista_mal, diccionario)

dicct_poligono_P = {}
lista_vertices = []
nombre = fichero4['Point']
latitud_P = fichero4['Lattitude_TXT']
longitud_P = fichero4['Longitude_TXT']

sacar_coordenadas_poligono(nombre, dicct_poligono_P, lista_vertices)
poligono = Polygon(lista_vertices)
x, y = poligono.exterior.xy
pyplot.plot(x, y)

#o = ['4155N00107W', 'ARVID']
#e = []
#for i in o:
#    e.append(tuple(diccionario.get(i)))
#linea_rara = LineString(e)
#print(linea_rara)
#ln = prolongar_recta(linea_rara, poligono)
#xx, yy = ln.xy
#ln2 = ln.intersection(poligono.exterior)
#print(ln2)
#print(type(ln2))
#print(list(ln2[2].coords))
#pyplot.plot(xx, yy)
#pyplot.show()

n_punto = 1
diccionario2 = {}
diccionario_nuevos_flujos = {}
flujos_con_problemas_cortes = []



for routeKey in dicct_flujo_puntos_clave.keys():
    flujo = dicct_flujo_puntos_clave.get(routeKey)
    coordenadas_r = []
    datos_recta = []
    for i in flujo:
        datos_recta.append(tuple(diccionario.get(i)))

    entrada = Point(diccionario.get(flujo[0]))
    salida = Point(diccionario.get(flujo[len(flujo) - 1]))

    if routeKey == 100487:
        datos_recta2 = []
        for i in flujo:
            if i != '4301N00111W':
                datos_recta2.append(tuple(diccionario.get(i)))

        linea = LineString(datos_recta2)
        intersecciones = linea.intersection(poligono.exterior)
        cortes = []

        contador_cortes = 0
        p = diccionario.get(flujo[0])
        primero = []
        primero.append(p[1])
        primero.append(p[0])
        primero = tuple(primero)

        cerca_primero = 0
        d_cerca_p = 0

        u = diccionario.get(flujo[len(flujo) - 1])
        ultimo = []
        ultimo.append(u[1])
        ultimo.append(u[0])
        ultimo = tuple(ultimo)

        cerca_ultimo = 0
        d_cerca_u = 0

        while contador_cortes < len(intersecciones):
            c = intersecciones[contador_cortes]
            punto = []
            punto.append(c.y)
            punto.append(c.x)
            punto = tuple(punto)

            d_primero = geopy.distance.distance(primero, punto).km
            if cerca_primero == 0 or d_cerca_p > d_primero:
                cerca_primero = punto
                d_cerca_p = d_primero

            contador_cortes += 1

        contador_cortes = 0
        while contador_cortes < len(intersecciones):
            c = intersecciones[contador_cortes]
            punto = []
            punto.append(c.y)
            punto.append(c.x)
            punto = tuple(punto)

            d_u = geopy.distance.distance(ultimo, punto).km
            if cerca_ultimo == 0 or d_cerca_u > d_u:
                cerca_ultimo = punto
                d_cerca_u = d_u

            contador_cortes += 1

        cerca_primero2 = []
        cerca_primero2.append(cerca_primero[1])
        cerca_primero2.append(cerca_primero[0])
        cerca_primero2 = tuple(cerca_primero2)
        cerca_ultimo2 = []
        cerca_ultimo2.append(cerca_ultimo[1])
        cerca_ultimo2.append(cerca_ultimo[0])
        cerca_ultimo2 = tuple(cerca_ultimo2)

        coordenadas_r.append("Punto" + str(n_punto))
        diccionario2.update({"Punto" + str(n_punto): cerca_primero2})
        n_punto += 1
        coordenadas_r.append("Punto" + str(n_punto))
        diccionario2.update({"Punto" + str(n_punto): cerca_ultimo2})
        n_punto += 1

        datos = {routeKey: coordenadas_r}
        diccionario_nuevos_flujos.update(datos)

    elif poligono.contains(entrada) == False and poligono.contains(salida) == False:

        linea = LineString(datos_recta)
        intersecciones = linea.intersection(poligono.exterior)

        if isinstance(intersecciones,shapely.geometry.multipoint.MultiPoint) and len(intersecciones) >= 2:

            contador_cortes = 0
            p = diccionario.get(flujo[0])
            primero = []
            primero.append(p[1])
            primero.append(p[0])
            primero = tuple(primero)

            cerca_primero = 0
            d_cerca_p = 0

            u = diccionario.get(flujo[len(flujo) - 1])
            ultimo = []
            ultimo.append(u[1])
            ultimo.append(u[0])
            ultimo = tuple(ultimo)

            cerca_ultimo = 0
            d_cerca_u = 0

            while contador_cortes < len(intersecciones):
                c = intersecciones[contador_cortes]
                punto = []
                punto.append(c.y)
                punto.append(c.x)
                punto = tuple(punto)

                d_primero = geopy.distance.distance(primero, punto).km
                if cerca_primero == 0 or d_cerca_p > d_primero:
                    cerca_primero = punto
                    d_cerca_p = d_primero

                contador_cortes += 1

            contador_cortes = 0
            while contador_cortes < len(intersecciones):
                c = intersecciones[contador_cortes]
                punto = []
                punto.append(c.y)
                punto.append(c.x)
                punto = tuple(punto)

                d_u = geopy.distance.distance(ultimo, punto).km
                if cerca_ultimo == 0 or d_cerca_u > d_u:
                    cerca_ultimo = punto
                    d_cerca_u = d_u

                contador_cortes += 1

            cerca_primero2 = []
            cerca_primero2.append(cerca_primero[1])
            cerca_primero2.append(cerca_primero[0])
            cerca_primero2 = tuple(cerca_primero2)
            cerca_ultimo2 = []
            cerca_ultimo2.append(cerca_ultimo[1])
            cerca_ultimo2.append(cerca_ultimo[0])
            cerca_ultimo2 = tuple(cerca_ultimo2)

            coordenadas_r.append("Punto" + str(n_punto))
            diccionario2.update({"Punto" + str(n_punto): cerca_primero2})
            n_punto += 1
            coordenadas_r.append("Punto" + str(n_punto))
            diccionario2.update({"Punto" + str(n_punto): cerca_ultimo2})
            n_punto += 1

            datos = {routeKey: coordenadas_r}
            diccionario_nuevos_flujos.update(datos)
        else:
            flujos_con_problemas_cortes.append(routeKey)
            print(len(flujos_con_problemas_cortes))

    elif poligono.contains(entrada) == True and poligono.contains(salida) == True:

        linea3 = LineString([diccionario.get(flujo[0]), diccionario.get(flujo[1])])
        nueva_recta3 = prolongar_recta(linea3, poligono)
        intersecciones3 = nueva_recta3.intersection(poligono.exterior)

        linea4 = LineString([diccionario.get(flujo[len(flujo) - 2]), diccionario.get(flujo[len(flujo) - 1])])
        nueva_recta4 = prolongar_recta(linea4, poligono)
        intersecciones4 = nueva_recta4.intersection(poligono.exterior)

        sentido = -1
        p = diccionario.get(flujo[0])
        p2 = diccionario.get(flujo[1])
        if p[0] != p2[0]:
            if p[0] > p2[0]:
                sentido = 0 #sentido hacia la izquierda
            else:
                sentido = 1 #sentido hacia la derecha
            if isinstance(intersecciones3, shapely.geometry.multipoint.MultiPoint):
                if sentido == 0:
                    primero = []
                    primero.append(intersecciones3[len(intersecciones3) - 1].x)
                    primero.append(intersecciones3[len(intersecciones3) - 1].y)
                    primero = tuple(primero)
                else:
                    primero = []
                    primero.append(intersecciones3[0].x)
                    primero.append(intersecciones3[0].y)
                    primero = tuple(primero)
            else:
                if sentido == 0:
                    primero = []
                    primero.append(intersecciones3[len(intersecciones3) - 2].x)
                    primero.append(intersecciones3[len(intersecciones3) - 2].y)
                    primero = tuple(primero)
                else:
                    primero = []
                    primero.append(intersecciones3[0].x)
                    primero.append(intersecciones3[0].y)
                    primero = tuple(primero)
        else:
            if p[1] > p2[1]:
                sentido = 0  # sentido hacia abajo, buscamos max
            else:
                sentido = 1

            lista_latitudes = []
            for inter in intersecciones3:
                if isinstance(inter, shapely.geometry.point.Point):
                    lista_latitudes.append(inter.y)
            lista_latitudes.sort(reverse=True)

            if sentido == 0:
                primero = []
                primero.append(p[0])
                primero.append(lista_latitudes[0])
                primero = tuple(primero)
            else:
                primero = []
                primero.append(p[0])
                primero.append(lista_latitudes[len(lista_latitudes) - 1])
                primero = tuple(primero)

        sentido = -1
        u = diccionario.get(flujo[len(flujo) - 1])
        u2 = diccionario.get(flujo[len(flujo) - 2])
        if u[0] != u2[0]:
            if u[0] > u2[0]:
                sentido = 1  # sentido hacia la derecha
            else:
                sentido = 0  # sentido hacia la izquierda

            if isinstance(intersecciones4, shapely.geometry.multipoint.MultiPoint):
                if sentido == 0:
                    ultimo = []
                    ultimo.append(intersecciones4[0].x)
                    ultimo.append(intersecciones4[0].y)
                    ultimo = tuple(ultimo)
                else:
                    ultimo = []
                    ultimo.append(intersecciones4[len(intersecciones4) - 1].x)
                    ultimo.append(intersecciones4[len(intersecciones4) - 1].y)
                    ultimo = tuple(ultimo)
            else:
                if sentido == 0:
                    ultimo = []
                    ultimo.append(intersecciones4[0].x)
                    ultimo.append(intersecciones4[0].y)
                    ultimo = tuple(ultimo)
                else:
                    ultimo = []
                    ultimo.append(intersecciones4[len(intersecciones4) - 2].x)
                    ultimo.append(intersecciones4[len(intersecciones4) - 2].y)
                    ultimo = tuple(ultimo)
        else:
            if u[1] > u2[1]:
                sentido = 1  # sentido hacia arriba, buscamos max
            else:
                sentido = 0

            lista_latitudes = []
            for inter in intersecciones4:
                if isinstance(inter, shapely.geometry.point.Point):
                    lista_latitudes.append(inter.y)
            lista_latitudes.sort(reverse=True)

            if sentido == 1:
                ultimo = []
                ultimo.append(u[0])
                ultimo.append(lista_latitudes[0])
                ultimo = tuple(ultimo)
            else:
                ultimo = []
                ultimo.append(u[0])
                ultimo.append(lista_latitudes[len(lista_latitudes) - 1])
                ultimo = tuple(ultimo)

        coordenadas = []
        coordenadas.append("Punto" + str(n_punto))
        diccionario2.update({"Punto" + str(n_punto): primero})
        n_punto += 1
        coordenadas.append("Punto" + str(n_punto))
        diccionario2.update({"Punto" + str(n_punto): ultimo})
        n_punto += 1

        datos = {routeKey: coordenadas}
        diccionario_nuevos_flujos.update(datos)

    else:
        if poligono.contains(entrada):
            punto_dentro = diccionario.get(flujo[0])
            punto_dentro2 = diccionario.get(flujo[1])
            punto_fuera = diccionario.get(flujo[len(flujo) - 1])
            el_de_fuera = 1
        else:
            punto_dentro = diccionario.get(flujo[len(flujo) - 1])
            punto_dentro2 = diccionario.get(flujo[len(flujo) - 2])
            punto_fuera = diccionario.get(flujo[0])
            el_de_fuera = 0

        linea2 = LineString(datos_recta)
        intersecciones2 = linea2.intersection(poligono.exterior)

        linea5 = LineString([punto_dentro, punto_dentro2])
        nueva_linea5 = prolongar_recta(linea5, poligono)
        intersecciones5 = nueva_linea5.intersection(poligono.exterior)

        contador_cortes = 0
        primero = []
        primero.append(punto_fuera[1])
        primero.append(punto_fuera[0])
        primero = tuple(primero)

        cerca_primero = 0
        d_cerca_p = 0

        if isinstance(intersecciones2, shapely.geometry.multipoint.MultiPoint):
            g = len(intersecciones2)
        else:
            g = 1

        while contador_cortes < g:
            if isinstance(intersecciones2, shapely.geometry.multipoint.MultiPoint):
                c = intersecciones2[contador_cortes]
            else:
                c = intersecciones2
            punto = []
            punto.append(c.y)
            punto.append(c.x)
            punto = tuple(punto)

            d_primero = geopy.distance.distance(primero, punto).km
            if cerca_primero == 0 or d_cerca_p > d_primero:
                cerca_primero = punto
                d_cerca_p = d_primero

            contador_cortes += 1

        sentido = -1
        if el_de_fuera == 1:
            u = diccionario.get(flujo[0])
            u2 = diccionario.get(flujo[1])
        else:
            u = diccionario.get(flujo[len(flujo) - 1])
            u2 = diccionario.get(flujo[len(flujo) - 2])
        if u[0] != u2[0]:
            if u[0] > u2[0]:
                sentido = 1  # sentido hacia la derecha
            else:
                sentido = 0  # sentido hacia la izquierda

            if isinstance(intersecciones5, shapely.geometry.multipoint.MultiPoint):
                if sentido == 0:
                    ultimo = []
                    ultimo.append(intersecciones5[0].x)
                    ultimo.append(intersecciones5[0].y)
                    ultimo = tuple(ultimo)
                else:
                    ultimo = []
                    ultimo.append(intersecciones5[len(intersecciones5) - 1].x)
                    ultimo.append(intersecciones5[len(intersecciones5) - 1].y)
                    ultimo = tuple(ultimo)
            else:
                if sentido == 0:
                    ultimo = []
                    ultimo.append(intersecciones5[0].x)
                    ultimo.append(intersecciones5[0].y)
                    ultimo = tuple(ultimo)
                else:
                    ultimo = []
                    ultimo.append(intersecciones5[len(intersecciones5) - 2].x)
                    ultimo.append(intersecciones5[len(intersecciones5) - 2].y)
                    ultimo = tuple(ultimo)
        else:
            if u[1] > u2[1]:
                sentido = 1  # sentido hacia arriba, buscamos max
            else:
                sentido = 0

            lista_latitudes = []
            for inter in intersecciones5:
                if isinstance(inter, shapely.geometry.point.Point):
                    lista_latitudes.append(inter.y)
            lista_latitudes.sort(reverse=True)

            if sentido == 1:
                ultimo = []
                ultimo.append(u[0])
                ultimo.append(lista_latitudes[0])
                ultimo = tuple(ultimo)
            else:
                ultimo = []
                ultimo.append(u[0])
                ultimo.append(lista_latitudes[len(lista_latitudes) - 1])
                ultimo = tuple(ultimo)

        cerca_primero2 = []
        cerca_primero2.append(cerca_primero[1])
        cerca_primero2.append(cerca_primero[0])
        cerca_primero2 = tuple(cerca_primero2)

        coordenadas = []
        if el_de_fuera == 1:
            coordenadas.append("Punto" + str(n_punto))
            diccionario2.update({"Punto" + str(n_punto): ultimo})
            n_punto += 1
            coordenadas.append("Punto" + str(n_punto))
            diccionario2.update({"Punto" + str(n_punto): cerca_primero2})
            n_punto += 1
        else:
            coordenadas.append("Punto" + str(n_punto))
            diccionario2.update({"Punto" + str(n_punto): cerca_primero2})
            n_punto += 1
            coordenadas.append("Punto" + str(n_punto))
            diccionario2.update({"Punto" + str(n_punto): ultimo})
            n_punto += 1

        datos = {routeKey: coordenadas}
        diccionario_nuevos_flujos.update(datos)

print(len(diccionario_nuevos_flujos.keys()))

for i in diccionario_nuevos_flujos:
    vv = diccionario_nuevos_flujos.get(i)
    print(str(i) + "    " + str(diccionario2.get(vv[0])) + str(diccionario2.get(vv[1])))

R = 18

diccionario_distancias = {}
lista_max_longitudes = []

for key in diccionario2.keys():
    punto = key
    puntos = []

    for k in diccionario2.keys():
        if k != key:
            punto_cord = diccionario2.get(punto)
            p1 = []

            if isinstance(punto_cord, shapely.geometry.point.Point):
                px = punto_cord.x
                py = punto_cord.y
            else:
                px = punto_cord[0]
                py = punto_cord[1]
            p1.append(py)
            p1.append(px)
            p1 = tuple(p1)

            punto2_cord = diccionario2.get(k)
            p2 = []
            if isinstance(punto2_cord, shapely.geometry.point.Point):
                px2 = punto2_cord.x
                py2 = punto2_cord.y
            else:
                px2 = punto2_cord[0]
                py2 = punto2_cord[1]
            p2.append(py2)
            p2.append(px2)
            p2 = tuple(p2)

            distancia = geopy.distance.distance(p1, p2).km
            if distancia < R:
                puntos.append(k)

    data = {punto: puntos}
    diccionario_distancias.update(data)
    print(data)
    data2 = []
    data2.append(punto)
    data2.append(len(puntos))
    contador = 0
    if len(lista_max_longitudes) == 0:
        lista_max_longitudes.append(data2)
    else:
        while contador <= len(lista_max_longitudes):
            if contador == len(lista_max_longitudes):
                lista_max_longitudes.append(data2)
            else:
                if lista_max_longitudes[contador][1] <= data2[1]:
                    lista_max_longitudes.insert(contador, data2)
                    contador = len(lista_max_longitudes) + 10
                else:
                    contador += 1

print(len(lista_max_longitudes))
print("DICDISTANCIAS    " + str(len(diccionario_distancias)))
diccionario_puntos_agrupados = {}
puntos_cambiados = []

for info in lista_max_longitudes:
    p = info[0]
    if len(puntos_cambiados) == 0 or p not in puntos_cambiados:
        print(info)
        puntos_cambiados.append(p)
        adyacentes = diccionario_distancias.get(p)
        x_media = diccionario2.get(p)[0]
        y_media = diccionario2.get(p)[1]
        antes_de_calcular_media = []
        for coordenada in adyacentes:
            if coordenada not in puntos_cambiados:
                antes_de_calcular_media.append(coordenada)
                coordenada_datos = diccionario2.get(coordenada)

                if isinstance(coordenada_datos, shapely.geometry.point.Point):
                    x_media += coordenada_datos.x
                    y_media += coordenada_datos.y
                else:
                    x_media += coordenada_datos[0]
                    y_media += coordenada_datos[1]

        x_media = x_media / (len(adyacentes) + 1)
        y_media = y_media / (len(adyacentes) + 1)
        tupla = (diccionario2.get(p)[0], diccionario2.get(p)[1])
        print(p + "         " + str(tupla))
        diccionario_puntos_agrupados.update({p: tuple(tupla)})
        for i in adyacentes:
            if i in antes_de_calcular_media:
                print(i + "         " + str(tupla))
                diccionario_puntos_agrupados.update({i: tuple(tupla)})
                puntos_cambiados.append(i)
print("LONGITUD DEL DICCIONARIO" + str(len(diccionario_puntos_agrupados.keys())))

f = open(
        "C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Report - Ejercicio " + ".txt", 'w')
f.write("DICCIONARIO PUNTOS AGRUPADOS")
for i in diccionario2.keys():
    f.write(i + "    " + str(diccionario2.get(i)))

for i in diccionario_puntos_agrupados:
    f.write(str(i) + str(diccionario_puntos_agrupados.get(i)))
    f.write("\n")


NO = 0
for i in diccionario2.keys():
    if i not in diccionario_puntos_agrupados.keys():
        d = {i: diccionario2.get(i)}
        diccionario_puntos_agrupados.update(d)
        NO += 1

print("NO ESTABAN CAMBIADOS" + "   " + str(NO))
ya_dibujados = []
flujos_total = 0

for i in diccionario_nuevos_flujos.keys():
    flujo = diccionario_nuevos_flujos.get(i)
    a = diccionario_puntos_agrupados.get(flujo[0])
    b = diccionario_puntos_agrupados.get(flujo[1])
    if a[0] == 0.0 or b[0]:
        print(i)
        print(a)
        print(b)
    t = []
    t.append(a)
    t.append(b)

    if t not in ya_dibujados or len(ya_dibujados) == 0:
        #datos_flujo = []
        ya_dibujados.append(t)
        #datos_flujo.append(b)
        #datos_flujo.append(a)

        flujos_total += 1


        linea = LineString(t)
        x3, y3 = linea.xy
        pyplot.plot(x3, y3)


print(flujos_total)
print(len(diccionario2))
pyplot.show()
