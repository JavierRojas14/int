import pandas as pd
import json
import warnings
import os
import numpy as np

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

with open('RESISTENCIAS_PSEUDOMONAS.json', 'r', encoding = 'utf-8') as f:
    RESISTENCIAS_PSEUDOMONAS = json.load(f)

with open('RESISTENCIAS_ENTEROCOCCUS.json', 'r', encoding = 'utf-8') as f:
    RESISTENCIAS_ENTEROCOCCUS = json.load(f)

with open('RESISTENCIAS_KLEBSIELLA.json', 'r', encoding = 'utf-8') as f:
    RESISTENCIAS_KLEBSIELLA = json.load(f)

with open('LIMPIADOR_TOTAL.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_LIMPIADOR_NOMENCLATURAS = json.load(f)

    LIMPIADOR_EVE = DICCIONARIO_LIMPIADOR_NOMENCLATURAS['NOMENCLATURA EVE']
    LIMPIADOR_REDUNDANTES = DICCIONARIO_LIMPIADOR_NOMENCLATURAS['REDUNDANTES']

    LIMPIADOR_GLOBAL = LIMPIADOR_EVE | LIMPIADOR_REDUNDANTES

class Estadisticas:
    def __init__(self):
        pass

    def obtener_estadisticas_todos_los_meses(self, output):
        nombres_sensibilidades_ordenadas = sorted([excel for excel in os.listdir() if 'Fibrosis' in excel])
        estadisticas_acumuladas = {}
        dfs_a_guardar = []

        for nombre_archivo in nombres_sensibilidades_ordenadas:
            print(f'Leyendo {nombre_archivo}')

            estadistica_fq_archivo = self.obtener_estadistica_por_archivo(nombre_archivo)
            estadisticas_acumuladas[nombre_archivo] = estadistica_fq_archivo
            df_fq_archivo = self.hacer_tabla(estadistica_fq_archivo)
            dfs_a_guardar.append((nombre_archivo, df_fq_archivo))


        df_estadisticas_acumuladas = self.hacer_tabla(estadisticas_acumuladas).transpose()
        dfs_a_guardar.append(('ESTADISTICAS GLOBALES FQ', df_estadisticas_acumuladas))
        
        with pd.ExcelWriter(output) as f:
            for nombre, df in dfs_a_guardar:
                df.to_excel(f, sheet_name = nombre)
        

    def hacer_tabla(self, diccionario_estadisticas):
        estadisticas_fq = pd.DataFrame.from_dict(diccionario_estadisticas, orient = 'index')
        # estadisticas_fq = estadisticas_fq.transpose()

        return estadisticas_fq

    def obtener_estadistica_por_archivo(self, nombre_archivo):
        df = pd.read_excel(nombre_archivo, header = 1).dropna(how = 'all')
        df = df.fillna('-')
        df_limpia = df.copy()
        df_limpia['MICROORGANISMO'] = df_limpia['MICROORGANISMO'].map(lambda x: LIMPIADOR_GLOBAL[x] if (LIMPIADOR_GLOBAL[x] != None) else x) 

        estadisticas_fq = self.calcular_estadisticas(df_limpia)

        return estadisticas_fq

    def calcular_estadisticas(self, df_fq):
        estadisticas = {}

        frecuencias_microorganismos = df_fq['MICROORGANISMO'].value_counts()

        numero_resistentes_TOB = 0
        for resultado_sensibilidad in df_fq.loc[:, 'TOB']:
            if resultado_sensibilidad == 'R':
                numero_resistentes_TOB += 1
        
        porcentaje_resistenes_TOB = round((numero_resistentes_TOB / df_fq.shape[0]) * 100, 1)
        
        estadisticas['Total Pacientes FQ'] = df_fq.shape[0]
        estadisticas['TOB N resistentes'] = numero_resistentes_TOB
        estadisticas['TOB % resistentes'] = porcentaje_resistenes_TOB

        estadisticas.update(frecuencias_microorganismos)

        return estadisticas.copy()

estadisticas = Estadisticas()
resultados = estadisticas.obtener_estadisticas_todos_los_meses('ESTADISTICAS_FQ.xlsx')