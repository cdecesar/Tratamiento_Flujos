import pandas
import geopy.distance
from PATH import PATH

fichero1 = pandas.read_excel("C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Documento_Flujos.xlsx")
fichero2 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Puntos.xlsx')
fichero3 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Radioayudas.xlsx')

fila_nombres = fichero1['rutaExtend']
sector = fichero1['SectorCode']
t = 0
for i in sector:
    if i == 'LECMPAU':
        t += 1
print(t)

print(fila_nombres.size)

contador_1 = 0
lista_nombres = []

while contador_1 < fila_nombres.size:
    if sector[contador_1] == 'LECMPAU':
        palabra = fila_nombres[contador_1]
        n1 = ""
        for i in palabra:
            if i != "-":
                n1 += i
            else:
                break

        if n1 not in lista_nombres:
            print(n1)
            lista_nombres.append(n1)

    contador_1 += 1

print(len(lista_nombres))

diccionario = {}
print(len(diccionario.keys()))

nombres = fichero2['IDENT_TXT']
latitud = fichero2['LAT_TXT']
longitud = fichero2['LONG_TXT']
contador2 = 0

for nombre in nombres:

        if nombre in lista_nombres:
            lat = 0
            lon = 0

            #print(latitud[contador2])
            #print(contador2)
            #print(nombre)
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
            #print(nombre +"      " + str(lat))
            datos = {nombre: [lat, lon]}

            diccionario.update(datos)

        contador2 += 1

print(len(diccionario.keys()))

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
    #print(punto + "         " + str(puntos))
    #print(data2)


#print(len(lista_max_longitudes))
#print(lista_max_longitudes[0][1])
#print(lista_max_longitudes[len(lista_max_longitudes) - 1][1])


num = 0
p = ""
for key in lista_max_longitudes:
    if key[1] > num:
        num = key[1]
        p = key[0]

print(p + "    " + str(num))
lista_puntos_sin_coincidencia = []
for i in lista_nombres:
    if i not in lista_aux:
        lista_puntos_sin_coincidencia.append(i)

print(lista_puntos_sin_coincidencia)
