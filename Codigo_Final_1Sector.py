# %%
import re
import json
import pandas
import pathlib
import shapely
import geopy.distance
from shapely.geometry import Polygon, LineString
from funciones import get_nivel, seleccionar_nivel, prolongar_recta, catalogar_nivel_vuelo, \
    sacar_datos_intersecciones, obtener_poligono, sacar_coordenadas_aerodromos

FILES_PATH = str(pathlib.Path(__file__).parent.resolve())

'''
CODIGOS DE AEROPUERTOS
Barcelona       -> LEBL
Castejon        -> LEMD
Canarias        -> GCLP GCTS GCLA GCXO GCRR GCLB GCFV GCHI GCGM 
Pamplona        -> Ninguno
Toledo          -> LEMD
Domingo         -> LEBB LEVT
Zaragoza        -> Ninguno
'''
# Se piden por línea de comandos los códigos de los sectores que se quieren analizar

aeropuertos_por_pantalla = []
condicion = True
while condicion:
    input_ = input("Dime un aeropuerto: ")
    if input_ != "Ya":
        aeropuertos_por_pantalla.append(input_)
    else:
        condicion = False

# Carga de datos de los ficheros

# Datos de los vuelos del sector
base_datos = pandas.read_csv(FILES_PATH + "\\Base_Datos_sectorizado_LECMTZI.csv", delimiter=',')
# Seleccion de las columnas necesarias
base_datos_reducida = base_datos.loc[:, ['flightkey', 'routeKey', 'adep', 'ades', 'lat_IN', 'lat_OUT', 'lng_IN',
                                         'lng_OUT', 'attitud_IN', 'attitud_OUT', 'callsign', 'vel_z_IN', 'vel_z_OUT']]
codigo_sector = 'LECMTZI'
c = 0
routeKey = base_datos_reducida['routeKey']
naves = base_datos_reducida['flightkey']
l_in = base_datos_reducida['lat_IN']
lo_in = base_datos_reducida['lng_IN']
l_out = base_datos_reducida['lat_OUT']
lo_out = base_datos_reducida['lng_OUT']
origen = base_datos_reducida['adep']
destino = base_datos_reducida['ades']
nivel_ent = base_datos_reducida['attitud_IN']
nivel_sal = base_datos_reducida['attitud_OUT']
call = base_datos_reducida['callsign']
v_IN = base_datos_reducida['vel_z_IN']
v_OUT = base_datos_reducida['vel_z_OUT']
contador_esp = base_datos_reducida.index

# Informacion de puntos de notificacion
fichero_coordenadas_puntos = pandas.read_csv(FILES_PATH + '\\Archivos\\Puntos.csv', delimiter=',')
nombres = fichero_coordenadas_puntos['IDENT_TXT']
latitud_puntos = fichero_coordenadas_puntos['LAT_TXT']
longitud_puntos = fichero_coordenadas_puntos['LONG_TXT']

# Coordenadas de los puntos del poligono
path_poligono = FILES_PATH + '\\Archivos\\poligonos_sectores_2D_2.0.csv'
fichero_coordenadas_poligonos = pandas.read_csv(path_poligono, delimiter=';')
coordenadas_todos_poligonos = fichero_coordenadas_poligonos['PolygonToString']
# Se genera el objeto Poligono
# Se selecciona el poligono que se necesite del fichero
codigo_poligono_sector = re.split(",", coordenadas_todos_poligonos[9])
lista_puntos_poligono = obtener_poligono(codigo_poligono_sector)
poligono = Polygon(lista_puntos_poligono)

# Informacion de los aerodromos.
fichero_coordenadas_aerodromos = pandas.read_csv(FILES_PATH + "\\Archivos\\Aerodromos.csv", delimiter=",")
aerodromos = fichero_coordenadas_aerodromos.loc[fichero_coordenadas_aerodromos.TYPE_CODE == 'AD', :]
nombres_aerodromos = aerodromos['IDENT_TXT']
latitud_aerodromos = aerodromos['LAT_TXT']
longitud_aerodromos = aerodromos['LONG_TXT']
aeropuertos = {}
# Se obtienen los datos necesarios
aeropuertos = sacar_coordenadas_aerodromos(nombres_aerodromos, latitud_aerodromos, longitud_aerodromos,
                                           aerodromos.index, aeropuertos, aeropuertos_por_pantalla)

# Informacion del bucle
c = 0
contador = contador_esp[c]
contador2 = 0

flujos_repetidos = []
vuelos_repetidos = []
niveles_flujos = {}
flujos = {}
vuelos = {}
niveles_vuelos = {}
contador_flujos = 1
vuelos_out = 0

destinos_naves = {}
origen_naves = {}

