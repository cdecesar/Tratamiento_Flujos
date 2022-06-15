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
def catalogar_nivel_vuelo(data):
    if data == 0:
        return 'CRUISE'
    elif data < 0:
        return 'DESCEND'
    else:
        return 'ASCEND'


def sacar_datos_intersecciones(intersecciones, iteracion):
    i1 = intersecciones[iteracion]
    i1_x = i1.y
    i1_y = i1.x
    i1c = (i1_x, i1_y)

    return i1c


def sacar_coordenadas(nombres, latitud, longitud, c, diccionario):

    contador = c
    for nombre in nombres:

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

base_datos = pandas.read_csv("C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\Base_Datos_definitiva.csv", delimiter=',')
#datos2 = base_datos.loc[:,['flightkey','routeKey','adep','ades','lat_IN','lat_OUT', 'lng_IN', 'lng_OUT', 'attitud_IN', 'attitud_OUT', 'callsign', 'vel_z_IN', 'vel_z_OUT']]

'''Este es el sector 2'''
df2 = base_datos.loc[base_datos.SectorCode=='LECMPAU',:]

datos2 = df2.loc[:,['flightkey','routeKey','adep','ades','lat_IN','lat_OUT', 'lng_IN', 'lng_OUT', 'attitud_IN', 'attitud_OUT','callsign', 'vel_z_IN', 'vel_z_OUT']]

'''Puntos de Insignia de Pamplona'''
fichero2 = pandas.read_csv('C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\Puntos.csv', delimiter=',')
nombres = fichero2['IDENT_TXT']
latitud_puntos = fichero2['LAT_TXT']
longitud_puntos = fichero2['LONG_TXT']

c = 0

routeKey = datos2['routeKey']
naves = datos2['flightkey']
l_in = datos2['lat_IN']
lo_in = datos2['lng_IN']
l_out = datos2['lat_OUT']
lo_out = datos2['lng_OUT']
origen = datos2['adep']
destino = datos2['ades']
nivel_ent = datos2['attitud_IN']
nivel_sal = datos2['attitud_OUT']
call = datos2['callsign']
v_IN = datos2['vel_z_IN']
v_OUT = datos2['vel_z_OUT']
contador_esp = datos2.index

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

def sacar_coordenadas_aerodromos(nombres, latitud, longitud, c, diccionario, seleccion):
    cont = 0
    contador = c[cont]
    for nombre in nombres:
        if nombre in seleccion:
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

            cont += 1
            if cont == len(c):
                break
            else:
                contador = c[cont]

path_poligono = 'C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\poligonos_sectores_2D_2.0.csv'

fich = pandas.read_csv(path_poligono, delimiter=';')
a = fich['PolygonToString']

b = re.split(",", a[5])
l = obtener_poligono(b)
poligono = Polygon(l)

codigo_sector = 'LECMPAU'


c = 0
contador = contador_esp[c]
contador2 = 0
flujos_repetidos = []
vuelos_repetidos = []
niveles_flujos = {}
flujos = {}
vuelos = {}
niveles_vuelos = {}
c_flujos = 1
vuelos_out = 0
final_bucle = 0


destinos_naves = {}
origen_naves = {}
while contador2 < naves.size:
    #if final_bucle == 20000:
    #    break
    #else:

        call_sg = call[contador]
        a = re.findall("\A[A-Z]{3}" + "[0-9]", call_sg)
        if len(a) == 1:
            v = naves[contador]
            if v in vuelos.keys():
                text = "__" + str(contador)
                v = str(v) + text

            lat1 = l_in[contador]
            lon1 = lo_in[contador]

            lat2 = l_out[contador]
            lon2 = lo_out[contador]
            p1 = []
            p2 = []

            p1.append(lon1)
            p1.append(lat1)
            p2.append(lon2)
            p2.append(lat2)
            p1 = tuple(p1)
            p2 = tuple(p2)
            #print(contador2, p1, p2)

            if p1 != p2:
                coordenadas = []
                coordenadas.append(p1)
                coordenadas.append(p2)

                a = catalogar_nivel_vuelo(v_IN[contador])
                b = catalogar_nivel_vuelo(v_OUT[contador])

                vuelos.update({v: coordenadas})
                origen_naves.update({v: origen[contador]})
                destinos_naves.update({v: destino[contador]})
                niveles_vuelos.update({v: (a,b)})
        final_bucle += 1

        if (contador2 + 1) == naves.size:
            break
        else:
            c += 1
            contador = contador_esp[c]
            contador2 += 1

coordenadas_nuevos_flujos = {}
asociacion_aeronaves = {}
final_bucle = 0
origen_flujos = {}
destino_flujos = {}

