import pandas as pd
import json
import warnings
import os
from collections import OrderedDict

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')


with open('RESISTENCIAS_PSEUDOMONAS.json', 'r') as f:
    RESISTENCIAS_PSEUDOMONAS = json.load(f)

with open('RESISTENCIAS_ENTEROCOCCUS.json', 'r') as f:
    RESISTENCIAS_ENTEROCOCCUS = json.load(f)

with open('RESISTENCIAS_KLEBSIELLA.json', 'r') as f:
    RESISTENCIAS_KLEBSIELLA = json.load(f)


class Estadisticas:
    def __init__(self):
        pass

    def hacer_tabla(self):
        todos_los_datos = self.obtener_estadisticas_todos_los_meses()
        index = todos_los_datos['1 SENS_ ENERO 22.xlsx'].keys()

        df_resultados = pd.DataFrame.from_dict(todos_los_datos, orient = 'index')
        df_resultados = df_resultados.transpose()
        df_resultados.to_excel('ESTADISTICAS_I_SEMESTRE_2022.xlsx')

    def obtener_estadisticas_todos_los_meses(self):
        nombres_sensibilidades_ordenadas = sorted([excel for excel in os.listdir() if 'SENS' in excel], key = lambda x: int(x[0:2]))
        estadisticas = {}

        for nombre in nombres_sensibilidades_ordenadas:
            print(f'Leyendo {nombre}')
            estadisticas[nombre] = self.obtener_estadistica_de_un_mes(nombre)
        
        return estadisticas

    def obtener_estadistica_de_un_mes(self, nombre):
        df = pd.read_excel(nombre, sheet_name = 1, header = 1)
        mask_uci = df['SERVICIO'].map(lambda x: (x == 'UCI'))
        mask_esteriles = df['TIPO MUESTRA'].map(lambda x: (x == 'Líquido Pleural') or (x == 'Sangre (Hemocultivo)') or \
                                                          (x == 'LP') or (x == 'HEMO'))

        mask_uci_esteriles = mask_uci & mask_esteriles
        df_uci_esteriles = df[mask_uci_esteriles]

        estadisticas_aureus = self.calcular_estadisticas(df_uci_esteriles, 'Aureus')
        estadisticas_enterococcus = self.calcular_estadisticas(df_uci_esteriles, 'Enterococcus')
        estadisticas_pseudomona = self.calcular_estadisticas(df_uci_esteriles, 'Pseudomonas aeruginosa')
        estadisticas_klebsiella = self.calcular_estadisticas(df_uci_esteriles, 'Klebsiella pneumoniae')

        diccionario_resultado = {**estadisticas_aureus, **estadisticas_enterococcus, **estadisticas_pseudomona, **estadisticas_klebsiella}
        orden_llaves = diccionario_resultado.keys()
        lista_tuplas = [(key, diccionario_resultado[key]) for key in orden_llaves]
        diccionario_ordenado = OrderedDict(lista_tuplas)

        return diccionario_ordenado

    def calcular_estadisticas(self, df_microorganismo, nombre_microorganismo):
        nuevo_diccionario = {}
        if nombre_microorganismo == 'Aureus':
            mask_aureus_metilcilino = df_microorganismo['MICROORGANISMO'].map(lambda x: ('eticilino' in x) or ('etilcilino' in x))
            mask_aureus_totales = df_microorganismo['MICROORGANISMO'].map(lambda x: ('aureus' in x))

            df_aureus_metilcilino = df_microorganismo[mask_aureus_metilcilino]
            df_aureus_totales = df_microorganismo[mask_aureus_totales]

            n_aureus_metilcilino = df_aureus_metilcilino.shape[0]
            n_aureus_totales = df_aureus_totales.shape[0]

            if n_aureus_totales > 0:
                porcentaje_aureus = round((n_aureus_metilcilino/ n_aureus_totales) * 100, 1)
            
            else:
                porcentaje_aureus = 0

            nuevo_diccionario[f'N aureus metilcilino resistentes'] = n_aureus_metilcilino
            nuevo_diccionario[f'N aureus totales'] = n_aureus_totales
            nuevo_diccionario[f'% Aureus metilcilino resistentes'] = porcentaje_aureus
        
        else:
            if nombre_microorganismo == 'Enterococcus':
                df_microorganismo = df_microorganismo[df_microorganismo['MICROORGANISMO'].map(lambda x: ('Enterococcus' in x) or ('faecalis' in x) or ('faecium' in x) or ('durans' in x) or ('avium' in x) or ('casseliflavus' in x) or ('gallinarum' in x) or ('raffinosus' in x) or ('malodoratus' in x) or ('hirae' in x) or ('mundtii' in x) or ('solitarius' in x) or ('pseudoavium' in x))]
                resistencias_a_calcular = RESISTENCIAS_ENTEROCOCCUS
            
            elif nombre_microorganismo == 'Pseudomonas aeruginosa':
                df_microorganismo = df_microorganismo[df_microorganismo['MICROORGANISMO'].map(lambda x: 'aeruginosa' in x)]
                resistencias_a_calcular = RESISTENCIAS_PSEUDOMONAS
            
            elif nombre_microorganismo == 'Klebsiella pneumoniae':
                df_microorganismo = df_microorganismo[df_microorganismo['MICROORGANISMO'].map(lambda x: 'pneumoniae' in x)]
                resistencias_a_calcular = RESISTENCIAS_KLEBSIELLA
        
            for farmaco in resistencias_a_calcular.keys():
                datos_resistencia_farmaco = df_microorganismo.loc[:, farmaco].value_counts()
                try:
                    numero_resistenes = datos_resistencia_farmaco['R']
                    microorganismos_totales = datos_resistencia_farmaco.sum()
                    resistencia_farmaco = round((numero_resistenes/ microorganismos_totales) * 100, 1)
                except KeyError:
                    numero_resistenes = 0
                    microorganismos_totales = 0
                    resistencia_farmaco = 0

                nuevo_diccionario[f'N {nombre_microorganismo} {farmaco} resistentes'] = numero_resistenes
                nuevo_diccionario[f'N {nombre_microorganismo} {farmaco} totales'] = microorganismos_totales
                nuevo_diccionario[f'% {nombre_microorganismo} {farmaco}'] = resistencia_farmaco

                # print(f'La resistencia a {farmaco} es del: {resistencia_farmaco}%')
            
        return nuevo_diccionario.copy()



estadisticas = Estadisticas()
resultados = estadisticas.hacer_tabla()