# Seleccion de las aeronaves que se van a estudiar. Se guarda el flightkey, coordenadas y la evolucion
while contador2 < naves.size:
    call_sg = call[contador]
    # Se descartan los vuelos no comerciales que no cumplen con la expresion regex en el flightkey
    coincidencias_patron_callsign = re.findall("\A[A-Z]{3}" + "[0-9]", call_sg)
    if len(coincidencias_patron_callsign) == 1:
        vuelo_comercial = naves[contador]
        # Como existe la posibilidad de que se repita el callsign,
        # se añade al callsign repetido un string para diferenciarlo
        if vuelo_comercial in vuelos.keys():
            text = "__" + str(contador)
            vuelo_comercial = str(vuelo_comercial) + text

        lat_entrada = l_in[contador]
        lon_entrada = lo_in[contador]

        lat_salida = l_out[contador]
        lon_salida = lo_out[contador]

        punto_entrada = []
        punto_salida = []
        punto_entrada.append(lon_entrada)
        punto_entrada.append(lat_entrada)
        punto_salida.append(lon_salida)
        punto_salida.append(lat_salida)
        punto_entrada = tuple(punto_entrada)
        punto_salida = tuple(punto_salida)

        # Comprobacion de que las coordenadas de entrada y salida no coinciden
        if punto_entrada != punto_salida:
            coordenadas = [punto_entrada, punto_salida]

            evolucion_entrada = catalogar_nivel_vuelo(v_IN[contador])
            evolucion_salida = catalogar_nivel_vuelo(v_OUT[contador])

            # Se guarda el vuelo con sus coordenadas, el origen, el destino y la evolucion en entrada y salida
            vuelos.update({vuelo_comercial: coordenadas})
            origen_naves.update({vuelo_comercial: origen[contador]})
            destinos_naves.update({vuelo_comercial: destino[contador]})
            niveles_vuelos.update({vuelo_comercial: (evolucion_entrada, evolucion_salida)})

    # Condicion de salida del bucle
    if (contador2 + 1) == naves.size:
        break
    else:
        c += 1
        contador = contador_esp[c]
        contador2 += 1

# Primeros flujos generados
coordenadas_flujos = {}
# Vuelos que pertenecen a cada uno de esos flujos
asociacion_aeronaves = {}
# Origenes y destinos de cada flujo
origen_flujos = {}
destino_flujos = {}

# Radio de la primera clusterizacion
R1 = 1.852 * 5

