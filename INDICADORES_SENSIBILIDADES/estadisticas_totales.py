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
        df_enterococcus = df[df['MICROORGANISMO'].map(lambda x: ('Enterococcus' in x) or ('faecalis' in x) or ('faecium' in x) or ('durans' in x) or ('avium' in x) or ('casseliflavus' in x) or ('gallinarum' in x) or ('raffinosus' in x) or ('malodoratus' in x) or ('hirae' in x) or ('mundtii' in x) or ('solitarius' in x) or ('pseudoavium' in x))]
        df_pseudomona = df[df['MICROORGANISMO'].map(lambda x: 'aeruginosa' in x)]

        numero_aureus = df_aureus_esteriles_uci.shape[0]
        resistencias_entero = self.calcular_resistencias(df_enterococcus, RESISTENCIAS_ENTEROCOCCUS, 'Enterococcus')
        resistencias_pseudomona = self.calcular_resistencias(df_pseudomona, RESISTENCIAS_PSEUDOMONAS, 'Pseudomonas')

        return {'Cantidad de aureus metilcilino resistentes:': numero_aureus,
                'Resistencias enterobacterias': resistencias_entero.copy(),
                'Resistencias pseudomonas':  resistencias_pseudomona.copy()}

    def obtener_aureus_metilcilino_esteriles_uci(self, df):
        mask_aureus_metilcilino = df['MICROORGANISMO'].map(lambda x: ('eticilino' in x) or ('etilcilino' in x))
        mask_muestras_esteriles = df['TIPO MUESTRA'].map(lambda x: (x == 'Líquido Pleural') or (x == 'Sangre (Hemocultivo)') or ('Lavado' in x) or ('Aspirado' in x) or \
                                                                   (x == 'LP') or (x == 'HEMO') or ('LB' in x) or ('ASP' in x))
        mask_uci = df['SERVICIO'].map(lambda x: (x == 'UCI'))

        mask_total = mask_aureus_metilcilino & mask_muestras_esteriles & mask_uci
        df_aureus_esteriles_uci = df[mask_total]

        return df_aureus_esteriles_uci

    def calcular_resistencias(self, df_microorganismo, resistencias_a_calcular, nombre_microorganismo):
        nuevo_diccionario = {}
        for farmaco in resistencias_a_calcular.keys():
            datos_resistencia_farmaco = df_microorganismo.loc[:, farmaco].value_counts()
            try:
                resistencia_farmaco = round((datos_resistencia_farmaco['R'] / datos_resistencia_farmaco.sum()) * 100, 1)
            except KeyError:
                resistencia_farmaco = 0
            
            nombre_llave = f'{nombre_microorganismo} {farmaco}'
            nuevo_diccionario[nombre_llave] = resistencia_farmaco
            # print(f'La resistencia a {farmaco} es del: {resistencia_farmaco}%')
        
        return nuevo_diccionario.copy()



estadisticas = Estadisticas()
resultados = estadisticas.obtener_estadisticas_todos_los_meses()
df_resultados = pd.DataFrame(resultados).transpose()
df_excel = pd.concat([df_resultados['Cantidad de aureus metilcilino resistentes:'], 
                      df_resultados['Resistencias enterobacterias'].apply(pd.Series),
                      df_resultados['Resistencias pseudomonas'].apply(pd.Series)], axis = 1)


df_excel.to_excel('ESTADISTICAS_I_SEMESTRE_2022.xlsx')
