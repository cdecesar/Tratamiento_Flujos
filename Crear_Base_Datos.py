import os, glob

import pandas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

bloc_notas = open(
        "C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros2\\Info_datos_cada_paso " + ".txt", 'w')

path = "C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros2\\Flight_Info"

all_files = glob.glob(os.path.join(path, "*.csv"))
all_df = []
for f in all_files:
    df = pd.read_csv(f, sep=';')
    df['file'] = f.split('/')[-1]
    all_df.append(df)

merged_df = pd.concat(all_df, ignore_index=True, sort=True)
print(len(merged_df))
merged_df['duplicados'] = merged_df.duplicated()
print(merged_df[merged_df["duplicados"]==True])
e = merged_df.drop(merged_df[merged_df["duplicados"]==True].index, axis=0)
print(len(e))
print("EY")
print(merged_df.head())
merged_df.to_csv("Flights_Unidos.csv", index=False, sep=";")

bloc_notas.write("CANTIDAD DE VUELOS EN FLIGHTS_UNIDOS:  " + str(len(merged_df)))
bloc_notas.write("\n")

path = "C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros2\\Planes_Vuelo"

all_files = glob.glob(os.path.join(path, "*.csv"))

all_df = []
for f in all_files:
    df = pd.read_csv(f, sep=';')
    df['file'] = f.split('/')[-1]
    all_df.append(df)

merged_df1 = pd.concat(all_df, ignore_index=True, sort=True)
merged_df1 = merged_df1.drop_duplicates(keep='first')

print(merged_df1.head())
merged_df1.to_csv("Planes_Vuelo_Unidos.csv", index=False, sep=";")

bloc_notas.write("CANTIDAD DE VUELOS DE PLANES_VUELO_UNIDOS:  " + str(len(merged_df1)))

bloc_notas.write("\n")

merged_df2 = pandas.read_csv("C:\\Cosas_Cesar\\Proyectos\\Proyecto_Flujos\\Ficheros2\\Flujos\\dimRouteClustered_R1I_R2I_SAN_PAU_CJI_BAS_CCC_2019.csv", delimiter=';')
bloc_notas.write("CANTIDAD DE FLUJOS EN EL FICHERO ORIGINAL:  " + str(len(merged_df2)))
bloc_notas.write("\n")

print(merged_df2.head())

merged_df3 = merged_df.merge(merged_df1, left_on = ['flightkey'],
                right_on= ['flightkey'],
                how = 'inner')

bloc_notas.write("CANTIDAD DE VUELOS AL UNIR DOS ARCHIVOS:  " + str(len(merged_df3)))
bloc_notas.write("\n")

merged_df4 = merged_df3.merge(merged_df2, left_on=['routeKey'],
                              right_on=['routeKey'], how='inner')
print(merged_df4.size)
print(merged_df4.columns)
print(merged_df4.describe())

l = []
flujos = merged_df4['routeKey']
contador = 0
while contador < flujos.size:
    i = flujos[contador]
    if i not in l:
        l.append(i)

    contador += 1

bloc_notas.write("CANTIDAD DE FLUJOS FINAL:  " + str(len(l)))
bloc_notas.write("\n")
bloc_notas.write("CANTIDAD FINAL DE VUELOS FINAL:  " + str(len(merged_df4)))