import re
import geopy
from geopy import distance
from shapely.geometry import Point, LineString, box

def get_nivel(dato, lista):
    '''
    En funcion del dato se suma 1 al indice de la lista que corresponda. Sirve para determinar el
    numero de flujos con evolucion de ascenso, descenso o crucero al agrupar por llegadas y salidas
    :param dato:evolucion de vuelo del flujo que se esta analizando
    :param lista: lista con numero que reflejan los flujos de cada tipo
    :return lista:
    '''
    if dato == 'ASCEND':
        lista[0] = lista[0] + 1
    elif dato == 'CRUISE':
        lista[1] = lista[1] + 1
    else:
        lista[2] = lista[2] + 1

    return lista

def seleccionar_nivel(dato):
    '''
    Se elige el tipo de evolucion en funcion de los numero que se pasan en dato
    :param dato: lista con 3 numeros que representan los flujos en ascenso, crucero y descenso de un grupo que se quiere juntar por origenes o destinos
    :return ASCEND/DESCEND/CRUISE: evoluciones de vuelo
    '''
    max = 0
    indice_max = -1
    cont = 0

    for i in dato:
        if indice_max == -1 or i > max:
            max = i
            indice_max = cont
        cont += 1

    if indice_max == 0:
        return 'ASCEND'
    elif indice_max == 1:
        return 'CRUISE'
    else:
        return 'DESCEND'

def prolongar_recta(linea, poligono):
    '''
    Permite prolongar una recta de modo que se corten la recta y el poligono
    :param linea: recta que refleja la trayectoria de un flujo
    :param poligono: poligono de un sector
    :return extended_line:linea prolongada para cortar con el poligono
    '''

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
    '''
    En funcion del dato, devuelve una evolucion de vuelo
    :param data: velocidad de la aeronave en el momento de entrada o salida del sector
    :return ASCEND/DESCEND/CRUISE: la evolucion de vuelo de la aeronave
    '''
    if data == 0:
        return 'CRUISE'
    elif data < 0:
        return 'DESCEND'
    else:
        return 'ASCEND'


def sacar_datos_intersecciones(intersecciones, iteracion):
    '''
    Funcion que cambia de orden las longitudes y latitudes de un punto
    :param intersecciones: lista de puntos
    :param iteracion: indice que se quiere cambiar
    :return i1c: punto con latitudes y longitudes cambiadas de orden
    '''
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

def obtener_poligono(datos):
    '''
    Cambio de representacion de las coordenadas del sector
    :param datos: coordendas del poligono
    :return lista_coordenadas: coordendas del poligono con las que se puede trabajar
    '''
    lista_coordenadas = []
    contador = 0
    while contador < len(datos):
        if contador == 0:
            punto = datos[0][10:]
            coordenadas = re.split("\s", punto)
            coordenadas[0] = float(coordenadas[0])
            coordenadas[1] = float(coordenadas[1])
            coordenadas = tuple(coordenadas)
            lista_coordenadas.append(coordenadas)
        elif contador < (len(datos) - 1):
            punto = datos[contador]
            coordenadas = re.split("\s", punto)
            coordenadas.pop(0)
            coordenadas[0] = float(coordenadas[0])
            coordenadas[1] = float(coordenadas[1])
            coordenadas = tuple(coordenadas)
            lista_coordenadas.append(coordenadas)
        else:
            punto = datos[contador][:-2]
            coordenadas = re.split("\s", punto)
            coordenadas.pop(0)
            coordenadas[0] = float(coordenadas[0])
            coordenadas[1] = float(coordenadas[1])
            coordenadas = tuple(coordenadas)
            lista_coordenadas.append(coordenadas)
        contador += 1

    return lista_coordenadas

def sacar_coordenadas_aerodromos(nombres, latitud, longitud, c, diccionario, seleccion):
    '''
    Obtencion de las coordenadas de todos los aeropuertos pedidos
    :param nombres: columna del fichero con los nombres de los aeropuertos
    :param latitud: columna del fichero con la latitud de las coordenadas de los aeropuertos
    :param longitud: columna del fichero con la longitud de las coordenadasde los aeropuertos
    :param c: indice del fichero
    :param diccionario: diccionario donde se guardan los datos
    :param seleccion: lista con los aeropuertos elegidos por linea de comandos
    :return diccionario
    '''
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

    return diccionario

def distancia_cortes(punto_original, punto_corte):
    '''
    Devuelve la distancia entre dos puntos
    :param punto_original: punto 1
    :param punto_corte: punto 2
    :return: distancia
    '''
    coordenadas1 = []
    coordenadas2 = []

    coordenadas1.append(punto_original[1])
    coordenadas1.append(punto_original[0])
    coordenadas1 = tuple(coordenadas1)

    coordenadas2.append(punto_corte.y)
    coordenadas2.append(punto_corte.x)
    coordenadas2 = tuple(coordenadas2)

    distancia = geopy.distance.distance(coordenadas1, coordenadas2).km
    return distancia

def obtener_datos_poligono(fichero, codigo):
    '''
    Devuelve las coordenadas de los puntos que dan forma a un sector
    :param fichero: datos de los sectores en forma de columna
    :param codigo: codigo del sector
    :return contador: indice dentro de la columna con los datos de los poligonos
    '''
    c = 0
    columna = fichero['SectorCode']
    contador = fichero.index[c]
    contador2 = 0

    while contador2 < columna.size:
        if columna[contador] == codigo:
            return contador

        if (contador2 + 1) == columna.size:
            break
        else:
            c += 1
            contador = fichero.index[c]
            contador2 += 1

def buscar_flujo(datos, flujo):
    '''
    Devuelve el flujo si esta dentro del diccionario. Funciona a modo de comprobacion de que un
    valor esta guardado como clave en el diccionario
    :param datos: diccionario
    :param flujo: nombre del flujo a buscar
    :return:
    '''
    for i in datos.keys():
        if flujo in datos.get(i):
            return i
