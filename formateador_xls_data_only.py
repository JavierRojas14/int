import pandas as pd
import json
import os
import pdfplumber
import numpy as np
from datetime import datetime

with open('DICCIONARIO_CODIGO_NOMBRE_FARMACOS.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_CODIGO_NOMBRE_FARMACOS = json.load(f)

with open ('DICCIONARIO_CIM.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_CIM = json.load(f)

class Formateador():
    def __init__(self):
        pass

    def hacer_tabla_global(self):
        todas_las_entradas = self.obtener_entradas_todos_los_pacientes()
        columnas = ['Ingreso', 'Tipo muestra', 'Nº de Cultivo', 'Rut', 'Nombre', 'Servicio', 'Fecha Firma', 'Microorganismo', 'BLEE'] + \
                   list(DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values())[:35] + \
                   list(DICCIONARIO_CIM.keys())        

        df = pd.DataFrame(todas_las_entradas, columns = columnas)
        df.drop(columns = ['CZA'], inplace = True)
        return df

    def obtener_entradas_todos_los_pacientes(self):
        entradas_todos_los_pacientes = []

        for nombre_archivo in os.listdir():
            if nombre_archivo[-4:len(nombre_archivo)] == '.xls':
                entradas_de_un_paciente = self.obtener_entradas_de_un_paciente(nombre_archivo)
                for entrada_de_un_paciente in entradas_de_un_paciente:
                    entradas_todos_los_pacientes.append(entrada_de_un_paciente)

        return entradas_todos_los_pacientes

    def obtener_entradas_de_un_paciente(self, nombre_archivo):
        entradas = []

        datos_persona = self.obtener_datos_demograficos_de_un_paciente(nombre_archivo)
        lista_microorganismos_persona = self.obtener_microorganismos_de_un_paciente(nombre_archivo)

        if 'HONGOS' in nombre_archivo:
            datos_totales_hongos = pd.read_excel(nombre_archivo)
            n_cultivo = datos_totales_hongos[datos_totales_hongos.iloc[:, 0] == 'Nº CULTIVO'].iloc[0, 4]
            datos_persona[2] = n_cultivo
            for microorganismo in lista_microorganismos_persona:
                entrada_hongos = datos_persona + microorganismo + [None for i in range(43)]
                entradas.append(entrada_hongos)
        
        elif 'POLI' in nombre_archivo:
            entrada_poli = datos_persona + ['Polimicrobiano'] + [None for i in range(43)]
            entradas.append(entrada_poli)
        
        else:
            lista_antibiogramas_persona = self.obtener_antibiogramas_de_un_paciente(nombre_archivo)

            diccionario_numeracion_cepas = {0: ' I', 1: ' II', 2: ' III', 3: ' IV'}
            for i in range(len(lista_antibiogramas_persona)):
                microorganismo = lista_microorganismos_persona[i]
                antibiograma = lista_antibiogramas_persona[i]

                if len(lista_antibiogramas_persona) > 1:
                    datos_persona_romanos = datos_persona.copy()
                    nuevo_numero_cultivo = f'{datos_persona_romanos[2]}{diccionario_numeracion_cepas[i]}'
                    datos_persona_romanos[2] = nuevo_numero_cultivo
                    entrada_antibiograma = datos_persona_romanos + microorganismo + antibiograma
                
                else:
                    entrada_antibiograma = datos_persona + microorganismo + antibiograma

                entradas.append(entrada_antibiograma)
        
        for i in entradas:
            print(f'Entrada de {nombre_archivo}, largo {len(i)} ')

        return entradas

    
    def obtener_antibiogramas_de_un_paciente(self, nombre_archivo):
        datos_totales = pd.read_excel(nombre_archivo)
        
        indice_fila_inicio_antibio, indice_fila_termino_antibio = self.identificar_localizacion_antibiograma(datos_totales)
        antibiograma_crudo = datos_totales.iloc[indice_fila_inicio_antibio: indice_fila_termino_antibio]
        antibiograma_crudo = antibiograma_crudo.dropna(axis = 1, how = 'all')
        if not(antibiograma_crudo.empty):
            # Si hay un número par de columnas (o sea, que una de las CIM estaba vacia)
            if antibiograma_crudo.shape[1] % 2 == 0:
                antibiograma_crudo['CIM'] = None

            antibiograma_formateado = self.formatear_tabla_antibiograma(antibiograma_crudo)
            lista_cepas_formato_df = self.separar_cepas(antibiograma_formateado)
            lista_cepas_formato_listas = list(map(self.mappear_resultados_a_formato_excel, lista_cepas_formato_df))
        
        else:
            lista_cepas_formato_listas = [[None for i in range(42)]]

        return lista_cepas_formato_listas


    def identificar_localizacion_antibiograma(self, datos_totales):
        se_encontro_antibiograma = False
        columna_a_iterar = datos_totales.iloc[:, 0].fillna('-')
        for identificadores in enumerate(columna_a_iterar):
            if 'ANTIBIOGRAMA' in identificadores:
                indice_inicial = identificadores[0]
                se_encontro_antibiograma = True

            if (identificadores[1] == '-') and (se_encontro_antibiograma):
                indice_final = identificadores[0]

        return indice_inicial + 1, indice_final


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

    def obtener_microorganismos_de_un_paciente(self, nombre_archivo):
        datos_totales = pd.read_excel(nombre_archivo)
        # Si es un archivo de hongos
        if 'HONGOS' in nombre_archivo:
            datos_hongos = datos_totales[datos_totales.iloc[:, 0] == 'CULTIVO DE HONGOS']
            microorganismos = []
            # Al parecer todos los hongos están en 1 casilla. 
            # Por lo tanto:
            for hongo in datos_hongos.iloc[:, 3][0].split(','):
                if 'BLEE' in hongo:
                    microorganismos.append([hongo, '(+)'])
                
                else:
                    microorganismos.append([hongo, None])

        
        # Si es cualquier otro
        else:
            datos_cepas = datos_totales[(datos_totales.iloc[:, 0] == 'Cepa')]
            microorganismos = []
            for cepa in datos_cepas.iloc[:, 2]:
                if 'BLEE' in cepa:
                    microorganismos.append([cepa, '(+)'])
                
                else:
                    microorganismos.append([cepa, None])

        return microorganismos


    def obtener_datos_demograficos_de_un_paciente(self, nombre_archivo):
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

            return [fecha_ingreso, tipo_muestra, n_cultivo, rut, nombre_paciente, seccion, fecha_firma]


formateador = Formateador()
lista = formateador.hacer_tabla_global()

fecha = os.getcwd().split('\\')[-2]
tipo = os.getcwd().split('\\')[-1]
nombre_archivo = f'{fecha}_DATOS_{tipo}.xlsx'

lista.to_excel(nombre_archivo, index = False)