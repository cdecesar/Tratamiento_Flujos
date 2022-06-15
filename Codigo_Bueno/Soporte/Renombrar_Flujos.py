#%%
import json
import pathlib
FILES_PATH = str(pathlib.Path(__file__).parent.resolve())


codigo_sector = input('Codigo del sector: ')
nombre_carpeta = input('Nombre de la carpeta: ')

with  open(FILES_PATH + '\\JSON_Cargados\\' + nombre_carpeta + '\\Clusterizados2_' + codigo_sector + '.json', "r") as f6:
    flujos_clusterizados = json.load(f6)
f6.close()
with  open(FILES_PATH + '\\JSON_Cargados\\' + nombre_carpeta + '\\Asociacion2_' + codigo_sector + '.json', "r") as f6:
    asociacion_aeronaves_clusterizados = json.load(f6)
f6.close()

contador = 1
flujos_2 = {}
asoci_2 = {}
for i in flujos_clusterizados.keys():
    c_f = str(contador) + '_' + codigo_sector + '_CL'

    a = flujos_clusterizados.get(i)
    b = asociacion_aeronaves_clusterizados.get(i)
    flujos_2.update({c_f: a})
    asoci_2.update({c_f:b})

with  open(FILES_PATH + '\\JSON_Cargados\\' + nombre_carpeta + '\\Clusterizados3_' + codigo_sector + '.json', "r") as f6:
    json.dump(flujos_2, f6, indent=4)
f6.close()
with  open(FILES_PATH + '\\JSON_Cargados\\' + nombre_carpeta + '\\Asociacion3_' + codigo_sector + '.json', "r") as f6:
    json.dump(asoci_2, f6, indent=4)
f6.close()