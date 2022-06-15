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
from shapely.geometry import Polygon, Point, LineString, box

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

#%%
'''Sacar el numero de aeronaves por flujo clusterizado'''
with open(FILES_PATH + '\\JSON_Cargados\\Castejon\\Asociacion_LECMCJI.json', "r") as f6:
    datos = json.load(f6)
f6.close()
l = []
v = []
for i in datos.keys():
    l.append(i)
    v.append(len(datos.get(i)))
data = pandas.DataFrame()
data['Flujo'] = l
data['Numero'] = v
data.to_csv('JAJA.csv', index=False, sep=',')


#%%
'''Eliminar los flujos que no tienen mas de 100 vuelos'''
with open(FILES_PATH + '\\JSON_Cargados\\Castejon\\Asociacion_LECMCJI.json', "r") as f6:
    datos = json.load(f6)
f6.close()
with open(FILES_PATH + '\\Carpeta_JSON\\Clusterizados2_LECMCJI.json', "r") as f6:
    datos2 = json.load(f6)
f6.close()
with open(FILES_PATH + '\\Carpeta_JSON\\Reestructurados_LECMCJI.json', "r") as f6:
    datos3 = json.load(f6)
f6.close()

print(len(datos.keys()), len(datos2.keys()), len(datos3.keys()))
fuera = []
for i in datos.keys():
    if len(datos.get(i)) <= 100:
        fuera.append(i)
print(len(fuera))

for i in fuera:
    datos.pop(i)
    datos2.pop(i)
print(len(datos.keys()), len(datos2.keys()), len(datos3.keys()))


#%%
'''Nuevo JSON con flujos con mas de 100 vuelos'''
codigo_sector = 'LECMCJI'
contador = 1
flujos_2 = {}
asoci_2 = {}
for i in datos2.keys():
    c_f = str(contador) + '_' + codigo_sector + '_CL'
    hh = re.split('_', i)
    ddd = hh[0] + '_' + codigo_sector + '_' + hh[2]
    a = datos2.get(i)
    b = datos.get(i)
    flujos_2.update({i: a})
    asoci_2.update({i:b})
    print(i, c_f)
    contador += 1

with  open(FILES_PATH + '\\JSON_Cargados\\Clusterizados3_LECMCJI.json', "w") as f6:
    json.dump(flujos_2, f6, indent=4)
f6.close()


#%%
'''Cargamos los nuevos flujos y juntamos 2 sectores para ver como quedarian ahora'''
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
for i in datos.keys():
    a = re.split("-", i)

    if a[0] in datos3.keys() and a[1] in datos2.keys():
        l1 = LineString(datos3.get(a[0])[0])
        l2 = LineString(datos2.get(a[1])[0])
        x, y = l1.xy
        pyplot.plot(x, y)
        x, y = l2.xy
        pyplot.plot(x, y)

path_poligono = FILES_PATH + '\\Archivos\\poligonos_sectores_2D_2.0.csv'
fich = pandas.read_csv(path_poligono, delimiter=';')
a = fich['PolygonToString']

b = re.split(",", a[8])
l = obtener_poligono(b)
poligono2 = Polygon(l)
x, y = poligono2.exterior.xy
pyplot.plot(x, y)

b = re.split(",", a[4])
l = obtener_poligono(b)
poligono2 = Polygon(l)
x, y = poligono2.exterior.xy
pyplot.plot(x, y)
pyplot.show()
print(numero)