# Generacion de los primeros flujos
for aeronave in vuelos.keys():

    origen = origen_naves.get(aeronave)
    destino = destinos_naves.get(aeronave)
    coordenadas_vuelo = vuelos.get(aeronave)

    if len(coordenadas_flujos.keys()) == 0:
        codigo_flujo = str(contador_flujos) + '_' + codigo_sector
        coordenadas_vuelo = tuple(coordenadas_vuelo)

        lista_aeronaves = [aeronave]
        coordenadas_flujos.update({codigo_flujo: coordenadas_vuelo})
        asociacion_aeronaves.update({codigo_flujo: lista_aeronaves})
        niveles_flujos.update({codigo_flujo: niveles_vuelos.get(aeronave)})

        lista_origenes = [origen_naves.get(aeronave)]
        origen_flujos.update({codigo_flujo: lista_origenes})

        lista_destinos = [destinos_naves.get(aeronave)]
        destino_flujos.update({codigo_flujo: lista_destinos})
        contador_flujos += 1
    else:
        # Es necesario cambiar el orden de las coordenadas porque se guardan lon-lat, pero para poder calcular
        # distancias correctamente hace falta tener las coordenadas como lat-lon
        niveles_aeronave = niveles_vuelos.get(aeronave)
        coordenadas_nuevas_entrada = []
        coordenadas_nuevas_salida = []

        coordenadas_nuevas_entrada.append(coordenadas_vuelo[0][1])
        coordenadas_nuevas_entrada.append(coordenadas_vuelo[0][0])
        coordenadas_nuevas_salida.append(coordenadas_vuelo[1][1])
        coordenadas_nuevas_salida.append(coordenadas_vuelo[1][0])
        coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)
        coordenadas_nuevas_salida = tuple(coordenadas_nuevas_salida)

        # Se busca el flujo más cercano a la aeronave que se este analizando
        # Es necesario recorrer todos los flujos para encontrar el mas adecuado

        comprobacion = 0
        posibles_flujo = None
        de_max = -1
        ds_max = -1

        # Comprobacion con cada uno de los flujos ya creados en iteraciones anteriores
        for j in coordenadas_flujos.keys():

            coordenadas_flujo_comprobar = coordenadas_flujos.get(j)
            niveles_flujo_comprobar = niveles_flujos.get(j)

            coordenadas_flujo_entrada = []
            coordenadas_flujo_salida = []

            coordenadas_flujo_entrada.append(coordenadas_flujo_comprobar[0][1])
            coordenadas_flujo_entrada.append(coordenadas_flujo_comprobar[0][0])
            coordenadas_flujo_salida.append(coordenadas_flujo_comprobar[1][1])
            coordenadas_flujo_salida.append(coordenadas_flujo_comprobar[1][0])

            coordenadas_flujo_entrada = tuple(coordenadas_flujo_entrada)
            coordenadas_flujo_salida = tuple(coordenadas_flujo_salida)

            # Calculo de las distancias entre los puntos de entrada y salida del flujo j y el vuelo que se analiza
            distancia_entrada = geopy.distance.distance(coordenadas_flujo_entrada, coordenadas_nuevas_entrada).km
            distancia_salida = geopy.distance.distance(coordenadas_flujo_salida, coordenadas_nuevas_salida).km

            # Deben tener la misma evolucion y una distancia menor a la especificada por el radio seleccionado
            if distancia_entrada < R1 and distancia_salida < R1 and niveles_flujo_comprobar[0] == niveles_aeronave[0] \
                    and niveles_flujo_comprobar[1] == niveles_aeronave[1]:
                # Se selecciona el flujo si las distancias son menores que las que ya se han registrado
                if (de_max == -1 and ds_max == -1) or (distancia_entrada < de_max and distancia_salida < ds_max):
                    de_max = distancia_entrada
                    ds_max = distancia_salida
                    posibles_flujo = j

        # En caso de no encontrar flujos que complan las condiciones
        if posibles_flujo is None:
            codigo_flujo = str(contador_flujos) + '_' + codigo_sector
            coordenadas_vuelo = tuple(coordenadas_vuelo)

            lista_aeronaves = [aeronave]
            coordenadas_flujos.update({codigo_flujo: coordenadas_vuelo})
            asociacion_aeronaves.update({codigo_flujo: lista_aeronaves})
            niveles_flujos.update({codigo_flujo: niveles_vuelos.get(aeronave)})

            lista_origenes = [origen_naves.get(aeronave)]
            origen_flujos.update({codigo_flujo: lista_origenes})

            lista_destinos = [destinos_naves.get(aeronave)]
            destino_flujos.update({codigo_flujo: lista_destinos})
            contador_flujos += 1

        # En caso contrario
        else:
            coordenadas_flujo_comprobar = coordenadas_flujos.get(posibles_flujo)
            coordenadas_flujo_entrada = []
            coordenadas_flujo_salida = []

            coordenadas_flujo_entrada.append(coordenadas_flujo_comprobar[0][1])
            coordenadas_flujo_entrada.append(coordenadas_flujo_comprobar[0][0])
            coordenadas_flujo_salida.append(coordenadas_flujo_comprobar[1][1])
            coordenadas_flujo_salida.append(coordenadas_flujo_comprobar[1][0])

            coordenadas_flujo_entrada = tuple(coordenadas_flujo_entrada)
            coordenadas_flujo_salida = tuple(coordenadas_flujo_salida)

            entrada_media_1 = (coordenadas_flujo_entrada[1] + coordenadas_nuevas_entrada[1]) / 2
            entrada_media_2 = (coordenadas_flujo_entrada[0] + coordenadas_nuevas_entrada[0]) / 2
            salida_media_1 = (coordenadas_flujo_salida[1] + coordenadas_nuevas_salida[1]) / 2
            salida_media_2 = (coordenadas_flujo_salida[0] + coordenadas_nuevas_salida[0]) / 2

            p_entrada = [entrada_media_1, entrada_media_2]
            p_salida = [salida_media_1, salida_media_2]
            p_entrada = tuple(p_entrada)
            p_salida = tuple(p_salida)

            tupla = (p_entrada, p_salida)
            lista_aeronaves_asociadas = asociacion_aeronaves.get(posibles_flujo)
            lista_aeronaves_asociadas.append(aeronave)
            asociacion_aeronaves[posibles_flujo] = lista_aeronaves_asociadas
            coordenadas_flujos[posibles_flujo] = tupla

            ori = origen_flujos.get(posibles_flujo)
            if origen_naves.get(aeronave) not in ori:
                ori.append(origen_naves.get(aeronave))
                origen_flujos[posibles_flujo] = ori

            dest = destino_flujos.get(posibles_flujo)
            if destinos_naves.get(aeronave) not in dest:
                dest.append(destinos_naves.get(aeronave))
                destino_flujos[posibles_flujo] = dest

# Radio de clusterizacion de los flujos
R = 1.852 * 14

# Para cada punto se
diccionario_agrupaciones = {}
lista_max_agrupaciones = []

