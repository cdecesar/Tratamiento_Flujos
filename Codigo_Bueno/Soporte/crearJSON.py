#%%
'''Crear los JSON para un sector desde 0'''
import pathlib
FILES_PATH = str(pathlib.Path(__file__).parent.resolve())

import json
s = {}

with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Aeropuertos_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Asociacion_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Clusterizados_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Clusterizados2_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Destinos_cluster_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Origenes_cluster_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Tipo1_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Tipo1.5_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Tipo2_LECMDGU.json", "w") as f6:
    json.dump(s, f6, indent=4)
f6.close()
#%%
s = {}
with  open(FILES_PATH + "\\JSON_Cargados\\Barcelona\\Asociacion2_LECBP2R.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Canarias\\Asociacion2_GCCCRNE.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Castejon\\Asociacion2_LECMCJI.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Domingo\\Asociacion2_LECMDGU.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Pamplona\\Asociacion2_LECMPAU.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\TLU\\Asociacion2_LECMTLU.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
with  open(FILES_PATH + "\\JSON_Cargados\\Zaragoza\\Asociacion2_LECMTZI.json", "w") as f10:
    json.dump(s, f10, indent=4)
f10.close()
print(111111)