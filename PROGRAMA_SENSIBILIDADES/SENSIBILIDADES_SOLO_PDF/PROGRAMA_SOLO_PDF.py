import tabula
import pandas as pd
import numpy as np
import os
import pdfplumber
from datetime import datetime
import json

#################################################

with open('DICCIONARIO_CODIGO_NOMBRE_FARMACOS.json', 'r', encoding = 'utf-8') as f:
    DICCIONARIO_CODIGO_NOMBRE_FARMACOS = json.load(f)

with open('ENTEROBACTERIAS.json', 'r', encoding = 'utf-8') as f:
    diccionario_enteros = json.load(f)
    TODAS_LAS_ENTEROBACTERIAS = []
    for llave in diccionario_enteros.keys():
        TODAS_LAS_ENTEROBACTERIAS += diccionario_enteros[llave]

with open('ENTEROBACTERIAS_RESISTENTES_NATURALMENTE.json', 'r', encoding = 'utf-8') as f:
    ENTEROBACTERIAS_RESISTENTES_NATURALMENTE = json.load(f)

with open('GENEROS_ENTEROBACTERIAS.json', 'r', encoding = 'utf-8') as f:
    GENEROS_ENTEROBACTERIAS = json.load(f)

#################################################
COLUMNAS_DATOS_DEMOGRAFICOS = ['Ingreso', 'Tipo muestra', 'Nº de Cultivo', 'Rut', 'Nombre', 'Servicio', 'Comentario', 'Fecha Firma', 'Microorganismo', 'BLEE']
COLUMNAS_FARMACOS = list(DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values()) + list(map(lambda x: f'CIM {x}', DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values()))
COLUMNAS_A_NO_OCUPAR = ['CZA', '?', '? 2', 'CIM CZA', 'CIM ?', 'CIM ? 2']
COLUMNAS_EVE = COLUMNAS_DATOS_DEMOGRAFICOS + list(DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values())[:-3] + ['CIM PEN', 'CIM CAF', 'CIM CAZ', 'CIM DAP', 'CIM VAN', 'CIM COL', 'CIM CFTXIMA', 'CIM COTRI']

LARGO_COLUMNAS_FARMACOS = len(COLUMNAS_FARMACOS)
ANTIBIOGRAMA_VACIO = [None for i in range(LARGO_COLUMNAS_FARMACOS)]
#################################################