for key in coordenadas_flujos.keys():
    flujo = key
    flujos_agrupar = []

    for k in coordenadas_flujos.keys():
        # Los dos flujos deben ser distintos y tener la misma evolucion para poder consederar la idea de unirlos
        if k != key and niveles_flujos.get(key)[0] == niveles_flujos.get(k)[0] and niveles_flujos.get(key)[1] == \
                niveles_flujos.get(k)[1]:
            punto_coordenadas_flujo1 = coordenadas_flujos.get(flujo)
            p1_entrada = []
            p1_salida = []

            px = punto_coordenadas_flujo1[0][1]
            py = punto_coordenadas_flujo1[0][0]
            p1_entrada.append(py)
            p1_entrada.append(px)
            p1_entrada = tuple(p1_entrada)

            px = punto_coordenadas_flujo1[1][1]
            py = punto_coordenadas_flujo1[1][0]
            p1_salida.append(py)
            p1_salida.append(px)
            p1_salida = tuple(p1_salida)

            punto_coordenadas_flujo2 = coordenadas_flujos.get(k)
            p2_entrada = []
            p2_salida = []

            px2 = punto_coordenadas_flujo2[0][1]
            py2 = punto_coordenadas_flujo2[0][0]
            p2_entrada.append(py2)
            p2_entrada.append(px2)
            p2_entrada = tuple(p2_entrada)

            px2 = punto_coordenadas_flujo2[1][1]
            py2 = punto_coordenadas_flujo2[1][0]
            p2_salida.append(py2)
            p2_salida.append(px2)
            p2_salida = tuple(p2_salida)

            distancia_entrada = geopy.distance.distance(p1_entrada, p2_entrada).km
            distancia_salida = geopy.distance.distance(p1_salida, p2_salida).km
            # Comparacion de la distancia entre las entradas y salidas de ambos flujos
            # Si se cumple la condicion, se añade el flujo k a la lista del flujo key
            if distancia_entrada < R and distancia_salida < R:
                flujos_agrupar.append(k)

    agrupaciones = {flujo: flujos_agrupar}
    diccionario_agrupaciones.update(agrupaciones)

    numero_agrupaciones = [flujo, len(flujos_agrupar)]
    contador = 0

    # Se ordena la lista de maximas agrupaciones de mayor a menor para poder clusterizar mas adelante correctamente
    if len(lista_max_agrupaciones) == 0:
        lista_max_agrupaciones.append(numero_agrupaciones)
    else:
        while contador <= len(lista_max_agrupaciones):
            if contador == len(lista_max_agrupaciones):
                lista_max_agrupaciones.append(numero_agrupaciones)
            else:
                if lista_max_agrupaciones[contador][1] <= numero_agrupaciones[1]:
                    lista_max_agrupaciones.insert(contador, numero_agrupaciones)
                    contador = len(lista_max_agrupaciones) + 10
                else:
                    contador += 1

diccionario_flujos_agrupados = {}
flujos_cambiados = []

# Se agrupan los flujos de mayor a menor numero de agrupaciones posibles
for info in lista_max_agrupaciones:
    flujo_principal = info[0]
    # Si el flujo no se ha agrupado anteriormente en otro, se prodece a desarrollar su agrupacion
    if len(flujos_cambiados) == 0 or flujo_principal not in flujos_cambiados:

        flujos_cambiados.append(flujo_principal)
        # Flujos a los que puede agrupar
        adyacentes = diccionario_agrupaciones.get(flujo_principal)
        entrada = coordenadas_flujos.get(flujo_principal)[0]
        salida = coordenadas_flujos.get(flujo_principal)[1]

        tupla = (entrada, salida)
        # Se guardan las coordenadas del flujo
        diccionario_flujos_agrupados.update({flujo_principal: tuple(tupla)})
        for i in adyacentes:
            # De todos los que podia agrupar, se seleccionan aquellos que no han sido agrupados antes.
            # Por eso se requiere que la lista este ordenada de mayor a menor.
            # De esta forma se consigue agrupar los flujos en funcion de aquellos que mas abarcan
            if i not in flujos_cambiados:
                diccionario_flujos_agrupados.update({i: tuple(tupla)})
                flujos_cambiados.append(i)

