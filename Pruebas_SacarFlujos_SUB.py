from shapely.geometry import Polygon, Point, LineString, box
import geopy.distance
from matplotlib import pyplot
import pandas
import random

def main(naves, l_in, lo_in, l_out, lo_out, contador_esp, bloc_notas):
    c = 0
    contador = contador_esp[c]
    contador2 = 0
    flujos_repetidos = []
    vuelos_repetidos = []
    niveles_flujos = {}
    flujos = {}
    vuelos = {}
    c_flujos = 1

    while contador2 < naves.size:
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

        if p1 != p2:
            coordenadas = []
            coordenadas.append(p1)
            coordenadas.append(p2)

            vuelos.update({v: coordenadas})

        if (contador2 + 1) == naves.size:
            break
        else:
            c += 1
            contador = contador_esp[c]
            contador2 += 1

    print("HECHO")
    coordenadas_nuevos_flujos = {}
    asociacion_aeronaves = {}
    final_bucle = 0

    for i in vuelos.keys():
        final_bucle += 1
        print(final_bucle)
        # if final_bucle == 20000:
        # break
        # if final_bucle > 10000:

        v = vuelos.get(i)
        if len(coordenadas_nuevos_flujos.keys()) == 0:
            v = tuple(v)
            l = []
            l.append(i)
            coordenadas_nuevos_flujos.update({c_flujos: v})
            asociacion_aeronaves.update({c_flujos: l})
            c_flujos += 1
        else:
            coordenadas_nuevas_entrada = []
            coordenadas_nuevas_salida = []

            coordenadas_nuevas_entrada.append(v[0][1])
            coordenadas_nuevas_entrada.append(v[0][0])
            coordenadas_nuevas_salida.append(v[1][1])
            coordenadas_nuevas_salida.append(v[1][0])

            coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)
            coordenadas_nuevas_salida = tuple(coordenadas_nuevas_salida)

            comprobacion = 0
            posibles_f = None
            de_max = -1
            ds_max = -1

            for j in coordenadas_nuevos_flujos.keys():
                avion2 = coordenadas_nuevos_flujos.get(j)
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

                if d_e < 10 and d_s < 10:
                    if (de_max == -1 and ds_max == -1) or (d_e < de_max and d_s < ds_max):
                        de_max = d_e
                        ds_max = d_s
                        posibles_f = j
                else:

                    d_e = geopy.distance.distance(c_n_e, coordenadas_nuevas_salida).km
                    d_s = geopy.distance.distance(c_n_s, coordenadas_nuevas_entrada).km
                    if d_e < 10 and d_s < 10:
                        if (de_max == -1 and ds_max == -1) or (d_e < de_max and d_s < ds_max):
                            de_max = d_e
                            ds_max = d_s
                            posibles_f = j

            if posibles_f == None:
                v = tuple(v)
                l = []
                l.append(i)
                coordenadas_nuevos_flujos.update({c_flujos: v})
                asociacion_aeronaves.update({c_flujos: l})
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

        bloc_notas.write("Vuelo " + str(i) + "\n")
        final_bucle += 1
    # else:
    # final_bucle += 1

    print("HECHO")

    R = 27

    for i in coordenadas_nuevos_flujos.keys():
        bloc_notas.write("Flujo" + str(i) + "   " + str(asociacion_aeronaves.get(i)) + "\n")

    diccionario_distancias = {}
    lista_max_longitudes = []

    for key in coordenadas_nuevos_flujos.keys():
        vuelo = key
        puntos = []

        for k in coordenadas_nuevos_flujos.keys():
            if k != key:
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
    print("HECHO")

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
    print("HECHO")

    ya_dibujados = []
    ya_dibujados_indices = []
    flujos_total = 0

    flujos_clusterizados = {}
    asociacion_flujos_clusterizados = {}
    flujos_clusterizados_origenes_destinos = {}
    contador_flujos = 1
    longitudes_flujos = {}

    for i in diccionario_flujos_agrupados.keys():
        flujo = diccionario_flujos_agrupados.get(i)

        if flujo not in ya_dibujados:
            ya_dibujados.append(flujo)
            ya_dibujados_indices.append(contador_flujos)
            datos_f = {str(contador_flujos): flujo}
            flujos_clusterizados.update(datos_f)

            todos_flujos = []
            todos_flujos.append(i)
            asociacion_flujos_clusterizados.update({str(contador_flujos): todos_flujos})

            contador_flujos += 1
            flujos_total += 1
        else:
            for q in flujos_clusterizados.keys():
                result = flujos_clusterizados.get(q)
                if result == flujo:
                    asociacion_flujos_clusterizados.get(q).append(i)
                    break

    print("HECHO")
    diccionario_longitudes = {}

    for i in flujos_clusterizados.keys():
        ps = flujos_clusterizados.get(i)
        line = LineString(ps)
        lista_cercanos = []

        for j in flujos_clusterizados.keys():
            if i != j:
                dot = flujos_clusterizados.get(j)
                line2 = LineString(dot)
                if line2.length > line.length:
                    p_ent = line2.interpolate(line2.project(Point(ps[0])))
                    p_sal = line2.interpolate(line2.project(Point(ps[1])))
                    print(p_ent, p_sal)
                    dent = (p_ent.y, p_ent.x)
                    dsal = (p_sal.y, p_sal.x)
                    print(dent, dsal)
                    lent = (ps[0][1], ps[0][0])
                    lsal = (ps[1][1], ps[1][0])

                    distanciae = geopy.distance.distance(dent, lent).km
                    distancias = geopy.distance.distance(dsal, lsal).km
                    print(distanciae)
                    print(distancias)
                    print("--------------")
                    if distanciae < 18 and distancias < 18:
                        lista_cercanos.append([j, line2.length])
        max_len = -1
        max_f = ""
        if len(lista_cercanos) > 0:
            for j in lista_cercanos:
                l = j[1]
                f = j[0]
                if l > max_len:
                    max_len = l
                    max_f = f
            diccionario_longitudes.update({i: max_f})

    flujos_clusterizados2 = {}
    los_dibujados = []

    for i in flujos_clusterizados.keys():
        if i not in diccionario_longitudes.keys():
            a = flujos_clusterizados.get(i)
            los_dibujados.append(i)
            #l = LineString(a)
            #xx, yy = l.xy
            #pyplot.plot(xx, yy)
        else:
            max_f = diccionario_longitudes.get(i)
            if max_f in flujos_clusterizados2.keys():
                flujos_clusterizados2.get(max_f).append(i)
            else:
                w = []
                w.append(i)
                r = {max_f: w}
                flujos_clusterizados2.update(r)
    #pyplot.show()
    flujo_original = []
    flujo_final = []
    c = 0
    contador = contador_esp[c]
    contador2 = 0

    while contador2 < naves.size:
        nave_a_estudiar = naves[contador]

        if nave_a_estudiar not in vuelos.keys():
            flujo_original.append(str(0))
            flujo_final.append(str(0))

        else:
            f_original = None
            for j in asociacion_aeronaves.keys():
                aso_vuelos = asociacion_aeronaves.get(j)
                if nave_a_estudiar in aso_vuelos:
                    f_original = j
                    break
            f_final = None
            for g in asociacion_flujos_clusterizados.keys():
                aso_flujos = asociacion_flujos_clusterizados.get(g)
                if f_original in aso_flujos:
                    f_final = g
                    break
            flujo_original.append(str(f_original))
            flujo_final.append(str(f_final))

        if (contador2 + 1) == naves.size:
            break
        else:
            c += 1
            contador = contador_esp[c]
            contador2 += 1

    return los_dibujados, flujos_clusterizados, flujos_clusterizados2, asociacion_flujos_clusterizados, flujo_original, flujo_final

