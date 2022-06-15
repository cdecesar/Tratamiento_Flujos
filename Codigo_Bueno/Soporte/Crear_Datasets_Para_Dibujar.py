#%%
import re
import json
import pandas
import pathlib
import shapely
from shapely.geometry import Polygon
'''Generar un csv para que se puedan dibujar los flujos en R'''
FILES_PATH = str(pathlib.Path(__file__).parent.resolve())
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Sin_Niveles_LECMPAU.json", "r") as f6:
    data = json.load(f6)
f6.close()

dataset = pandas.DataFrame()

lon = []
lat = []
flujo = []

for i in data.keys():
    a = data.get(i)
    lon.append(a[0][0])
    lat.append(a[0][1])
    flujo.append(i)
    lon.append(a[1][0])
    lat.append(a[1][1])
    flujo.append(i)

dataset['lon'] = lon
dataset['lat'] = lat
dataset['flujo'] = flujo

dataset.to_csv('Dataset_Pamplona_Sin_Clusterizar.csv', index=False, sep=',')

#%%
'''Generar el csv para los flujos que quedan al juntar 2 sectores'''

with open(FILES_PATH + '\\JSON_Uniones\\LECMCJI_LECMPAU_Uniones.json', "r") as f6:
    datos = json.load(f6)
f6.close()


lat = []
lon = []
nombre = []
for i in datos.keys():
    lat.append(datos.get(i)[0][0][1])
    lon.append(datos.get(i)[0][0][0])
    nombre.append(i)
    lat.append(datos.get(i)[0][1][1])
    lon.append(datos.get(i)[0][1][0])
    nombre.append(i)
    lat.append(datos.get(i)[1][1][1])
    lon.append(datos.get(i)[1][1][0])
    nombre.append(i)

data = pandas.DataFrame()
data['Nombre'] = nombre
data['Longitud'] = lon
data['Latitud'] = lat

data.to_csv('Uniones_LECMCJI_LECMPAU.csv', index=False, sep=',')
#%%
'''Generar un csv para poder dibujar el sector en R'''

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

path_poligono = 'C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\poligonos_sectores_2D_2.0.csv'

fich = pandas.read_csv(path_poligono, delimiter=';')
a = fich['PolygonToString']

b = re.split(",", a[5])
l = obtener_poligono(b)

dataset2 = pandas.DataFrame()
lon = []
lat = []
poligono = []
for i in l:
    lon.append(i[0])
    lat.append(i[1])
    poligono.append('Canarias')

dataset2['lon'] = lon
dataset2['lat'] = lat
dataset2['poligono'] = poligono

dataset2.to_csv('Dataset_Poligono_Pamplona.csv', index=False, sep=',')