analizados = []
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
    datos_flujo = [flujo, niveles_flujos.get(i)]

    # Si las coordenadas de ese flujo junto con su evolucion no se han analizado, se procede a ello.
    # En caso contrario, no se crea otro flujo con esas caracteristicas
    if datos_flujo not in analizados:

        analizados.append(datos_flujo)
        codigo_flujo_clusterizado = str(contador_flujos) + '_' + codigo_sector + '_CL'
        niveles_flujos_cl.update({codigo_flujo_clusterizado: niveles_flujos.get(i)})

        todos_flujos_asociados = [i]
        asociacion_flujos_clusterizados.update({codigo_flujo_clusterizado: todos_flujos_asociados})

        lista_origenes_conjunto = []
        for m in origen_flujos.get(i):
            lista_origenes_conjunto.append(m)
        lista_destinos_conjunto = []
        for m in destino_flujos.get(i):
            lista_destinos_conjunto.append(m)
        lista_aeronaves_conjunto = []
        for m in asociacion_aeronaves.get(i):
            lista_aeronaves_conjunto.append(str(m))

        asociacion_aeronaves_clusterizados.update({codigo_flujo_clusterizado: lista_aeronaves_conjunto})
        origenes_cluster.update({codigo_flujo_clusterizado: lista_origenes_conjunto})
        destinos_cluster.update({codigo_flujo_clusterizado: lista_destinos_conjunto})
        datos_f = {codigo_flujo_clusterizado: datos_flujo}
        flujos_clusterizados.update(datos_f)

        contador_flujos += 1
        flujos_total += 1
    else:
        for q in flujos_clusterizados.keys():
            result = flujos_clusterizados.get(q)
            if result == datos_flujo:
                asociacion_flujos_clusterizados.get(q).append(i)
                for m in origen_flujos.get(i):
                    if m not in origenes_cluster.get(q):
                        origenes_cluster.get(q).append(m)
                for m in destino_flujos.get(i):
                    if m not in destinos_cluster.get(q):
                        destinos_cluster.get(q).append(m)
                for m in asociacion_aeronaves.get(i):
                    if m not in asociacion_aeronaves_clusterizados.get(q):
                        asociacion_aeronaves_clusterizados.get(q).append(str(m))

                break
print('Numero de flujos despues de clusterizar la primera vez: ', len(flujos_clusterizados.keys()))
# Se dividen los flujos en 3 grupos en funcion de sus coordenadas dentro del sector y dimensiones
tipo1 = {}
tipo1_5 = {}
tipo2 = {}

for i in flujos_clusterizados.keys():

    info_coordenadas = flujos_clusterizados.get(i)[0]
    linea = LineString(info_coordenadas)

    nueva_linea = prolongar_recta(linea, poligono)
    intersecciones = nueva_linea.intersection(poligono.exterior)

    if (isinstance(intersecciones, shapely.geometry.multipoint.MultiPoint)) and ((len(intersecciones) % 2) == 0):
        # Se seleccionan la primera y ultima interseccion de la recta prolongada con el sector

        i1 = intersecciones[0]
        i1_x = i1.y
        i1_y = i1.x
        i1_coordenadas = (i1_x, i1_y)

        i2 = intersecciones[len(intersecciones) - 1]
        i2_x = i2.y
        i2_y = i2.x
        i2_coordenadas = (i2_x, i2_y)

        p1_entrada = []
        p1_salida = []

        px = info_coordenadas[0][0]
        py = info_coordenadas[0][1]
        p1_entrada.append(py)
        p1_entrada.append(px)
        p1_entrada = tuple(p1_entrada)

        px = info_coordenadas[1][0]
        py = info_coordenadas[1][1]
        p1_salida.append(py)
        p1_salida.append(px)
        p1_salida = tuple(p1_salida)

        # Se calcula la distancia entre el punto de entrada de del flujo y el primer punto de interseccion,
        # y la distancia entre la salida y el ultimo punto de interseccion
        d1 = geopy.distance.distance(i1_coordenadas, p1_entrada)
        d2 = geopy.distance.distance(i2_coordenadas, p1_salida)

        if (d1 < 7) and (d2 < 7):
            tipo1.update({i: flujos_clusterizados.get(i)})
        else:
            # Si no se cumple,se calculan las distancias del reves
            d1 = geopy.distance.distance(i1c, p1_salida)
            d2 = geopy.distance.distance(i2c, p1_entrada)

            if (d1 < 7) and (d2 < 7):
                tipo1.update({i: flujos_clusterizados.get(i)})
            else:
                # Como no se sabe el orden de las intersecciones en caso de tener mas de 2, se comprueban
                # las distancias con cada punto de interseccion de la resta prolongada y el sector
                if len(intersecciones) > 2:
                    contador_intersecciones = 1
                    encontrado = False
                    while contador_intersecciones < len(intersecciones) - 1:
                        i1c = sacar_datos_intersecciones(intersecciones, contador_intersecciones)
                        i2c = sacar_datos_intersecciones(intersecciones, (len(intersecciones) - 1))

                        p1_entrada = []
                        p1_salida = []

                        px = info_coordenadas[0][0]
                        py = info_coordenadas[0][1]
                        p1_entrada.append(py)
                        p1_entrada.append(px)
                        p1_entrada = tuple(p1_entrada)

                        px = info_coordenadas[1][0]
                        py = info_coordenadas[1][1]
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

                    if encontrado is False:
                        contador_intersecciones = len(intersecciones) - 2
                        while contador_intersecciones > 0 and encontrado is False:
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

                        if encontrado is False:

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

