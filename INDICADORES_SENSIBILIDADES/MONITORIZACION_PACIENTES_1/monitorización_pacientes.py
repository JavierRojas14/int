import pandas as pd
import os
import json
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

with open('LIMPIADOR_TOTAL.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_LIMPIADOR_NOMENCLATURAS = json.load(f)

    LIMPIADOR_EVE = DICCIONARIO_LIMPIADOR_NOMENCLATURAS['NOMENCLATURA EVE']
    LIMPIADOR_REDUNDANTES = DICCIONARIO_LIMPIADOR_NOMENCLATURAS['REDUNDANTES']

    LIMPIADOR_GLOBAL = LIMPIADOR_EVE | LIMPIADOR_REDUNDANTES

with open('DICCIONARIO_CODIGO_NOMBRE_FARMACOS.json', 'r') as f:
    DICCIONARIO_FARMACOS_A_MONITORIZAR = json.load(f)
    FARMACOS_A_MONITORIZAR = list(DICCIONARIO_FARMACOS_A_MONITORIZAR.values())[: -3]

class Monitorizador:
    def __init__(self):
        pass

    def agrupar_sub_tablas_en_una_grande(self):
        nombres_sensibilidades_ordenadas = sorted([excel for excel in os.listdir() if 'Fibrosis' in excel])
        dfs_a_guardar = []


        for nombre in nombres_sensibilidades_ordenadas:
            df = pd.read_excel(nombre, header = 1).dropna(how = 'all')
            df = df.fillna('-')
            df_limpia = df.copy()
            df_limpia['MICROORGANISMO'] = df_limpia['MICROORGANISMO'].map(lambda x: LIMPIADOR_GLOBAL[x] if (LIMPIADOR_GLOBAL[x] != None) else x)

            dfs_a_guardar.append(df_limpia)

        df_global = pd.concat(dfs_a_guardar)

        return df_global
    
    def leer_y_formatear_tabla_FQ(self, archivo):
        df_global = pd.read_excel(archivo)
        cambiar_rut = {'13218653-7': '13.218.653-7',
                    '15102568-4': '15.102.568-4',
                    '17014710-3': '17.014.710-3',
                    '17564424-5': '17.564.424-5',
                    '17.564.424-': '17.564.424-5',
                    '17837944-5': '17.837.944-5',
                    ' 17.014.710-3': '17.014.710-3',
                    'EXP': '19.485.701-2'}

        df_global = df_global.replace(cambiar_rut)
        df_global = df_global.replace({'-': None,
                                    'S': 1,
                                    's': 1,
                                    'I': 2,
                                    'R': 3,
                                    'R ': 3})
        
        return df_global
    
    def monitorizar_pacientes(self, archivo):
        df_global = self.leer_y_formatear_tabla_FQ(archivo)
        for rut in df_global['RUT'].unique():
            df_paciente = df_global[df_global['RUT'] == rut]
            os.mkdir(f'{rut}')
            os.chdir(f'{rut}')

            df_paciente.to_excel(f'{rut}.xlsx')

            wide_form = pd.concat([df_paciente.loc[:, ['FECHA INFORME', 'MICROORGANISMO']], df_paciente.loc[:, FARMACOS_A_MONITORIZAR]], axis = 1)

            for microorganismo in wide_form['MICROORGANISMO'].unique():
                    datos_microorganismo = wide_form[wide_form['MICROORGANISMO'] == microorganismo]
                    datos_microorganismo = datos_microorganismo.dropna(how = 'all', axis = 1)
                    farmacos_medidos = datos_microorganismo.iloc[:, 2:].columns

                    if len(farmacos_medidos) > 0:
                            fig, axis = plt.subplots(len(farmacos_medidos), 1, figsize = (12, 30))

                            for i in range(len(farmacos_medidos)):
                                    sns.scatterplot(data = datos_microorganismo, x = 'FECHA INFORME', y = farmacos_medidos[i], ax = axis[i])
                                    sns.lineplot(data = datos_microorganismo, x = 'FECHA INFORME', y = farmacos_medidos[i], ax = axis[i])
                                    axis[i].set_yticks([1, 2, 3])
                                    axis[i].set_yticklabels(['S', 'I', 'R'])
                            
                            

                            fig.suptitle(f'Monitorización {microorganismo} \n RUT: {rut}', fontsize = 16)
                            fig.savefig(f'{rut} {microorganismo}.png', bbox_inches = 'tight')
                            plt.close(fig)
            
            os.chdir('..')

monitorizador = Monitorizador()
monitorizador.monitorizar_pacientes('FQ_AGRUPADO.xlsx')
