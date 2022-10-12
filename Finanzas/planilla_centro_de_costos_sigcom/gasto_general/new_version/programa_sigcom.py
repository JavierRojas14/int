import json
import os
from time import sleep

import numpy as np
import pandas as pd
import requests

from constantes import (CENTROS_DE_COSTO, CODIGOS_CENTRO_DE_COSTO, NOMBRES_CENTRO_DE_COSTO,
                        EXCEPCIONES_SIGFE, TICKET_MERCADO_PUBLICO)

pd.set_option('display.max_colwidth', None)
pd.options.mode.chained_assignment = None  # default='warn'

class AnalizadorSIGCOM:
    '''Esta es la definición de la clase AnalizadorSIGCOM, que permite:

    1) Leer los archivos de estado de ejecución presupuestaria, estado de devengo,
    planilla PERC y el formato SIGOM para los gastos generales.
    '''
    def __init__(self):
        pass

    def correr_programa(self):
        '''
        Esta es la función principal del programa, permite correrlo de forma general.
        '''
        estado_ej_presup, disponibilidad_devengo = self.cargar_archivos_y_tratar_df()

        estado_ej_presup, \
        facturas_a_gg, \
        facturas_a_rrhh, \
        facturas_a_fondos_fijos = self.desglosar_gastos_generales_rrhh_fondo_fijo(estado_ej_presup,\
                                                                        disponibilidad_devengo)

        facturas_a_gg = self.obtener_detalle_facturas(facturas_a_gg)
        facturas_a_gg = self.rellenar_centros_de_costos(facturas_a_gg)

        # formato_rellenado = self.rellenar_formato(suma_desglosada_por_sigcom, \
        #                                           formato_gg_sigcom)

        # self.guardar_archivos(suma_desglosada_por_sigfe, suma_desglosada_por_sigcom, \
        #                       facturas_gg, facturas_rrhh, \
        #                       detalle_facturas, \
        #                       formato_rellenado)

    def cargar_archivos_y_tratar_df(self):
        '''
        Esta función permite cargar los archivos necesarios para calcular los Gastos Generales
        (EjecuciónPresupuestaria y DisponbilidadDevengo)

        - El archivo ejecución presupuestaria lo carga, filtra por las columnas útiles ("Concepto
        Presupuestario" y "Devengado"), filtra los headers de las subtablas presentes y finalmente
        asigna los dtypes correctos (object, int64 y object; Concepto Presupuestario, Devengado
        y COD SIGFE).

        - Agrega la columna "COD SIGFE" a los dos primeros archivos. Además, los COD SIGFE
        están en formato str.
        '''
        print('- Cargando los archivos -')
        estado_ej_presup = pd.read_excel('input\\SA_EstadoEjecucionPresupuestaria.xls', header = 6)
        estado_ej_presup = estado_ej_presup[['Concepto Presupuestario', 'Devengado']]
        estado_ej_presup = estado_ej_presup.query('`Devengado` != "Devengado"')
        estado_ej_presup['Devengado'] = estado_ej_presup['Devengado'].astype(np.int64)
        estado_ej_presup['Devengado_merge'] = estado_ej_presup['Devengado'].astype(np.int64)
        estado_ej_presup['COD SIGFE'] = estado_ej_presup['Concepto Presupuestario'].str.split()\
                                                                                   .str[0]

        disponibilidad_devengo = pd.read_excel('input\\SA_DisponibilidadDevengoPresupuestario.xls',\
                                               header = 5)
        disponibilidad_devengo = disponibilidad_devengo[['Titulo', 'Principal', 'Número Documento',\
                                                        'Concepto Presupuestario', 'Monto Vigente']]
        disponibilidad_devengo['COD SIGFE'] = disponibilidad_devengo['Concepto Presupuestario'].str\
                                              .split().str[0]
        disponibilidad_devengo['oc'] = disponibilidad_devengo['Titulo'].str.split('/').str[3]


        traductor_sigfe_sigcom = pd.read_excel('input\\relacion_sigfe_sigcom_cristian_GG.xlsx')
        traductor_sigfe_sigcom['COD SIGFE'] = traductor_sigfe_sigcom['COD SIGFE'] \
                                              .str.replace("'", "", regex = False)
        traductor_sigfe_sigcom['COD SIGCOM'] = traductor_sigfe_sigcom['COD SIGCOM'] \
                                              .str.replace("'", "", regex = False)

        estado_ej_presup = pd.merge(estado_ej_presup, traductor_sigfe_sigcom, how = 'inner', \
                                            on = 'COD SIGFE')
        disponibilidad_devengo = pd.merge(disponibilidad_devengo, traductor_sigfe_sigcom, \
                                          how = 'inner', on = 'COD SIGFE')

        return estado_ej_presup, disponibilidad_devengo

    def desglosar_gastos_generales_rrhh_fondo_fijo(self, estado_ej_presup, disponibilidad_devengo):
        '''
        Esta función permite desglosar el detalle de cada ítem SIGFE, y sus facturas asociadas.

        - En este caso, se filtran las facturas asociadas a gastos por m2 (COD SIGCOM
        92, 93, 100, 133 y 170), ya que no es necesario analizarlas (Sin embargo, se podrían
        dejar para ver si los gastos coinciden con los de la ejecución presupuestaria

        - Luego, se guardan las facturas que van asociadas a gastos de RRHH, analizando las ex
        cepciones.

        - Después, se guardan las facturas que van asociadas a FONDOS FIJOS, y se guardan.

        - Finalmente, se sacan las facturas de los últimos dos apartados, y se obtienen las
        facturas asociadas a GG.
        '''

        print('- Analizando la disponbilidad de devengo y sus facturas - \n')
        filtro_metros_cuadrados = disponibilidad_devengo['COD SIGCOM'].isin([92, 93, 100, 133, 170])
        facturas_a_gg = disponibilidad_devengo[~filtro_metros_cuadrados]

        facturas_a_rrhh, estado_ej_presup = self.obtener_excepciones_a_rrhh(facturas_a_gg, \
                                                                            estado_ej_presup)
        facturas_a_gg = facturas_a_gg.drop(facturas_a_rrhh.index)

        facturas_a_fondos_fijos, estado_ej_presup = self.obtener_fondos_fijos(facturas_a_gg, \
                                                                            estado_ej_presup)

        facturas_a_gg = facturas_a_gg.drop(facturas_a_fondos_fijos.index)

        return estado_ej_presup, facturas_a_gg, facturas_a_rrhh, facturas_a_fondos_fijos

    def obtener_excepciones_a_rrhh(self, facturas_a_analizar, estado_ej_presup):
        facturas_a_rrhh = pd.DataFrame()

        for codigo_sigfe_excepcion in EXCEPCIONES_SIGFE:
            print(f'\n Analizando la excepcion: {codigo_sigfe_excepcion} \n')
            query_excepcion = facturas_a_analizar.query('`COD SIGFE` == @codigo_sigfe_excepcion')

            if codigo_sigfe_excepcion == '221299901601':
                mask_a_rrhh = query_excepcion['Principal'].str.contains('BARAONA')

            elif codigo_sigfe_excepcion == '221299901602':
                mask_a_rrhh = query_excepcion['Principal'].notna()

            elif codigo_sigfe_excepcion == '221299900902':
                mask_a_rrhh = query_excepcion['Principal'].str.contains('CARDIOLOGIA') | \
                              (query_excepcion['Principal'].str.contains('CARDIOCIRUGIA'))

            elif codigo_sigfe_excepcion == '221299900201':
                mask_a_rrhh = query_excepcion['Principal'].str.contains('MANUEL MENESES')

            elif codigo_sigfe_excepcion == '221299900202':
                mask_a_rrhh = query_excepcion['Principal'].str.contains('ANDUEZA') | \
                              query_excepcion['Principal'].str.contains('CARDIOCIRUGIA')

            df_a_rrhh = query_excepcion[mask_a_rrhh]
            df_a_gg = query_excepcion[~mask_a_rrhh]

            valor_a_rrhh = df_a_rrhh['Monto Vigente'].sum()
            valor_a_gg = df_a_gg['Monto Vigente'].sum()

            print(f'Las siguientes facturas irán a RRHH: \n'
                  f'{df_a_rrhh[["Titulo", "Monto Vigente"]].to_markdown()} \n'
                  f'El monto destinado a RRHH será de: {valor_a_rrhh} \n')

            print(f'Las siguientes facturas irán a GG: \n'
                  f'{df_a_gg[["Titulo", "Monto Vigente"]].to_markdown()} \n'
                  f'El monto destinado a GG será de: {valor_a_gg} \n')

            facturas_a_rrhh = pd.concat([facturas_a_rrhh, df_a_rrhh])
            mask_excepcion = (estado_ej_presup['COD SIGFE'] == codigo_sigfe_excepcion)

            estado_ej_presup.loc[mask_excepcion, 'Devengado_merge'] = valor_a_gg
            estado_ej_presup.loc[mask_excepcion, 'Costo_a_gg'] = valor_a_gg
            estado_ej_presup.loc[mask_excepcion, 'Costo_a_rrhh'] = valor_a_rrhh

        return facturas_a_rrhh, estado_ej_presup

    def obtener_fondos_fijos(self, facturas_a_analizar, estado_ej_presup):
        print('\n - Analizando fondos fijos -\n')
        mask_fondos_fijos = facturas_a_analizar['Titulo'].str.upper() \
                                                            .str.contains('FIJO')

        facturas_a_fondos_fijos = facturas_a_analizar[mask_fondos_fijos]
        print(f'Las facturas que van a fondos fijos son: \n'
              f'{facturas_a_fondos_fijos[["Titulo", "Principal", "COD SIGFE", "COD SIGCOM"]].to_markdown()}')
        suma_fondos_fijos = facturas_a_fondos_fijos.groupby('COD SIGFE').sum()
        print(f'\nY suman lo siguiente (esto se va a descontar): \n{suma_fondos_fijos.to_markdown()}')

        for codigo_sigfe in suma_fondos_fijos.index:
            monto = suma_fondos_fijos.loc[codigo_sigfe][0]

            mask_fondo_fijo = (estado_ej_presup['COD SIGFE'] == codigo_sigfe)
            estado_ej_presup.loc[mask_fondo_fijo, 'Descuento_fondo_fijo'] = monto
            resta_fondo = (estado_ej_presup.loc[mask_fondo_fijo, 'Devengado_merge']- monto)

            estado_ej_presup.loc[mask_fondo_fijo, 'Devengado_merge'] = resta_fondo

        return facturas_a_fondos_fijos, estado_ej_presup

    def obtener_detalle_facturas(self, facturas_a_gg):
        '''
        Esta función permite obtener el detalle de cada factura involucrada en el gasto general
        del item SIGCOM.

        Para esto, toma los items presupuestarios involucrados en el gasto general y busca las
        facturas en la disponibilidad de devengo.
        '''
        print('- Se buscarán las ordenes de compra en marcado público -\n')

        if 'facturas_gg_con_detalle.xlsx' in os.listdir('input'):
            print('Ya existe un archivo con el detalle de las facturas, se leerá ese archivo.')
            facturas_a_gg = pd.read_excel('input\\facturas_gg_con_detalle.xlsx')

        else:
            mask_con_oc = facturas_a_gg['oc'].str.contains('-')
            facturas_a_buscar = facturas_a_gg[mask_con_oc]

            cols_a_mostrar = ['Titulo', 'Número Documento','COD SIGCOM', 'COD SIGFE']
            print(facturas_a_buscar[cols_a_mostrar].to_markdown())

            facturas_a_gg['detalle_oc'] = facturas_a_buscar['oc'] \
                                        .apply(self.funcion_obtener_requests_mercado_publico)

            facturas_a_buscar['centro_de_costo_asociado'] = None

            facturas_a_gg.to_excel('input\\facturas_gg_con_detalle.xlsx')

        return facturas_a_gg

    def funcion_obtener_requests_mercado_publico(self, orden_de_compra):
        print(f'Pidiendo la orden de compra: {orden_de_compra}')
        orden_de_compra = orden_de_compra.strip()
        url_request = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra." \
                      f"json?codigo={orden_de_compra}&ticket={TICKET_MERCADO_PUBLICO}"


        try:
            response = requests.get(url_request, timeout = 20)
            detalle_oc = response.json()['Listado'][0]['Items']

            sleep(2.0)

        except Exception as excepcion:
            print(type(excepcion), excepcion)
            detalle_oc = excepcion

        return detalle_oc

    def rellenar_centros_de_costos(self, facturas_a_gg):
        print('\n- Se rellenarán los centros de costo asociados a cada factura - \n')

        for factura in facturas_a_gg.itertuples():
            detalle_formateado = json.dumps(factura.detalle_oc, indent = 1, ensure_ascii = False)
            print('------------------------------------------------')
            print('------------------------------------------------')

            print(f'La factura {factura.Titulo} tiene el siguiente detalle: \n'
                  f'CODIGO SIGFE: {factura._7} - {factura._9}\n'
                  f'CODIGO SIGCOM: {factura._10} - {factura._11} \n\n'
                  f'{detalle_formateado} \n')
            
            while True:
                cc = input('¿Qué centro de costo crees que es? (Ingresar sólo el N° de código. '
                        'Los códigos están en constantes.py): ')

                if cc in CODIGOS_CENTRO_DE_COSTO:
                    break

                else:
                    print('Debes ingresar un código válido.')

            facturas_a_gg.loc[factura.Index, 'centro_de_costo_asignado'] = cc
            print('------------------------------------------------')
            print('------------------------------------------------\n\n')

        facturas_a_gg.to_excel('prueba.xlsx')

        return facturas_a_gg

    def obtener_formato_rrhh(self, facturas_rrhh):
        facturas_rrhh = facturas_rrhh.groupby('Principal')['Monto Vigente'] \
                                    .sum() \
                                    .reset_index()

        facturas_rrhh['Principal'] = facturas_rrhh['Principal'].str \
                                                            .split(n = 1)

        facturas_rrhh['Rut'] = facturas_rrhh['Principal'].str[0]
        facturas_rrhh['Nombre'] = facturas_rrhh['Principal'].str[1]
        facturas_rrhh = facturas_rrhh[['Rut', 'Nombre', 'Monto Vigente']]

        suma_gastos_ej_presup_por_sigcom = suma_gastos_ej_presup_por_sigfe \
                                        .groupby('COD SIGCOM') \
                                        .sum() \
                                        .reset_index()

    def rellenar_formato(self, suma_desglosada_por_sigcom, formato_sigcom_gg):
        print('--------------------------------\n\n'
              'Rellenando la planilla formato')
        columnas_antiguas = formato_sigcom_gg.columns
        formato_sigcom_gg.columns = formato_sigcom_gg.columns.str.split('-').str[0].astype(int)

        for codigo_gasto in suma_desglosada_por_sigcom['COD SIGCOM']:
            if codigo_gasto in formato_sigcom_gg.columns:
                valor_a_ingresar = suma_desglosada_por_sigcom.loc[codigo_gasto, 'Devengado_ej_presup_y_estado_devengo']
                formato_sigcom_gg.loc['Valor General', codigo_gasto] = valor_a_ingresar

                print(f'El codigo {codigo_gasto} se ingresó a la planilla \n'
                      f'Se ingresó con el monto: {valor_a_ingresar} \n'
                      f'--------------------------------------------')

        formato_sigcom_gg.columns = columnas_antiguas
        formato_sigcom_gg = formato_sigcom_gg.reset_index()
        
        return formato_sigcom_gg
    
    def guardar_archivos(self, suma_desglosada_por_sigfe, suma_desglosada_por_sigcom, \
                              facturas_gg, facturas_rrhh, \
                              detalle_facturas, \
                              formato_rellenado):

        with pd.ExcelWriter('output.xlsx') as writer:
            formato_rellenado.to_excel(writer, sheet_name = 'formato_rellenado', \
                                     index = False)

            suma_desglosada_por_sigfe.to_excel(writer, sheet_name = 'suma_desglosada_por_sigfe', \
                                     index = False)
                                    
            suma_desglosada_por_sigcom.to_excel(writer, sheet_name = 'suma_desglosada_por_sigcom', \
                                     index = False)
            
            facturas_gg.to_excel(writer, sheet_name = 'facturas_gg', \
                                     index = False)
            
            facturas_rrhh.to_excel(writer, sheet_name = 'facturas_rrhh', \
                                     index = False)
            
            detalle_facturas.to_excel(writer, sheet_name = 'detalle_facturas', \
                                     index = False)


objeto = AnalizadorSIGCOM()
objeto.correr_programa()
            
                