for i in vuelos.keys():
    #if final_bucle == 20000:
    #    break
    #else:
    print(final_bucle)
    origen = origen_naves.get(i)
    destino = destinos_naves.get(i)

    v = vuelos.get(i)
    if len(coordenadas_nuevos_flujos.keys()) == 0:
        v = tuple(v)
        l = []
        l.append(i)
        c_f = str(c_flujos) + '_' + codigo_sector
        coordenadas_nuevos_flujos.update({c_f: v})
        asociacion_aeronaves.update({c_f: l})
        niveles_flujos.update({c_f: niveles_vuelos.get(i)})
        l = []
        l.append(origen_naves.get(i))
        origen_flujos.update({c_f: l})
        l = []
        l.append(destinos_naves.get(i))
        destino_flujos.update({c_f: l})
        c_flujos += 1
    else:
        niveles_v = niveles_vuelos.get(i)
        coordenadas_nuevas_entrada = []
        coordenadas_nuevas_salida = []

        coordenadas_nuevas_entrada.append(v[0][1])
        coordenadas_nuevas_entrada.append(v[0][0])
        coordenadas_nuevas_salida.append(v[1][1])
        coordenadas_nuevas_salida.append(v[1][0])
        #print(final_bucle, coordenadas_nuevas_entrada, coordenadas_nuevas_salida)
        coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)
        coordenadas_nuevas_salida = tuple(coordenadas_nuevas_salida)

        comprobacion = 0
        posibles_f = None
        de_max = -1
        ds_max = -1

        for j in coordenadas_nuevos_flujos.keys():
            avion2 = coordenadas_nuevos_flujos.get(j)
            niveles = niveles_flujos.get(j)
            c_n_e = []
            c_n_s = []

            c_n_e.append(avion2[0][1])
            c_n_e.append(avion2[0][0])
            c_n_s.append(avion2[1][1])
            c_n_s.append(avion2[1][0])

            c_n_e = tuple(c_n_e)
            c_n_s = tuple(c_n_s)

            d_e = geopy.distance.distance(c_n_e, coordenadas_nuevas_entrada).km
            d_s = geopy.distance.distance(c_n_s, coordenadas_nuevas_salida).km

            if d_e < 10 and d_s < 10 and niveles_v[0] == niveles[0] and niveles_v[1] == niveles[1]:
                if (de_max == -1 and ds_max == -1) or (d_e < de_max and d_s < ds_max):
                    de_max = d_e
                    ds_max = d_s
                    posibles_f = j

        if posibles_f == None:
            v = tuple(v)
            l = []
            l.append(i)
            c_f = str(c_flujos) + '_' + codigo_sector
            coordenadas_nuevos_flujos.update({c_f: v})
            asociacion_aeronaves.update({c_f: l})
            niveles_flujos.update({c_f: niveles_vuelos.get(i)})
            l = []
            l.append(origen_naves.get(i))
            origen_flujos.update({c_f: l})
            l = []
            l.append(destinos_naves.get(i))
            destino_flujos.update({c_f: l})
            c_flujos += 1
        else:
            avion2 = coordenadas_nuevos_flujos.get(posibles_f)
            c_n_e = []
            c_n_s = []

            c_n_e.append(avion2[0][1])
            c_n_e.append(avion2[0][0])
            c_n_s.append(avion2[1][1])
            c_n_s.append(avion2[1][0])

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
            lista = asociacion_aeronaves.get(posibles_f)
            lista.append(i)
            asociacion_aeronaves[posibles_f] = lista
            coordenadas_nuevos_flujos[posibles_f] = tupla

            ori = origen_flujos.get(posibles_f)
            if origen_naves.get(i) not in ori:
                ori.append(origen_naves.get(i))
                origen_flujos[posibles_f] = ori

            dest = destino_flujos.get(posibles_f)
            if destinos_naves.get(i) not in dest:
                dest.append(destinos_naves.get(i))
                destino_flujos[posibles_f] = dest

    final_bucle += 1

R = 27

diccionario_distancias = {}
lista_max_longitudes = []

