import pandas
import geopy.distance

fichero1 = pandas.read_excel("C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Documento_Flujos.xlsx")
#fichero2 = pandas.read_excel('C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros\\Puntos')

print(fichero1.columns)

primera_fila = fichero1['poligono'][0]
primera_fila = primera_fila[12:]
print(primera_fila)
contador = 0
comas = 0
lon1 = 0
lat1 = 0
lon2 = 0
lat2 = 0
palabra = ""

while comas < 2:
    letra = primera_fila[contador]
    if comas == 0:
        if letra == ",":
            lat1 = float(palabra)
            contador += 1
            comas += 1
            palabra = ""
        elif letra == " ":
            lon1 = float(palabra)
            palabra = ""
        else:
            palabra += letra

        contador += 1
    else:
        if letra == ",":
            lat2 = float(palabra)
            contador += 1
            comas += 1
            palabra = ""
        elif letra == " ":
            lon2 = float(palabra)
            palabra = ""
        else:
            palabra += letra

        contador += 1

print(lat1, lon1)
print(lat2, lon2)