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
        todos_los_datos_esteriles, todos_los_datos_respiratorios = self.obtener_estadisticas_todos_los_meses()

        df_resultados_esteriles = pd.DataFrame.from_dict(todos_los_datos_esteriles, orient = 'index')
        df_resultados_esteriles = df_resultados_esteriles.transpose()

        df_resultados_respiratorios = pd.DataFrame.from_dict(todos_los_datos_respiratorios, orient = 'index')
        df_resultados_respiratorios = df_resultados_respiratorios.transpose()

        with pd.ExcelWriter('ESTADISTICAS_I_SEMESTRE_2022.xlsx') as f:
            df_resultados_esteriles.to_excel(f, sheet_name = 'MUESTRAS ESTERILES')
            df_resultados_respiratorios.to_excel(f, sheet_name = 'MUESTRAS RESPIRATORIAS')

    def obtener_estadisticas_todos_los_meses(self):
        nombres_sensibilidades_ordenadas = sorted([excel for excel in os.listdir() if 'SENS' in excel], key = lambda x: int(x[0:2]))
        estadisticas_esteriles = {}
        estadisticas_respiratorios = {}

        for nombre in nombres_sensibilidades_ordenadas:
            print(f'Leyendo {nombre}')
            esteriles_estadisticas_mes, respiratorios_estadisticas_mes = self.obtener_estadistica_de_un_mes(nombre)
            estadisticas_esteriles[nombre] = esteriles_estadisticas_mes
            estadisticas_respiratorios[nombre] = respiratorios_estadisticas_mes
        
        return estadisticas_esteriles, estadisticas_respiratorios

    def obtener_estadistica_de_un_mes(self, nombre):
        df = pd.read_excel(nombre, sheet_name = 1, header = 1)
        mask_uci = df['SERVICIO'].map(lambda x: (x == 'UCI'))

        mask_esteriles = df['TIPO MUESTRA'].map(lambda x: (x == 'Líquido Pleural') or (x == 'Sangre (Hemocultivo)') or \
                                                            (x == 'LP') or (x == 'HEMO'))
                                                        
        mask_respiratorios = df['TIPO MUESTRA'].map(lambda x: ('Lavado' in x) or ('LB' in x))

        mask_uci_esteriles = mask_uci & mask_esteriles
        mask_uci_respiratorios = mask_uci & mask_respiratorios

        df_uci_esteriles = df[mask_uci_esteriles]
        df_uci_respiratorios = df[mask_uci_respiratorios]

        estadisticas_esteriles = self.calcular_estadisticas(df_uci_esteriles)
        estadisticas_respiratorios = self.calcular_estadisticas(df_uci_respiratorios)

        return estadisticas_esteriles, estadisticas_respiratorios

    def calcular_estadisticas(self, df_microorganismo):
        nuevo_diccionario = {}
 
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
        
    
        df_entero = df_microorganismo[df_microorganismo['MICROORGANISMO'].map(lambda x: ('Enterococcus' in x) or ('faecalis' in x) or ('faecium' in x) or ('durans' in x) or ('avium' in x) or ('casseliflavus' in x) or ('gallinarum' in x) or ('raffinosus' in x) or ('malodoratus' in x) or ('hirae' in x) or ('mundtii' in x) or ('solitarius' in x) or ('pseudoavium' in x))]
        df_pseudo = df_microorganismo[df_microorganismo['MICROORGANISMO'].map(lambda x: 'aeruginosa' in x)]
        df_klebsi = df_microorganismo[df_microorganismo['MICROORGANISMO'].map(lambda x: 'pneumoniae' in x)]

        nombre_microorganismos = ['Enterococcus', 'Pseudomona aeruginosa', 'Klebsiella pneumoniae']
        lista_microorganismos_a_analizar = [df_entero, df_pseudo, df_klebsi]
        resistencias_a_calcular = [RESISTENCIAS_ENTEROCOCCUS, RESISTENCIAS_PSEUDOMONAS, RESISTENCIAS_KLEBSIELLA]

        nombre_df_farmacos_microorganismos = list(zip(nombre_microorganismos, lista_microorganismos_a_analizar, resistencias_a_calcular))

        for nombre_microorganismo, df, lista_resistencias in nombre_df_farmacos_microorganismos:
            for farmaco in lista_resistencias:
                try:
                    serie_resistencia_farmaco = df.loc[:, farmaco].value_counts()
                    numero_resistenes = serie_resistencia_farmaco['R']
                    microorganismos_totales = serie_resistencia_farmaco.sum()
                    resistencia_farmaco = round((numero_resistenes/ microorganismos_totales) * 100, 1)

                except KeyError:
                    numero_resistenes = 0
                    microorganismos_totales = 0
                    resistencia_farmaco = 0
                
                nuevo_diccionario[f'{nombre_microorganismo} {farmaco} N resistentes'] = numero_resistenes
                nuevo_diccionario[f'{nombre_microorganismo} {farmaco} N totales'] = microorganismos_totales
                nuevo_diccionario[f'{nombre_microorganismo} {farmaco} % '] = resistencia_farmaco
        
        return nuevo_diccionario.copy()

        # print(f'La resistencia a {farmaco} es del: {resistencia_farmaco}%')
            
        



estadisticas = Estadisticas()
resultados = estadisticas.hacer_tabla()