for key in coordenadas_nuevos_flujos.keys():
    vuelo = key
    puntos = []

    for k in coordenadas_nuevos_flujos.keys():
        if k != key and niveles_flujos.get(key)[0] == niveles_flujos.get(k)[0] and niveles_flujos.get(key)[1] == niveles_flujos.get(k)[1]:
            punto_cord = coordenadas_nuevos_flujos.get(vuelo)
            p1_entrada = []
            p1_salida = []
            p2_entrada = []
            p2_salida = []

            px = punto_cord[0][1]
            py = punto_cord[0][0]
            p1_entrada.append(py)
            p1_entrada.append(px)
            p1_entrada = tuple(p1_entrada)

            px = punto_cord[1][1]
            py = punto_cord[1][0]
            p1_salida.append(py)
            p1_salida.append(px)
            p1_salida = tuple(p1_salida)

            punto2_cord = coordenadas_nuevos_flujos.get(k)

            px2 = punto2_cord[0][1]
            py2 = punto2_cord[0][0]
            p2_entrada.append(py2)
            p2_entrada.append(px2)
            p2_entrada = tuple(p2_entrada)

            px2 = punto2_cord[1][1]
            py2 = punto2_cord[1][0]
            p2_salida.append(py2)
            p2_salida.append(px2)
            p2_salida = tuple(p2_salida)

            distancia_entrada = geopy.distance.distance(p1_entrada, p2_entrada).km
            distancia_salida = geopy.distance.distance(p1_salida, p2_salida).km
            if distancia_entrada < R and distancia_salida < R:
                puntos.append(k)

    data = {vuelo: puntos}
    diccionario_distancias.update(data)
    data2 = []
    data2.append(vuelo)
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

diccionario_flujos_agrupados = {}
puntos_cambiados = []

for info in lista_max_longitudes:
    vuelo_principal = info[0]
    if len(puntos_cambiados) == 0 or vuelo_principal not in puntos_cambiados:
        puntos_cambiados.append(vuelo_principal)
        adyacentes = diccionario_distancias.get(vuelo_principal)
        entrada = coordenadas_nuevos_flujos.get(vuelo_principal)[0]
        salida = coordenadas_nuevos_flujos.get(vuelo_principal)[1]

        tupla = (entrada, salida)
        diccionario_flujos_agrupados.update({vuelo_principal: tuple(tupla)})
        for i in adyacentes:
            if i not in puntos_cambiados:
                diccionario_flujos_agrupados.update({i: tuple(tupla)})
                puntos_cambiados.append(i)
#%%

ya_dibujados = []
ya_dibujados_indices = []
flujos_total = 0

flujos_clusterizados = {}
asociacion_flujos_clusterizados = {}
asociacion_aeronaves_clusterizados = {}
contador_flujos = 1
niveles_flujos_cl = {}
origenes_cluster = {}
destinos_cluster = {}

for i in diccionario_flujos_agrupados.keys():
    flujo = diccionario_flujos_agrupados.get(i)
    a = []
    a.append(flujo)
    a.append(niveles_flujos.get(i))
    if a not in ya_dibujados:
        ya_dibujados.append(a)
        ya_dibujados_indices.append(contador_flujos)
        c_f = str(contador_flujos) + '_' + codigo_sector + '_CL'
        niveles_flujos_cl.update({c_f: niveles_flujos.get(i)})

        todos_flujos = []
        todos_flujos.append(i)
        asociacion_flujos_clusterizados.update({c_f: todos_flujos})

        lista = []
        for m in origen_flujos.get(i):
            lista.append(m)
        lista2 = []
        for m in destino_flujos.get(i):
            lista2.append(m)

        asociacion_aeronaves_clusterizados.update({c_f: asociacion_aeronaves.get(i)})
        origenes_cluster.update({c_f: lista})
        destinos_cluster.update({c_f: lista2})
        #a.append(lista)
        #a.append(lista2)
        datos_f = {c_f: a}
        flujos_clusterizados.update(datos_f)

        li = LineString([flujo[0], flujo[1]])
        x, y = li.xy
        pyplot.plot(x, y)

        contador_flujos += 1
        flujos_total += 1
    else:
        for q in flujos_clusterizados.keys():
            result = flujos_clusterizados.get(q)
            if result == a:
                asociacion_flujos_clusterizados.get(q).append(i)
                for m in asociacion_aeronaves.get(i):
                    if m not in asociacion_aeronaves_clusterizados.get(q):
                        asociacion_aeronaves_clusterizados.get(q).append(m)
                for m in origen_flujos.get(i):
                    if m not in origenes_cluster.get(q):
                        origenes_cluster.get(q).append(m)
                for m in destino_flujos.get(i):
                    if m not in destinos_cluster.get(q):
                        destinos_cluster.get(q).append(m)
                break

x, y = poligono.exterior.xy
pyplot.plot(x, y)

