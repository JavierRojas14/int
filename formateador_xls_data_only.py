from cmath import nan
import pandas as pd
import json
import os
import pdfplumber
import numpy as np
from datetime import datetime
from itertools import zip_longest

with open('DICCIONARIO_CODIGO_NOMBRE_FARMACOS.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_CODIGO_NOMBRE_FARMACOS = json.load(f)

with open ('DICCIONARIO_CIM.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_CIM = json.load(f)

###################################################################################################

COLUMNAS_FARMACOS = list(DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values()) + list(DICCIONARIO_CIM.keys())   
LARGO_COLUMNAS_FARMACOS = len(COLUMNAS_FARMACOS)
COLUMNAS_A_NO_OCUPAR = ['CZA', '?']

#########################################################################################

class Formateador():
    def __init__(self):
        pass

    def hacer_tabla_global(self):
        todas_las_entradas = self.obtener_entradas_todos_los_pacientes()
        columnas = ['Ingreso', 'Tipo muestra', 'Nº de Cultivo', 'Rut', 'Nombre', 'Servicio', 'Comentario', 'Fecha Firma', 'Microorganismo', 'BLEE'] + COLUMNAS_FARMACOS
        df = pd.DataFrame(todas_las_entradas, columns = columnas)
        df.drop(columns = COLUMNAS_A_NO_OCUPAR, inplace = True)

        return df

    def obtener_entradas_todos_los_pacientes(self):
        entradas_todos_los_pacientes = []

        for nombre_archivo in os.listdir():
            if nombre_archivo[-4:len(nombre_archivo)] == '.xls':
                nombre_archivo_sin_extension = nombre_archivo[:-4]
                tipo_archivo = nombre_archivo_sin_extension.split('_')[-1]
                entradas_de_un_paciente = self.obtener_entradas_de_un_paciente(nombre_archivo, tipo_archivo)
                for entrada_de_un_paciente in entradas_de_un_paciente:
                    entradas_todos_los_pacientes.append(entrada_de_un_paciente)

        return entradas_todos_los_pacientes

    def obtener_entradas_de_un_paciente(self, nombre_archivo, tipo_archivo):
        datos_persona = self.obtener_datos_demograficos_de_un_paciente(nombre_archivo, tipo_archivo)
        lista_microorganismos_persona = self.obtener_microorganismos_de_un_paciente(nombre_archivo, tipo_archivo)
        numero_microorganismos = len(lista_microorganismos_persona)

        lista_antibiogramas_persona = self.obtener_antibiogramas_de_un_paciente(nombre_archivo, tipo_archivo, numero_microorganismos)
        entradas_de_un_paciente_formato_lista = self.formatear_todos_los_datos_un_paciente(datos_persona, lista_microorganismos_persona, lista_antibiogramas_persona)

        for entrada in entradas_de_un_paciente_formato_lista:
            print(f'Entrada de {nombre_archivo}, largo {len(entrada)} ')

        return entradas_de_un_paciente_formato_lista
    
    def formatear_todos_los_datos_un_paciente(self, datos_persona, lista_microorganismos_persona, lista_antibiogramas_persona):
        entradas = []
        diccionario_numeracion_cepas = {0: ' I', 1: ' II', 2: ' III', 3: ' IV'}
        for i in range(len(lista_microorganismos_persona)):
            micro = lista_microorganismos_persona[i]
            antibio = lista_antibiogramas_persona[i]
            if len(lista_microorganismos_persona) > 1:
                datos_persona_romanos = datos_persona.copy()
                nuevo_numero_cultivo = f'{datos_persona_romanos[2]}{diccionario_numeracion_cepas[i]}'
                datos_persona_romanos[2] = nuevo_numero_cultivo

                entrada_paciente = datos_persona_romanos + micro + antibio
            
            else:
                entrada_paciente = datos_persona + micro + antibio

            
            entradas.append(entrada_paciente)

        return entradas
    
    def obtener_datos_demograficos_de_un_paciente(self, nombre_archivo, tipo_archivo):
        tabla_cruda = pd.read_excel(nombre_archivo)
        nombre_archivo = nombre_archivo[:-4] + '.pdf'

        with pdfplumber.open(nombre_archivo) as pdf:
            datos_personales_relevantes = pdf.pages[0].extract_text().split('\n')[3:12]

            nombre_paciente = datos_personales_relevantes[0].split(':')[1][:-10]
            n_orden = datos_personales_relevantes[0].split(':')[-1]
            rut = datos_personales_relevantes[1].split(':')[-1]

            linea_ingreso = datos_personales_relevantes[4].split(' ')
            try:
                fecha_ingreso = datetime.strptime(f'{linea_ingreso[-2]} {linea_ingreso[-1]}', ':%d-%m-%Y %H:%M:%S')
            except ValueError:
                fecha_ingreso = datetime.strptime(f'{linea_ingreso[-2]} {linea_ingreso[-1]}', ':%d/%m/%Y %H:%M:%S')


            linea_firma = datos_personales_relevantes[5].split(' ')
            try:
                fecha_firma = datetime.strptime(f'{linea_firma[-2]} {linea_firma[-1]}', ':%d-%m-%Y %H:%M:%S')
            except ValueError:
                fecha_firma = datetime.strptime(f'{linea_firma[-2]} {linea_firma[-1]}', ':%d/%m/%Y %H:%M:%S')

            seccion = datos_personales_relevantes[5].split(':')[1][:-13]
            tipo_muestra = datos_personales_relevantes[7].split(':')[-1]
            n_cultivo = datos_personales_relevantes[8].split(':', 1)[-1]
        
        if tipo_archivo == 'HONGOS':
            n_cultivo = tabla_cruda[tabla_cruda.iloc[:, 0] == 'Nº CULTIVO'].iloc[0, 4]
        
        comentario = None
        for filas in list(tabla_cruda.iloc[:, 0]):
            if type(filas) == str:
                if 'Avisado' in filas:
                    comentario = 'ALERTA'
                    print(f'El paciente {nombre_archivo} tiene una alerta!')

        return [fecha_ingreso, tipo_muestra, n_cultivo, rut, nombre_paciente, seccion, comentario, fecha_firma]

    def obtener_microorganismos_de_un_paciente(self, nombre_archivo, tipo_archivo):
        datos_totales = pd.read_excel(nombre_archivo)
        microorganismos = []
        # Si es un archivo de hongos
        if tipo_archivo == 'HONGOS':
            datos_hongos = datos_totales[datos_totales.iloc[:, 0] == 'CULTIVO DE HONGOS']
            for hongo in datos_hongos.iloc[:, 3][0].split(','):
                microorganismos.append(hongo)
        
        elif tipo_archivo == 'POLI':
            microorganismos.append('POLIMICROBIANO')
        
        elif tipo_archivo == 'NOANTI':
            datos_hemo = datos_totales[(datos_totales.iloc[:, 0] == 'HEMOCULTIVO AEROBICO') | (datos_totales.iloc[:, 0] == 'HEMOCULTIVO ANAEROBICO')]
            microorganismo_contaminante = list(datos_hemo.iloc[:, 2])[0].split(' ')
            microorganismo_contaminante = ' '.join(microorganismo_contaminante[2:])
            microorganismos.append(microorganismo_contaminante)
        
        else:
            datos_cepas = datos_totales[(datos_totales.iloc[:, 0] == 'Cepa')]
            for microorganismo in datos_cepas.iloc[:, 2]:
                microorganismos.append(microorganismo)
        
        microorganismos = list(map(lambda microorg: [microorg, '(+)'] if ('BLEE' in microorg) else [microorg, None], microorganismos))
        return microorganismos

    def obtener_antibiogramas_de_un_paciente(self, nombre_archivo, tipo_archivo, numero_microorganismos):
        datos_totales = pd.read_excel(nombre_archivo)
        lista_sin_antibiograma = [None for i in range(LARGO_COLUMNAS_FARMACOS)]
        antibiogramas = []

        if tipo_archivo == 'HONGOS' or tipo_archivo == 'POLI' or tipo_archivo == 'NOANTI':
            for i in range(numero_microorganismos):
                antibiogramas.append(lista_sin_antibiograma)
        
        else:
            indice_fila_inicio_antibio, indice_fila_termino_antibio = self.identificar_localizacion_antibiograma(datos_totales)
            columnas_sobre_antibiograma = list(datos_totales.iloc[indice_fila_inicio_antibio - 1].dropna())
            numero_cepas = []
            for columna in columnas_sobre_antibiograma:
                if type(columna) == str:
                    if columna.isnumeric():
                        numero_cepas.append(columna)
                
                elif type(columna) == np.float64:
                    numero_cepas.append(int(columna))
            
            cantidad_columnas_de_cepas = len(numero_cepas)
            indice_columnas_a_tomar = (cantidad_columnas_de_cepas * 2) + 1
            antibiograma_crudo = datos_totales.iloc[indice_fila_inicio_antibio: indice_fila_termino_antibio, :indice_columnas_a_tomar]

            if not(antibiograma_crudo.empty):
                antibiograma_formateado = self.formatear_tabla_antibiograma(antibiograma_crudo)
                lista_cepas_formato_df = self.separar_cepas(antibiograma_formateado)
                antibiogramas = list(map(self.mappear_resultados_a_formato_excel, lista_cepas_formato_df))
            
            else:
                print('Hay un antibiograma vacio!')
                for i in range(numero_microorganismos):
                    antibiogramas.append(lista_sin_antibiograma)
            
        return antibiogramas



    def identificar_localizacion_antibiograma(self, datos_totales):
        se_encontro_antibiograma = False
        columna_a_iterar = datos_totales.iloc[:, 0].fillna('-')
        for identificadores in enumerate(columna_a_iterar):
            if 'ANTIBIOGRAMA' in identificadores:
                indice_inicial = identificadores[0]
                se_encontro_antibiograma = True

            if (identificadores[1] == '-') and (se_encontro_antibiograma):
                indice_final = identificadores[0]

        return indice_inicial + 1, indice_final - 2


    def formatear_tabla_antibiograma(self, antibiograma_crudo):
        antibiograma_formateado = antibiograma_crudo.copy()

        headers = ['ANTIBIOTICO']
        self.cantidad_de_cepas = int((len(antibiograma_formateado.columns) - 1)/ 2)
        for i in range(self.cantidad_de_cepas):
            headers.append(f'Cepa')
            headers.append(f'CIM')

        antibiograma_formateado.columns = headers
        antibiograma_formateado.ANTIBIOTICO = antibiograma_formateado.ANTIBIOTICO.map(DICCIONARIO_CODIGO_NOMBRE_FARMACOS)
        antibiograma_formateado.set_index(antibiograma_formateado.ANTIBIOTICO, inplace = True)
        antibiograma_formateado.drop(columns = 'ANTIBIOTICO', inplace = True)

        return antibiograma_formateado
    
    def separar_cepas(self, antibiograma_formateado):
        tablas_cepas = []
        for i in range(self.cantidad_de_cepas):
            df = antibiograma_formateado.iloc[:, i * 2: (i * 2) + 2]
            df = df[df['Cepa'].notna()]
            tablas_cepas.append(df)
        
        return tablas_cepas
    
    def mappear_resultados_a_formato_excel(self, tabla_una_cepa):
        cambiador_nomenclatura_sensibilidades = {'Sensible': 'S', 'Resistente': 'R', 'Intermedio': 'I'}
        diccionario_sensibilidades_a_llenar = {farmaco: None for farmaco in DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values()}
        for farmaco in tabla_una_cepa.index:
            resultado_sensibilidad = tabla_una_cepa['Cepa'][farmaco]
            diccionario_sensibilidades_a_llenar[farmaco] = cambiador_nomenclatura_sensibilidades[resultado_sensibilidad]

        diccionario_cim_a_llenar = {farmaco: None for farmaco in DICCIONARIO_CIM.keys()}
        for farmaco in tabla_una_cepa.index:
            if farmaco == 'PEN' or farmaco == 'VAN':
                resultado_cim = tabla_una_cepa['CIM'][farmaco]
                diccionario_cim_a_llenar[f'CIM {farmaco}'] = resultado_cim
        
        lista_sensibilidades_llenas = list(diccionario_sensibilidades_a_llenar.values()) + list(diccionario_cim_a_llenar.values())
        return lista_sensibilidades_llenas 


formateador = Formateador()
lista = formateador.hacer_tabla_global()

fecha = os.getcwd().split('\\')[-2]
tipo = os.getcwd().split('\\')[-1]
nombre_archivo = f'{fecha}_DATOS_{tipo}.xlsx'

lista.to_excel(nombre_archivo, index = False)