with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Clusterizados_LECMTZI.json", "w") as f6:
    json.dump(flujos_clusterizados, f6, indent=4)
f6.close()
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Aeropuertos_LECMTZI.json", "w") as outfile:
    json.dump(aeropuertos, outfile, indent=4)
outfile.close()
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Origenes_cluster_LECMTZI.json", "w") as outfile:
    json.dump(origenes_cluster, outfile, indent=4)
outfile.close()

with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Destinos_cluster_LECMTZI.json", "w") as outfile:
    json.dump(destinos_cluster, outfile, indent=4)
outfile.close()
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Asociacion_LECMTZI.json", "w") as f10:
    json.dump(asociacion_aeronaves_clusterizados, f10, indent=4)
f10.close()

tipo1_5_antes = len(tipo1_5.keys())
grupos_llegadas = []
grupos_despegues = []

for i in tipo1_5.keys():

    if len(origenes_cluster.get(i)) == 1 and origenes_cluster.get(i)[0] in aeropuertos:
        grupos_despegues.append(i)
    if len(destinos_cluster.get(i)) == 1 and destinos_cluster.get(i)[0] in aeropuertos:
        grupos_llegadas.append(i)

tipo1_5_antes = len(tipo1_5.keys())
grupos_llegadas = []
grupos_despegues = []
for i in tipo1_5.keys():
    if len(origenes_cluster.get(i)) == 1 and origenes_cluster.get(i)[0] in aeropuertos:
        grupos_despegues.append(i)
    if len(destinos_cluster.get(i)) == 1 and destinos_cluster.get(i)[0] in aeropuertos:
        grupos_llegadas.append(i)

remplazables = []
salidas = {}
for i in grupos_despegues:
    datos = tipo1_5.get(i)
    if len(salidas.keys()) == 0:
        lista = [datos[0]]
        salidas.update({i: lista})
    else:
        coordenadas_nuevas_entrada = []
        coordenadas_nuevas_salida = []

        coordenadas_nuevas_entrada.append(datos[0][0][1])
        coordenadas_nuevas_entrada.append(datos[0][0][0])
        coordenadas_nuevas_salida.append(datos[0][1][1])
        coordenadas_nuevas_salida.append(datos[0][1][0])
        coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)
        coordenadas_nuevas_salida = tuple(coordenadas_nuevas_salida)

        posibles_flujo = None
        dsalida_max = -1

        for j in salidas.keys():
            f = salidas.get(j)[0]

            c_n_s = [f[1][1], f[0][0]]
            c_n_s = tuple(c_n_s)

            d_s = geopy.distance.distance(c_n_s, coordenadas_nuevas_salida).km

            if d_s < 27:
                if (dsalida_max == -1) or (d_s < dsalida_max):
                    dsalida_max = d_s
                    posibles_flujo = j

        if posibles_flujo is None:
            lista = [datos[0]]
            salidas.update({i: lista})
        else:
            datos_flujo_salida = salidas.get(posibles_flujo)
            c_n_e = []
            c_n_s = []

            c_n_e.append(datos_flujo_salida[0][0][1])
            c_n_e.append(datos_flujo_salida[0][0][0])
            c_n_s.append(datos_flujo_salida[0][1][1])
            c_n_s.append(datos_flujo_salida[0][1][0])

            c_n_e = tuple(c_n_e)
            c_n_s = tuple(c_n_s)

            # lon
            entrada_media_1 = (c_n_e[1] + coordenadas_nuevas_entrada[1]) / 2
            # lat
            entrada_media_2 = (c_n_e[0] + coordenadas_nuevas_entrada[0]) / 2
            # lon
            salida_media_1 = (c_n_s[1] + coordenadas_nuevas_salida[1]) / 2
            # lat
            salida_media_2 = (c_n_s[0] + coordenadas_nuevas_salida[0]) / 2

            d1 = [entrada_media_1, entrada_media_2]
            d2 = [salida_media_1, salida_media_2]
            d1 = tuple(d1)
            d2 = tuple(d2)

            tupla = (d1, d2)
            datos_flujo_salida[0] = tupla
            datos_flujo_salida.append(i)
            salidas[posibles_flujo] = datos_flujo_salida