pyplot.show()
# VAMOS A DIVIDIR LOS FLUJOS EN DOS GRUPOS: TIPO 1 (ESTAN CASI CASI CORTANDO AL SECTOR) Y TIPO2 (SE QUEDAN EN MITAD Y ROMPEN EL RESULTADO
tipo1 = {}
tipo1_5 = {}
tipo2 = {}
for i in flujos_clusterizados.keys():

    info = flujos_clusterizados.get(i)[0]
    linea = LineString(info)

    nueva_linea = prolongar_recta(linea, poligono)
    intersecciones = nueva_linea.intersection(poligono.exterior)

    if (isinstance(intersecciones, shapely.geometry.multipoint.MultiPoint)) and ((len(intersecciones) % 2) == 0):

        i1 = intersecciones[0]
        i1_x = i1.y
        i1_y = i1.x
        i1c = (i1_x,i1_y)

        i2 = intersecciones[len(intersecciones) - 1]
        i2_x = i2.y
        i2_y = i2.x
        i2c = (i2_x,i2_y)

        p1_entrada = []
        p1_salida = []

        px = info[0][0]
        py = info[0][1]
        p1_entrada.append(py)
        p1_entrada.append(px)
        p1_entrada = tuple(p1_entrada)

        px = info[1][0]
        py = info[1][1]
        p1_salida.append(py)
        p1_salida.append(px)
        p1_salida = tuple(p1_salida)

        d1 = geopy.distance.distance(i1c, p1_entrada)
        d2 = geopy.distance.distance(i2c, p1_salida)

        if (d1 < 7) and (d2 < 7):
            tipo1.update({i: flujos_clusterizados.get(i)})
        else:
            d1 = geopy.distance.distance(i1c, p1_salida)
            d2 = geopy.distance.distance(i2c, p1_entrada)

            if (d1 < 7) and (d2 < 7):
                tipo1.update({i: flujos_clusterizados.get(i)})
            else:
                if len(intersecciones) > 2:
                    contador_intersecciones = 1
                    encontrado = False
                    while contador_intersecciones < len(intersecciones) - 1:
                        i1c = sacar_datos_intersecciones(intersecciones, contador_intersecciones)
                        i2c = sacar_datos_intersecciones(intersecciones, (len(intersecciones) - 1))

                        p1_entrada = []
                        p1_salida = []

                        px = info[0][0]
                        py = info[0][1]
                        p1_entrada.append(py)
                        p1_entrada.append(px)
                        p1_entrada = tuple(p1_entrada)

                        px = info[1][0]
                        py = info[1][1]
                        p1_salida.append(py)
                        p1_salida.append(px)
                        p1_salida = tuple(p1_salida)

                        d1 = geopy.distance.distance(i1c, p1_entrada)
                        d2 = geopy.distance.distance(i2c, p1_salida)
                        if (d1 < 10) and (d2 < 10):
                            tipo1.update({i: flujos_clusterizados.get(i)})
                            contador_intersecciones = len(intersecciones) + 5
                            encontrado = True
                        else:
                            d1 = geopy.distance.distance(i1c, p1_salida)
                            d2 = geopy.distance.distance(i2c, p1_entrada)
                            if (d1 < 7) and (d2 < 7):
                                tipo1.update({i: flujos_clusterizados.get(i)})
                                contador_intersecciones = len(intersecciones) + 5
                                encontrado = True
                            else:
                                contador_intersecciones += 1

                    if encontrado == False:
                        contador_intersecciones = len(intersecciones) - 2
                        while contador_intersecciones > 0 and encontrado == False:
                            i1c = sacar_datos_intersecciones(intersecciones, 0)
                            i2c = sacar_datos_intersecciones(intersecciones, contador_intersecciones)

                            p1_entrada = []
                            p1_salida = []

                            px = info[0][0]
                            py = info[0][1]
                            p1_entrada.append(py)
                            p1_entrada.append(px)
                            p1_entrada = tuple(p1_entrada)

                            px = info[1][0]
                            py = info[1][1]
                            p1_salida.append(py)
                            p1_salida.append(px)
                            p1_salida = tuple(p1_salida)

                            d1 = geopy.distance.distance(i1c, p1_entrada)
                            d2 = geopy.distance.distance(i2c, p1_salida)

                            if (d1 < 10) and (d2 < 10):
                                tipo1.update({i: flujos_clusterizados.get(i)})
                                contador_intersecciones = len(intersecciones) + 5
                                encontrado = True
                            else:
                                d1 = geopy.distance.distance(i1c, p1_salida)
                                d2 = geopy.distance.distance(i2c, p1_entrada)

                                if (d1 < 7) and (d2 < 7):
                                    tipo1.update({i: flujos_clusterizados.get(i)})
                                    contador_intersecciones = len(intersecciones) + 5
                                    encontrado = True
                                else:
                                    contador_intersecciones -= 1

                        if encontrado == False:

                            p1_entrada = []
                            p1_salida = []

                            px = info[0][0]
                            py = info[0][1]
                            p1_entrada.append(py)
                            p1_entrada.append(px)
                            p1_entrada = tuple(p1_entrada)

                            px = info[1][0]
                            py = info[1][1]
                            p1_salida.append(py)
                            p1_salida.append(px)
                            p1_salida = tuple(p1_salida)

                            d = geopy.distance.distance(p1_entrada, p1_salida)
                            if d < 40:
                                tipo2.update({i: flujos_clusterizados.get(i)})
                            else:
                                tipo1_5.update({i: flujos_clusterizados.get(i)})

                else:

                    p1_entrada = []
                    p1_salida = []

                    px = info[0][0]
                    py = info[0][1]
                    p1_entrada.append(py)
                    p1_entrada.append(px)
                    p1_entrada = tuple(p1_entrada)

                    px = info[1][0]
                    py = info[1][1]
                    p1_salida.append(py)
                    p1_salida.append(px)
                    p1_salida = tuple(p1_salida)

                    d = geopy.distance.distance(p1_entrada, p1_salida)
                    if d < 40:
                        tipo2.update({i: flujos_clusterizados.get(i)})
                    else:
                        tipo1_5.update({i: flujos_clusterizados.get(i)})
    else:

        p1_entrada = []
        p1_salida = []

        px = info[0][0]
        py = info[0][1]
        p1_entrada.append(py)
        p1_entrada.append(px)
        p1_entrada = tuple(p1_entrada)

        px = info[1][0]
        py = info[1][1]
        p1_salida.append(py)
        p1_salida.append(px)
        p1_salida = tuple(p1_salida)

        d = geopy.distance.distance(p1_entrada, p1_salida)
        if d < 40:
            tipo2.update({i: flujos_clusterizados.get(i)})
        else:
            tipo1_5.update({i: flujos_clusterizados.get(i)})
