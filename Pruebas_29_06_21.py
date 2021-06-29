import pandas
import geopy.distance
import re
from matplotlib import pyplot
from shapely.geometry import Polygon, Point, LineString, box
#from PATH import PATH

fichero1 = pandas.read_excel("C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Documento_Flujos.xlsx")
fichero2 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Puntos.xlsx')
fichero3 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Radioayudas.xlsx')
fichero4 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Poligono_Pamplona.xlsx')

fila_nombres = fichero1['rutaExtend']
sector = fichero1['SectorCode']
t = 0

contador_1 = 0
lista_nombres = []
lista_solo_coord = []

while contador_1 < fila_nombres.size:
    if sector[contador_1] == 'LECMPAU':
        palabra = fila_nombres[contador_1]
        lista_aux = []
        n1 = ""
        n2 = ""
        cont_ = 0
        for i in palabra:
            if cont_ == 0:
                if i != "-":
                    n1 += i
                else:
                    lista_aux.append(n1)
                    n1 = ""
                    cont_ += 1
            else:
                if i != "-":
                    n1 += i
                else:
                    lista_aux.append(n1)
                    break

        cont_ = 0
        contador_2 = 1
        while cont_ != 2:
            indice = len(palabra) - contador_2
            if palabra[indice] == "-":
                cont_ += 1
                if cont_ == 2:
                    break
            n2 += palabra[indice]
            contador_2 += 1

        n3 = ""
        contador_2 = len(n2) - 1
        cont_ = 0

        while contador_2 >= 0:
            letra = n2[contador_2]

            if cont_ == 0:
                if letra != "-":
                    n3 += letra
                else:
                    lista_aux.append(n3)
                    n3 = ""
                    cont_ = 1
            else:
                if contador_2 != 0:
                    n3 += letra
                else:
                    n3 += n2[0]
                    lista_aux.append(n3)
                    n3 = ""
                    cont_ = 0
                    break

            contador_2 -= 1

        lista_nombres.append(lista_aux)
        #print(lista_aux)
        for n in lista_aux:

            if n not in lista_nombres:

                lista_nombres.append(n)
                #print(n)

    contador_1 += 1

#print(len(lista_nombres))

diccionario = {}
#print(len(diccionario.keys()))

nombres = fichero2['IDENT_TXT']
latitud = fichero2['LAT_TXT']
longitud = fichero2['LONG_TXT']
contador2 = 0

for nombre in nombres:

        if nombre in lista_nombres:
            lat = 0
            lon = 0

            g = 0
            m = 0
            s = 0
            s2 = ""
            l = ""

            if latitud[contador2][0] != 0:
                g = float(latitud[contador2][:2])
                m = float(latitud[contador2][2:4])
                s = (latitud[contador2][4:len(latitud[contador2]) - 1])
                l = latitud[contador2][-1]
            else:
                g = float(latitud[contador2][:3])
                m = float(latitud[contador2][3:5])
                s = (latitud[contador2][5:len(latitud[contador2]) - 1])
                l = latitud[contador2][-1]

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
            if len(longitud[contador2]) == 7:
                g = float(longitud[contador2][:2])
                m = float(longitud[contador2][2:4])
                s = (longitud[contador2][4:6])
                l = longitud[contador2][-1]
            else:
                g = float(longitud[contador2][:3])
                m = float(longitud[contador2][3:5])
                s = (longitud[contador2][5:len(longitud[contador2]) - 1])
                l = longitud[contador2][-1]

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

        contador2 += 1

#print("DICCIONARIO LLENO " + str(len(diccionario.keys())))

R = 20

diccionario_distancias = {}
lista_max_longitudes = []
lista_aux = []

for key in diccionario.keys():
    punto = key
    puntos = []
    for k in diccionario.keys():
        if k != key:
            punto_cor = diccionario.get(punto)
            punto_cor = tuple(punto_cor)

            punto2_cord = diccionario.get(k)
            punto2_cord = tuple(punto2_cord)

            distancia = geopy.distance.distance(punto_cor, punto2_cord).km
            if distancia < R:
                puntos.append(k)

    data = {punto: puntos}
    diccionario_distancias.update(data)
    data2 = []
    data2.append(punto)
    lista_aux.append(punto)
    data2.append(len(puntos))
    lista_max_longitudes.append(data2)

dicct_poligono_P = {}
nombre = fichero4['Point']
latitud_P = fichero4['Lattitude_TXT']
longitud_P = fichero4['Longitude_TXT']

contador_vertices = 0
for point in nombre:
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

    dicct_poligono_P.update(datos_vertice)

    contador_vertices += 1

print(len(dicct_poligono_P.keys()))

lista_vertices = []
for p in dicct_poligono_P.keys():
    r = tuple(dicct_poligono_P.get(p))
    lista_vertices.append(r)

poligono = Polygon(lista_vertices)
coordenadas = []
#a = tuple(diccionario.get("DONOS"))
a = tuple(diccionario.get("GARVU"))
#b = tuple(diccionario.get("GOMSO"))
b = tuple(diccionario.get("BANEV"))

print("A: " + str(a) + "         B: " + str(b))
coordenadas.append(a)
coordenadas.append(b)
linea = LineString(coordenadas)
#xx, yy = linea.xy

x, y = poligono.exterior.xy
pyplot.plot(x, y)
#pyplot.plot(xx, yy)

#print(linea.intersection(poligono))


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

print(extended_line.intersection(poligono.exterior))
xx, yy = extended_line.xy
pyplot.plot(xx, yy)
pyplot.show()