llegadas = {}
for i in grupos_llegadas:
    datos = tipo1_5.get(i)
    if len(llegadas.keys()) == 0:
        lista = [datos[0]]
        llegadas.update({i: lista})
    else:

        coordenadas_nuevas_entrada = []
        coordenadas_nuevas_salida = []

        coordenadas_nuevas_entrada.append(datos[0][0][1])
        coordenadas_nuevas_entrada.append(datos[0][0][0])
        coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)

        coordenadas_nuevas_salida.append(datos[0][1][1])
        coordenadas_nuevas_salida.append(datos[0][1][0])
        coordenadas_nuevas_salida = tuple(coordenadas_nuevas_salida)

        posibles_f = None
        de_max = -1

        for j in llegadas.keys():
            # Se comprueba que los destinos coincidan
            dest = destinos_cluster.get(j)
            if dest == destinos_cluster.get(i):
                f = llegadas.get(j)

                c_n_e = [f[0][0][1], f[0][0][0]]

                c_n_e = tuple(c_n_e)

                d_e = geopy.distance.distance(c_n_e, coordenadas_nuevas_entrada).km

                if d_e < 27:
                    if de_max == -1 or d_e < de_max:
                        de_max = d_e
                        posibles_f = j

        if posibles_f is None:
            lista = [datos[0]]
            llegadas.update({i: lista})
        else:
            df = llegadas.get(posibles_f)
            c_n_e = []
            c_n_s = []

            c_n_e.append(df[0][0][1])
            c_n_e.append(df[0][0][0])
            c_n_s.append(df[0][1][1])
            c_n_s.append(df[0][1][0])

            c_n_e = tuple(c_n_e)
            c_n_s = tuple(c_n_s)

            entrada_media_1 = (c_n_e[1] + coordenadas_nuevas_entrada[1]) / 2
            entrada_media_2 = (c_n_e[0] + coordenadas_nuevas_entrada[0]) / 2
            salida_media_1 = (c_n_s[1] + coordenadas_nuevas_salida[1]) / 2
            salida_media_2 = (c_n_s[0] + coordenadas_nuevas_salida[0]) / 2

            d1 = [entrada_media_1, entrada_media_2]
            d1 = tuple(d1)
            d2 = [salida_media_1, salida_media_2]
            d2 = tuple(d2)

            tupla = (d1, d2)
            df[0] = tupla
            df.append(i)
            llegadas[posibles_f] = df

cf = len(flujos_clusterizados.keys()) + 1

asociacion_reemplazables = {}

for i in salidas.keys():
    if len(salidas.get(i)) > 1:
        c_f = str(cf) + '_' + codigo_sector + '_CL'

        datos_s = [0, 0, 0]
        datos_e = [0, 0, 0]

        lista_flujos_salidas = []
        cont = 0
        for j in salidas.get(i):
            if cont == 0:
                lista_flujos_salidas.append(i)
                remplazables.append(i)

                info_flujo_clusterizado = flujos_clusterizados.get(i)
                datos_s = get_nivel(info_flujo_clusterizado[1][1], datos_s)
                datos_e = get_nivel(info_flujo_clusterizado[1][0], datos_e)

                cont += 1
            else:
                lista_flujos_salidas.append(j)
                remplazables.append(j)

                info_flujo_clusterizado = flujos_clusterizados.get(j)
                datos_s = get_nivel(info_flujo_clusterizado[1][1], datos_s)
                datos_e = get_nivel(info_flujo_clusterizado[1][0], datos_e)

                cont += 1

        ev = [seleccionar_nivel(datos_e), seleccionar_nivel(datos_s)]
        lista_datos = [salidas.get(i)[0], ev]
        tipo1_5.update({c_f: lista_datos})
        flujos_clusterizados.update({c_f: lista_datos})

        asociacion_flujos_clusterizados.update({c_f: lista_flujos_salidas})
        asociacion_reemplazables.update({c_f: lista_flujos_salidas})

        cf += 1
# %%
for i in llegadas.keys():
    if len(llegadas.get(i)) > 1:
        lista_flujos_llegadas = []
        cont = 0

        datos_s = [0, 0, 0]
        datos_e = [0, 0, 0]

        for j in llegadas.get(i):
            if cont == 0:
                if i not in remplazables:
                    lista_flujos_llegadas.append(i)
                    remplazables.append(i)
                    info_flujo_clusterizado = flujos_clusterizados.get(i)
                    datos_s = get_nivel(info_flujo_clusterizado[1][1], datos_s)
                    datos_e = get_nivel(info_flujo_clusterizado[1][0], datos_e)
                    cont += 1
            else:
                if j not in remplazables:
                    lista_flujos_llegadas.append(j)
                    remplazables.append(j)
                    info_flujo_clusterizado = flujos_clusterizados.get(j)
                    datos_s = get_nivel(info_flujo_clusterizado[1][1], datos_s)
                    datos_e = get_nivel(info_flujo_clusterizado[1][0], datos_e)
                    cont += 1

        if len(lista_flujos_llegadas) > 0:
            c_f = str(cf) + '_' + codigo_sector + '_CL'
            ev = [seleccionar_nivel(datos_e), seleccionar_nivel(datos_s)]
            lista_datos = [llegadas.get(i)[0], ev]
            tipo1_5.update({c_f: lista_datos})
            flujos_clusterizados.update({c_f: lista_datos})

            asociacion_flujos_clusterizados.update({c_f: lista_flujos_llegadas})
            asociacion_reemplazables.update({c_f: lista_flujos_llegadas})

            cf += 1