#%%
# Clusterizados
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Clusterizados_LECMPAU.json", "w") as f6:
    json.dump(flujos_clusterizados, f6, indent=4)
f6.close()
# Tipo1
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Tipo1_LECMPAU.json", "w") as f7:
    json.dump(tipo1, f7, indent=4)
f7.close()
# Tipo1.5
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Tipo1.5_LECMPAU.json", "w") as f8:
    json.dump(tipo1_5, f8, indent=4)
f8.close()
# Tipo2
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Tipo2_LECMPAU.json", "w") as f9:
    json.dump(tipo2, f9, indent=4)
f9.close()
# Asociacion
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Asociacion_LECMPAU.json", "w") as f10:
    json.dump(asociacion_flujos_clusterizados, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Asociacion_Vuelos_LECMPAU.json", "w") as f13:
    json.dump(asociacion_aeronaves_clusterizados, f13, indent=4)
f13.close()

flujocrida = df2['routeKey']
naves = df2['flightkey']

diccionario_global_crida_flujos = {}
diccionario_global_flujos_crida = {}
asociacion_aeronaves

c = 0
contador = contador_esp[c]
contador2 = 0

while contador2 < flujocrida.size:
    vuelo = naves[contador]
    flujo_crida = flujocrida[contador]
    for i in asociacion_aeronaves_clusterizados.keys():
        if vuelo in asociacion_aeronaves_clusterizados.get(i):
            if i in diccionario_global_flujos_crida.keys() and flujo_crida not in diccionario_global_flujos_crida.get(i):
                diccionario_global_flujos_crida.get(i).append(flujo_crida)
            else:
                lista = []
                lista.append(flujocrida[contador])
                diccionario_global_flujos_crida.update({i: lista})

            if flujo_crida in diccionario_global_crida_flujos.keys() and i not in diccionario_global_crida_flujos.get(flujo_crida):
                diccionario_global_crida_flujos.get(flujo_crida).append(i)
            else:
                lista2 = []
                lista2.append(i)
                diccionario_global_crida_flujos.update({flujo_crida: lista2})

            break

    if (contador2 + 1) == naves.size:
        break
    else:
        c += 1
        contador = contador_esp[c]
        contador2 += 1

with  open(FILES_PATH + "AsociacionFlujos_Crida_PuntoMedio.json", "w") as f11:
    json.dump(diccionario_global_crida_flujos, f11, indent=4)
f11.close()
with  open(FILES_PATH + "AsociacionFlujos_PuntoMedio_Crida.json", "w") as f12:
    json.dump(diccionario_global_flujos_crida, f12, indent=4)
f12.close()