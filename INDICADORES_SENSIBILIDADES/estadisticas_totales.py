import pandas as pd
import json
import warnings
import os

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')


with open('RESISTENCIAS_PSEUDOMONAS.json', 'r') as f:
    RESISTENCIAS_PSEUDOMONAS = json.load(f)

with open('RESISTENCIAS_ENTEROCOCCUS.json', 'r') as f:
    RESISTENCIAS_ENTEROCOCCUS = json.load(f)


class Estadisticas:
    def __init__(self):
        pass

    def obtener_estadisticas_todos_los_meses(self):
        nombres_sensibilidades_ordenadas = sorted([excel for excel in os.listdir() if 'SENS' in excel], key = lambda x: int(x[0:2]))
        estadisticas = {}
        

        for nombre in nombres_sensibilidades_ordenadas:
            print(f'Leyendo {nombre}')
            estadisticas[nombre] = self.obtener_estadistica_de_un_mes(nombre)
        
        return estadisticas

    def obtener_estadistica_de_un_mes(self, nombre):
        df = pd.read_excel(nombre, sheet_name = 1, header = 1)
        df_aureus_esteriles_uci = self.obtener_aureus_metilcilino_esteriles_uci(df)
        df_enterococcus = df[df['MICROORGANISMO'].map(lambda x: 'Enterococcus' in x)]
        df_pseudomona = df[df['MICROORGANISMO'].map(lambda x: 'aeruginosa' in x)]

        numero_aureus = df_aureus_esteriles_uci.shape[0]
        resistencias_entero = self.calcular_resistencias(df_enterococcus, RESISTENCIAS_ENTEROCOCCUS)
        resistencias_pseudomona = self.calcular_resistencias(df_pseudomona, RESISTENCIAS_PSEUDOMONAS)

        return {'Cantidad de aureus metilcilino resistentes:': numero_aureus,
                'Resistencias enterobacterias': resistencias_entero.copy(),
                'Resistencias pseudomonas':  resistencias_pseudomona.copy()}

    def obtener_aureus_metilcilino_esteriles_uci(self, df):
        mask_aureus_metilcilino = df['MICROORGANISMO'].map(lambda x: 'etilcilino' in x)
        mask_muestras_esteriles = df['TIPO MUESTRA'].map(lambda x: (x == 'Líquido Pleural') or (x == 'Sangre (Hemocultivo)') or ('Lavado' in x) or ('Aspirado' in x))
        mask_uci = df['SERVICIO'].map(lambda x: (x == 'UCI'))

        mask_total = mask_aureus_metilcilino & mask_muestras_esteriles & mask_uci
        df_aureus_esteriles_uci = df[mask_total]

        return df_aureus_esteriles_uci

    def calcular_resistencias(self, df_microorganismo, resistencias_a_calcular):
        for farmaco in resistencias_a_calcular.keys():
            datos_resistencia_farmaco = df_microorganismo.loc[:, farmaco].value_counts()
            try:
                resistencia_farmaco = round((datos_resistencia_farmaco['R'] / datos_resistencia_farmaco.sum()) * 100, 1)
            except KeyError:
                resistencia_farmaco = 0

            resistencias_a_calcular[farmaco] = resistencia_farmaco
            # print(f'La resistencia a {farmaco} es del: {resistencia_farmaco}%')
        
        return resistencias_a_calcular


estadisticas = Estadisticas()
resultados = estadisticas.obtener_estadisticas_todos_los_meses()

with open('Resultados.json', 'w') as f:
    json.dump(resultados, f, indent = 4)