# %%
# Se eliminan los flujos que se han agrupado por entradas y salidas
for i in remplazables:
    tipo1_5.pop(i)
    flujos_clusterizados.pop(i)

print('Numero de flujos despues de quitar los origenes/destinos: ', len(flujos_clusterizados.keys()))

# Se actualizan las aeronaves agrupadas a los flujos que se acaban de eliminar
for i in asociacion_reemplazables.keys():
    dat = asociacion_reemplazables.get(i)
    naves = []
    for j in dat:
        aso = asociacion_aeronaves_clusterizados.get(j)
        for h in aso:
            naves.append(h)
        asociacion_aeronaves_clusterizados.pop(j)
    asociacion_aeronaves_clusterizados.update({i: naves})

fuera = []
cantidad1 = 0
cantidad2 = 0
# Se guardan los flujos que tengan menos de 100 aeronaves para eliminarlos
for i in asociacion_aeronaves_clusterizados.keys():
    cantidad1 += len(asociacion_aeronaves_clusterizados.get(i))
    if len(asociacion_aeronaves_clusterizados.get(i)) <= 100:
        cantidad2 += len(asociacion_aeronaves_clusterizados.get(i))
        fuera.append(i)

print('Número de aeronaves que se pierden al quitar los flujos < 100: ', cantidad2 / cantidad1)

for i in fuera:
    asociacion_aeronaves_clusterizados.pop(i)
    flujos_clusterizados.pop(i)

print('Numero de flujos al quitar los de menos de 100: ', len(flujos_clusterizados.keys()))

# Tipo1
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Tipo1_LECMTZI.json", "w") as f7:
    json.dump(tipo1, f7, indent=4)
f7.close()
# Tipo1.5
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Tipo1.5_LECMTZI.json", "w") as f8:
    json.dump(tipo1_5, f8, indent=4)
f8.close()
# Tipo2
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Tipo2_LECMTZI.json", "w") as f9:
    json.dump(tipo2, f9, indent=4)
f9.close()
# Asociacion2
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Asociacion2_LECMTZI.json", "w") as f10:
    json.dump(asociacion_aeronaves_clusterizados, f10, indent=4)
f10.close()
# Clusterizados2
with open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Clusterizados2_LECMTZI.json", "w") as f6:
    json.dump(flujos_clusterizados, f6, indent=4)
f6.close()

# %%
# Se preparan listas de longitud igual a las naves extraidas del
# fichero al principio para guardar los nuevos flujos clusterizados
flujo_original = [0] * naves.size
flujo_final = [0] * naves.size
c = 0
contador = contador_esp[c]
contador2 = 0

while contador2 < naves.size:
    nave_a_estudiar = naves[contador]

    condicion = True
    if nave_a_estudiar not in vuelos.keys():
        # Si no se ha estudiado la nave porque no cumple con la expresion regex de aviones comerciales
        # Se marcan como flujo 0
        flujo_original[contador2] = str(0)
        flujo_final[contador2] = str(0)
        condicion = False
    else:
        f_original = None
        # Se busca a la aeronave en la lista de asociaciones de cada flujo original (los primeros creados)
        for j in asociacion_aeronaves.keys():
            aso_vuelos = asociacion_aeronaves.get(j)
            if nave_a_estudiar in aso_vuelos:
                flujo_original[contador2] = j
                break

        f_final = None
        # Se busca en los flujos clusterizados
        for g in asociacion_aeronaves_clusterizados.keys():
            aso_flujos = asociacion_aeronaves_clusterizados.get(g)
            if str(nave_a_estudiar) in aso_flujos:
                flujo_final[contador2] = g
                condicion = False
                break

    if condicion:
        # Si por algun casual no se ha encontrado en algun flujo, se ajusta al flujo 0
        flujo_original[contador2] = '0'
        flujo_final[contador2] = '0'
        condicion = False

    if (contador2 + 1) == naves.size:
        break
    else:
        c += 1
        contador = contador_esp[c]
        contador2 += 1

base_datos_reducida['Flujo_Original'] = flujo_original
base_datos_reducida['Flujo_Clusterizado'] = flujo_final
# Se eliminan las aeronaves de flujo clusterizado 0 porque no se usan
base_datos2 = base_datos_reducida.loc[base_datos_reducida['Flujo_Clusterizado'] != '0']
base_datos2.to_csv(FILES_PATH + "\\Carpeta_CSV\\LECMTZI_Final.csv", index=False, sep=",")
