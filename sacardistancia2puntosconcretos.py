import pandas
import geopy.distance

fichero1 = pandas.read_excel("C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Documento_Flujos.xlsx")
fichero2 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Puntos.xlsx')

primera_fila = fichero1['rutaExtend'][0]
segunda_fila = fichero1['rutaExtend'][1]

n1 = ""
n2 = ""

for i in primera_fila:
    letra = i
    if i != "-":
        n1 += i
    else:
        break
for i in segunda_fila:
    letra = i
    if i == "-":
        break
    else:
        n2 += i

diccionario = {}

nombres = fichero2['NAME_TXT']
latitud = fichero2['LAT_TXT']
longitud = fichero2['LONG_TXT']
contador2 = 0

for nombre in nombres:
    datos = {nombre: [latitud[contador2], longitud[contador2]]}
    diccionario.update(datos)
    contador2 += 1

p1 = diccionario.get(n1)
p2 = diccionario.get(n2)
p12 = []
p22 = []

for i in p1:
    g = 0
    m = 0
    s = 0
    l = ""
    if len(i) == 7:
        g = float(i[:2])
        m = float(i[2:4])
        s = float(i[4:6])
        l = i[-1]
    else:
        g = float(i[:3])
        m = float(i[3:5])
        s = float(i[5:7])
        l = i[-1]

    c = g + (m/60) + (s/3600)
    if (l == "W") or (l == "S"):
        c *= -1
    p12.append(c)

for i in p2:
    g = 0
    m = 0
    s = 0
    l = ""
    if len(i) == 7:
        g = float(i[:2])
        m = float(i[2:4])
        s = float(i[4:6])
        l = i[-1]
    else:
        g = float(i[:3])
        m = float(i[3:5])
        s = float(i[5:7])
        l = i[-1]

    c = g + (m / 60) + (s / 3600)
    if (l == "W") or (l == "S"):
        c *= -1
    p22.append(c)
p12 = tuple(p12)
p22 = tuple(p22)

print(geopy.distance.distance(p12, p22).km)

if len(latitud[contador2]) == 7:
    g = float(latitud[contador2][:2])
    m = float(latitud[contador2][2:4])
    s = (latitud[contador2][4:6])
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
print(nombre + "      " + str(lat))
datos = {nombre: [lat, lon]}
diccionario.update(datos)