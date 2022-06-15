#%%
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

with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Clusterizados2_LECMPAU.json", "r") as f6:
    data = json.load(f6)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Asociacion_LECMPAU.json", "r") as f6:
    asociaciones = json.load(f6)
f6.close()

#%%
puntos = {}
relacion = {}
punto_contador = 1
for i in data.keys():
    if len(puntos.keys()) == 0:
        datos = data.get(i)

        id = "Punto" + str(punto_contador)
        punto_contador += 1
        id2 = "Punto" + str(punto_contador)
        l1 = []
        l2 = []
        l1.append(i)
        l2.append(i)
        puntos.update({id : datos[0][0]})
        relacion.update({id: l1})
        puntos.update({id2 : datos[0][1]})
        relacion.update({id2: l2})
        punto_contador += 1

    else:
        datos = data.get(i)

        for k in range(2):
            coordenadas_nuevas_entrada = []

            coordenadas_nuevas_entrada.append(datos[0][k][1])
            coordenadas_nuevas_entrada.append(datos[0][k][0])

            # print(final_bucle, coordenadas_nuevas_entrada, coordenadas_nuevas_salida)
            coordenadas_nuevas_entrada = tuple(coordenadas_nuevas_entrada)

            comprobacion = 0
            posibles_p = None
            de_max = -1

            for j in puntos.keys():
                datos2 = puntos.get(j)

                c_n_e = []

                c_n_e.append(datos2[1])
                c_n_e.append(datos2[0])

                c_n_e = tuple(c_n_e)
                d_e = geopy.distance.distance(c_n_e, coordenadas_nuevas_entrada).km

                if d_e < 5:
                    if de_max == -1 or d_e < de_max:
                        de_max = d_e
                        posibles_p = j

            if posibles_p == None:
                id2 = "Punto" + str(punto_contador)
                punto_contador += 1
                puntos.update({id2: datos[0][k]})
                l1 = []
                l1.append(i)
                relacion.update({id2: l1})
            else:
                punto_elegido = puntos.get(posibles_p)
                lon = (punto_elegido[1] + coordenadas_nuevas_entrada[1]) / 2
                lat = (punto_elegido[0] + coordenadas_nuevas_entrada[0]) / 2
                d1 = []
                d1.append(lon)
                d1.append(lat)

                puntos[posibles_p] = d1

                l1 = relacion.get(posibles_p)
                l1.append(i)
                relacion[posibles_p] = l1

'''Numero de puntos y flujos'''

p = pandas.DataFrame()
o = []
ñ = []
o.append(len(puntos.keys()))
ñ.append(len(data.keys()))
p['Numero de puntos'] = o
p['Numero de flujos'] = ñ
p.to_csv("Puntos_Pamplona.csv", index=False, sep=",")

'''Cargamos en diferentes JSON los puntos y las relaciones entre ellos'''

with  open(FILES_PATH + "\\Datos\\Coordenadas_Puntos_GCCCRNE.json", "w") as f6:
    json.dump(puntos, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\Datos\\Relacion_Puntos_Flujos_GCCCRNE.json", "w") as f6:
    json.dump(relacion, f6, indent=4)
f6.close()


#%%
'''Guardamos los flujos que hay por cada punto y el total de naves que pasan por cada uno'''
x = pandas.DataFrame()
nombre = []
l = []
for i in relacion.keys():
    nombre.append(i)
    l.append(len(relacion.get(i)))
x['Punto'] = nombre
x['Numero Flujos/Punto'] = l

s = []
for j in relacion.keys():
    a = relacion.get(j)
    suma = 0
    for k in a:
        suma += len(asociaciones.get(k))
    s.append(suma)
x['Numero de Aviones'] = s
x.to_csv('Densidad.csv', index=False, sep=';')

