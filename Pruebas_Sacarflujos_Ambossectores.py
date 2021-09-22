import pandas
import Pruebas_SacarFlujos_SUB
import re
from matplotlib import pyplot
from shapely.geometry import Polygon

bloc_notas = open(
        "C:\\DATOS\\TRABAJO_CRIDA\\REPORTS\\YYYYYYEEEEE" + ".txt", 'w')

base_datos = pandas.read_csv("C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\Base_Datos_Principal.csv", delimiter=';')

''' Este es el sector 1'''
df = base_datos.loc[base_datos.SectorCode=='LECMCJI',:]

''' Este es el sector 2'''
df2 = base_datos.loc[base_datos.SectorCode=='LECMPAU',:]

datos = df.loc[:,['flightkey','routeKey','adep','ades','lat_IN','lat_OUT', 'lng_IN', 'lng_OUT', 'attitud_IN', 'attitud_OUT']]
datos2 = df2.loc[:,['flightkey','routeKey','adep','ades','lat_IN','lat_OUT', 'lng_IN', 'lng_OUT', 'attitud_IN', 'attitud_OUT']]


c = 0
routeKey = datos['routeKey']
naves = datos['flightkey']
l_in = datos['lat_IN']
lo_in = datos['lng_IN']
l_out = datos['lat_OUT']
lo_out = datos['lng_OUT']
nivel_ent = datos['attitud_IN']
nivel_sal = datos['attitud_OUT']
contador = datos.index

routeKey2 = datos2['routeKey']
naves2 = datos2['flightkey']
l_in2 = datos2['lat_IN']
lo_in2 = datos2['lng_IN']
l_out2 = datos2['lat_OUT']
lo_out2 = datos2['lng_OUT']
nivel_ent2 = datos2['attitud_IN']
nivel_sal2 = datos2['attitud_OUT']
contador3 = datos2.index

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

path_poligono = 'C:\\DATOS\\TRABAJO_CRIDA\\DATOS\\poligonos_sectores_2D.csv'

fich = pandas.read_csv(path_poligono, delimiter=';')
a = fich['PolygonToString']

b = re.split(",", a[3])
l = obtener_poligono(b)
poligono = Polygon(l)
x, y = poligono.exterior.xy
pyplot.plot(x, y)

z = re.split(",", a[2])
l = obtener_poligono(z)
poligono2 = Polygon(l)
x, y = poligono2.exterior.xy
pyplot.plot(x, y)

los_dibujados_sector1, flujos_c_s1, flujos_c2_s1, aso_s1, flujo_or_s1, flujo_final_s1 = Pruebas_SacarFlujos_SUB.main(naves, l_in, lo_in, l_out, lo_out, contador, bloc_notas)
los_dibujados_sector2, flujos_c_s2, flujos_c2_s2, aso_s2, flujo_or_s2, flujo_final_s2 = Pruebas_SacarFlujos_SUB.main(naves2, l_in2, lo_in2, l_out2, lo_out2, contador3,bloc_notas)

datos['Flujo_Inventado'] = flujo_or_s1
datos['Flujo_Clusterizado_Final'] = flujo_final_s1
datos2['Flujo_Inventado2'] = flujo_or_s2
datos2['Flujo_Clusterizado_Final2'] = flujo_final_s2

parejas_flujos = Pruebas_SacarFlujos_SUB.main2(datos, datos2, bloc_notas)
Pruebas_SacarFlujos_SUB.dibujar_flujos_concretos(flujos_c_s1,flujos_c_s2,flujos_c2_s1,flujos_c2_s2,los_dibujados_sector1,los_dibujados_sector2,parejas_flujos)

print("FINALIZADO")