class ProgramaSensibilidades:
    def __init__(self):
        pass

    def formatear_formato_eve(self, df):
        df = df.loc[:, COLUMNAS_EVE]
        df['CIM CAF'] = None
        df['CIM CAZ'] = None
        df['CIM DAP'] = None
        df['CIM COL'] = None
        df['CIM CFTXIMA'] = None
        df['CIM COTRI'] = None
        return df


    def hacer_tabla_global(self):
        todas_las_entradas = self.obtener_entradas_todos_los_pacientes()
        columnas = COLUMNAS_DATOS_DEMOGRAFICOS + COLUMNAS_FARMACOS
        df = pd.DataFrame(todas_las_entradas, columns = columnas)
        df.drop(columns = COLUMNAS_A_NO_OCUPAR, inplace = True)

        return df

    def obtener_entradas_todos_los_pacientes(self):
        entradas_todos_los_pacientes = []

        for nombre_archivo in os.listdir():
            if '.pdf' in nombre_archivo:
                entradas_de_un_paciente = self.obtener_entradas_de_un_paciente(nombre_archivo)
                print(f'Leyendo {nombre_archivo}, tiene {len(entradas_de_un_paciente)} entradas')

                for entrada_de_un_paciente in entradas_de_un_paciente:
                    entradas_todos_los_pacientes.append(entrada_de_un_paciente)

        return entradas_todos_los_pacientes
    
    def obtener_entradas_de_un_paciente(self, nombre_archivo):
        tipo_archivo, texto_completo_pdf = self.obtener_tipo_de_archivo_y_texto_pdf(nombre_archivo)

        if tipo_archivo != None:
            datos_persona = self.obtener_datos_demograficos_de_un_paciente(texto_completo_pdf)
            lista_microorganismos_persona = self.obtener_microorganismos_de_un_paciente(texto_completo_pdf, tipo_archivo)
            lista_antibiogramas_persona = self.obtener_antibiogramas_de_un_paciente(nombre_archivo, tipo_archivo, len(lista_microorganismos_persona))
            entradas_de_un_paciente_formato_lista = self.formatear_todos_los_datos_un_paciente(datos_persona, lista_microorganismos_persona, lista_antibiogramas_persona)

            return entradas_de_un_paciente_formato_lista
    
    def formatear_todos_los_datos_un_paciente(self, datos_persona, lista_microorganismos_persona, lista_antibiogramas_persona):
        entradas = []
        diccionario_numeracion_cepas = {0: ' I', 1: ' II', 2: ' III', 3: ' IV'}
        for i in range(len(lista_microorganismos_persona)):
            micro = lista_microorganismos_persona[i]
            antibio = lista_antibiogramas_persona[i]

            antibio[:] = self.cambiar_sensibilidades_enteros_y_staphylos(micro[0], antibio)

            if len(lista_microorganismos_persona) > 1:
                datos_persona_romanos = datos_persona.copy()
                nuevo_numero_cultivo = f'{datos_persona_romanos[2]}{diccionario_numeracion_cepas[i]}'
                datos_persona_romanos[2] = nuevo_numero_cultivo

                entrada_paciente = datos_persona_romanos + micro + antibio
            
            else:
                entrada_paciente = datos_persona + micro + antibio

            entradas.append(entrada_paciente)

        return entradas
    
    def cambiar_sensibilidades_enteros_y_staphylos(self, nombre_microorganismo, antibiograma):
        if any(antibiograma):
            if ('Staphylococcus' in nombre_microorganismo) \
            or ('aureus' in nombre_microorganismo) \
            or ('epidermidis' in nombre_microorganismo) \
            or ('capitis' in nombre_microorganismo) \
            or ('coagulasa (-)' in nombre_microorganismo) \
            or ('epidermidis' in nombre_microorganismo) \
            or ('haemolyticus' in nombre_microorganismo) \
            or ('hominis' in nombre_microorganismo) \
            or ('lugdunensis' in nombre_microorganismo) \
            or ('pasteuri' in nombre_microorganismo) \
            or ('pettenkoferi' in nombre_microorganismo) \
            or ('pseudointermedius' in nombre_microorganismo) \
            or ('saprophyticus' in nombre_microorganismo) \
            or ('warneri' in nombre_microorganismo):
                antibiograma[19] = 'S'
                antibiograma[28] = 'S'
            
            # Formato completo
            if not('.' in nombre_microorganismo):
                    nombre_separado = nombre_microorganismo.split(' ')
                    genero, especie = nombre_separado[0], nombre_separado[1]
                    if genero in GENEROS_ENTEROBACTERIAS:
                        if not(nombre_microorganismo in ENTEROBACTERIAS_RESISTENTES_NATURALMENTE):
                            antibiograma[12] = 'S'
                            print(f'{nombre_microorganismo} es sensible a COL')
                        
                        else:
                            print(f'{nombre_microorganismo} es insensible a COL')
            
            else:
                if nombre_microorganismo in TODAS_LAS_ENTEROBACTERIAS:
                    if not(nombre_microorganismo in ENTEROBACTERIAS_RESISTENTES_NATURALMENTE):
                        antibiograma[12] = 'S'
                        print(f'{nombre_microorganismo} es sensible a COL \n')
                    
                    else:
                        print(f'{nombre_microorganismo} es insensible a COL \n')
           
        
        return antibiograma
    
    def obtener_tipo_de_archivo_y_texto_pdf(self, nombre_archivo):
        with pdfplumber.open(nombre_archivo) as pdf:
            texto_completo_pdf = pdf.pages[0].extract_text().split('\n')
            tipo_archivo = None

            for linea in texto_completo_pdf:
                if 'ANTIBIOGRAMA' in linea:
                    tipo_archivo = 'ANTI'
                    break

                elif ('CULTIVO DE HONGOS :' in linea) or ('Polimicrobiano' in linea) or ('HEMOCULTIVO AEROBICO :' in linea) or ('HEMOCULTIVO ANAEROBICO :' in linea) or ('CULTIVO CORRIENTE :' in linea):
                    tipo_archivo = 'NOANTI'
                    break

    
        return tipo_archivo, texto_completo_pdf

    
    def obtener_datos_demograficos_de_un_paciente(self, texto_completo_pdf):
        datos_personales_relevantes = texto_completo_pdf[3:12]

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
        
        for i in range(len(texto_completo_pdf)):
            linea = texto_completo_pdf[i]
            if 'CULTIVO DE HONGOS' in linea:
                n_cultivo = texto_completo_pdf[i + 1].split(' ')[-1]
                break
        
        comentario = None
        for linea in texto_completo_pdf:
            linea = linea.lower()
            if ('avisa' in linea) or ('avisado' in linea):
                comentario = 'ALERTA'
                break
        
        return [fecha_ingreso, tipo_muestra, n_cultivo, rut, nombre_paciente, seccion, comentario, fecha_firma]
    
    def borrador_recuentos_positivos(self, microorganismo):
        a_borrar = ['Rcto', '+', ':']
        for palabra in a_borrar:
            microorganismo = microorganismo.replace(palabra, ' ')

        microorganismo = microorganismo.strip()

        if microorganismo == 'Polimicrobiano':
            microorganismo = 'POLIMICROBIANO'
        
        return microorganismo
    
    def obtener_microorganismos_de_un_paciente(self, texto_pdf, tipo_archivo):
        microorganismos = []

        if tipo_archivo == 'ANTI':
            microorganismos = []
            for linea in texto_pdf:
                if ((('Cepa 1' in linea) or ('Cepa 2' in linea) or ('Cepa 3' in linea) or ('Cepa 4' in linea)) and (('ufc' in linea) or ('+' in linea))):
                    linea_separada = linea.split(' ')
                    for indice, palabra in enumerate(linea_separada):
                        if palabra == '1' or palabra == '2' or palabra == '3' or palabra == '4':
                            indice_inicio_microorganismo = indice + 1
                        
                        elif palabra == 'Mas' or palabra == 'Menos' or '.' in palabra or '+' in palabra:
                            indice_termino_miccroorganismo = indice
                            break
                        
                    microorganismo = ' '.join(linea_separada[indice_inicio_microorganismo: indice_termino_miccroorganismo])
                    microorganismos.append(microorganismo)

        
        else:
            for linea in texto_pdf:
                if ('CULTIVO DE HONGOS :' in linea) or ('HEMOCULTIVO AEROBICO :' in linea) or ('HEMOCULTIVO ANAEROBICO :' in linea) or ('UROCULTIVO : Polimicrobiano' in linea) or ('CULTIVO CORRIENTE :' in linea):
                    microorganismos = list(map(self.borrador_recuentos_positivos, linea.split(':', 1)[-1].split(',')))
                    break
        
        microorganismos = list(map(lambda microorg: [microorg, '(+)'] if ('BLEE' in microorg) else [microorg, None], microorganismos))
        return microorganismos
    
    
    def obtener_antibiogramas_de_un_paciente(self, nombre_archivo, tipo_archivo, numero_microorganismos):
        if tipo_archivo == 'ANTI':
            antibiograma_completo = self.obtener_antibiograma_completo(nombre_archivo)
            antibiogramas = self.separar_por_cepa(antibiograma_completo, numero_microorganismos)

        else:
            antibiogramas = [ANTIBIOGRAMA_VACIO for i in range(numero_microorganismos)]
        
        return antibiogramas
    
    def obtener_antibiograma_completo(self, nombre_archivo):
        df = tabula.read_pdf(nombre_archivo, columns = [64, 218, 264, 296, 346, 373, 424, 450, 507], pages = 1, guess = False)[0]
        ya_hay_inicio_antibio = False

        for i in range(len(df)):
            contenido_linea = df.iloc[i].values
            if 'ANTIBIO' in contenido_linea:
                indice_inicio_antibio = i + 1
                ya_hay_inicio_antibio = True
            
            elif not(('ANTIBIO' in  contenido_linea) or ('Cepa 1' in contenido_linea) or ('Sensible' in contenido_linea) or ('Resistente' in contenido_linea) or ('Intermedio' in contenido_linea)) and (ya_hay_inicio_antibio):
                indice_termino_antibio = i
                break

        antibiograma_completo = df.iloc[indice_inicio_antibio: indice_termino_antibio]
        antibiograma_completo.columns = antibiograma_completo.iloc[0]
        antibiograma_completo = antibiograma_completo.iloc[1:, :]
        antibiograma_completo['ANTIBIOTICOS'] = antibiograma_completo['ANTIBIOTICOS'].map(DICCIONARIO_CODIGO_NOMBRE_FARMACOS)
        antibiograma_completo.set_index('ANTIBIOTICOS', inplace = True)
        
        numero_cepas = len([i for i in list(antibiograma_completo.columns.dropna()) if 'Cepa' in i])
        antibiograma_completo = antibiograma_completo.iloc[:, 1: (2 * numero_cepas) + 1]
        print(antibiograma_completo)

        return antibiograma_completo
    
    def separar_por_cepa(self, antibiograma_completo, numero_microorganismos):
        antibiogramas = []

        if antibiograma_completo.empty:
            for i in range(numero_microorganismos):
                antibiogramas.append([None for i in range(LARGO_COLUMNAS_FARMACOS)])
        
        else:
            tablas_cepas = []
            for i in range(int((antibiograma_completo.shape[1]) / 2)):
                df = antibiograma_completo.iloc[:, i * 2: (i * 2) + 2].dropna(how = 'all', axis = 0)
                tablas_cepas.append(df)
            
            cambiador_nomenclatura_sensibilidades = {'Sensible': 'S', 'Resistente': 'R', 'Intermedio': 'I'}

            for df_cepa in tablas_cepas:
                diccionario_sensibilidades_a_llenar = {farmaco: None for farmaco in DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values()}
                diccionario_cim_a_llenar = {f'CIM {farmaco}': None for farmaco in DICCIONARIO_CODIGO_NOMBRE_FARMACOS.values()}
                for farmaco in df_cepa.index:
                    resultado_sensibilidad, cim = df_cepa.loc[farmaco][0], df_cepa.loc[farmaco][1]
                    diccionario_sensibilidades_a_llenar[farmaco] = cambiador_nomenclatura_sensibilidades[resultado_sensibilidad]
                    diccionario_cim_a_llenar[f'CIM {farmaco}'] = cim

                resultados = list((diccionario_sensibilidades_a_llenar | diccionario_cim_a_llenar).values())
                antibiogramas.append(resultados)

        return antibiogramas



programa = ProgramaSensibilidades()
tabla_global = programa.hacer_tabla_global()
tabla_eve = programa.formatear_formato_eve(tabla_global)

fecha = os.getcwd().split('\\')[-2]
tipo = os.getcwd().split('\\')[-1]
nombre_archivo = f'{fecha}_DATOS_{tipo}.xlsx'
nombre_archivo_eve = f'EVE_{fecha}_DATOS_{tipo}.xlsx'

tabla_global.to_excel(nombre_archivo, index = False)
tabla_eve.to_excel(nombre_archivo_eve, index = False)