def main2(datos1, datos2, bloc):
    dataframe_unido = datos1.merge(datos2, left_on=['Flightkey'], right_on=['Flightkey'], how='inner')

    c = 0
    n = dataframe_unido['Flightkey']
    contador = dataframe_unido.index[c]
    contador2 = 0

    parejas_flujos = []
    while contador2 < n.size:
        f1 = dataframe_unido['Flujo_Clusterizado_Final'][contador]
        f2 = dataframe_unido['Flujo_Clusterizado_Final2'][contador]

        l = []
        l.append(f1)
        l.append(f2)

        if l not in parejas_flujos:
            parejas_flujos.append(l)
            bloc.write("Nueva pareja de flujos entre sectores " + str(l) + "\n")

    return parejas_flujos

def dibujar_flujos_concretos(flujos_c_s1, flujos_c_s2, flujos_c2_s1, flujos_c2_s2, dibujados_s1, dibujados_s2, parejas_flujos):
    bloc_notas2 = open(
        "C:\\DATOS\\TRABAJO_CRIDA\\REPORTS\\Flujos Compartidos" + ".txt", 'w')

    for i in parejas_flujos:
        bloc_notas2.write("Flujos compartidos" + "  " + str(i) + "\n")
        a = i[0]
        b = i[1]

        if a in dibujados_s1:
            data = flujos_c_s1.get(a)
            l = LineString(data)
            xx, yy = l.xy
            pyplot.plot(xx, yy)
            bloc_notas2.write("Sector1 " + str(a) + "   " + str(data))
        elif a in dibujados_s2:
            data = flujos_c_s2.get(a)
            l = LineString(data)
            xx, yy = l.xy
            pyplot.plot(xx, yy)
            bloc_notas2.write("Sector2 " + str(a) + "   " + str(data))
        else:
            limit = False
            for j in flujos_c2_s1.keys():
                if limit == False:
                    fs = flujos_c2_s1.get(j)
                    if a in fs:
                        data = flujos_c_s1.get(j)
                        l = LineString(data)
                        xx, yy = l.xy
                        pyplot.plot(xx, yy)
                        limit = True
                        bloc_notas2.write("Sector1: a no lo dibujamos porque se queda a mitad. Dibujamos a quien lo agrupa " + str(j) + "   " + str(data))
                else:
                    break
            if limit == False:
                for j in flujos_c2_s2.keys():
                    if limit == False:
                        fs = flujos_c2_s2.get(j)
                        if a in fs:
                            data = flujos_c_s2.get(j)
                            l = LineString(data)
                            xx, yy = l.xy
                            pyplot.plot(xx, yy)
                            limit = True
                            bloc_notas2.write(
                                "Sector2: a no lo dibujamos porque se queda a mitad. Dibujamos a quien lo agrupa " + str(
                                    j) + "   " + str(data))
                    else:
                        break

        if b in dibujados_s1:
            data = flujos_c_s1.get(a)
            l = LineString(data)
            xx, yy = l.xy
            pyplot.plot(xx, yy)
            bloc_notas2.write("Sector1 " + str(b) + "   " + str(data))
        elif b in dibujados_s2:
            data = flujos_c_s2.get(a)
            l = LineString(data)
            xx, yy = l.xy
            pyplot.plot(xx, yy)
            bloc_notas2.write("Sector2 " + str(b) + "   " + str(data))
        else:
            limit = False
            for j in flujos_c2_s1.keys():
                if limit == False:
                    fs = flujos_c2_s1.get(j)
                    if b in fs:
                        data = flujos_c_s1.get(j)
                        l = LineString(data)
                        xx, yy = l.xy
                        pyplot.plot(xx, yy)
                        limit = True
                        bloc_notas2.write("Sector1: b no lo dibujamos porque se queda a mitad. Dibujamos a quien lo agrupa " + str(j) + "   " + str(data))
                else:
                    break
            if limit == False:
                for j in flujos_c2_s2.keys():
                    if limit == False:
                        fs = flujos_c2_s2.get(j)
                        if b in fs:
                            data = flujos_c_s2.get(j)
                            l = LineString(data)
                            xx, yy = l.xy
                            pyplot.plot(xx, yy)
                            limit = True
                            bloc_notas2.write(
                                "Sector2: b no lo dibujamos porque se queda a mitad. Dibujamos a quien lo agrupa " + str(
                                    j) + "   " + str(data))
                    else:
                        break
    bloc_notas2.close()
    pyplot.show()


