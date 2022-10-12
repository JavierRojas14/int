import pandas as pd
import requests
from time import sleep

pd.set_option('display.max_colwidth', None)
pd.options.mode.chained_assignment = None  # default='warn'

TRADUCTOR_SIGFE_SIGCOM = pd.read_excel('input\\relacion_sigfe_sigcom_cristian_GG.xlsx')
TRADUCTOR_SIGFE_SIGCOM['COD SIGFE'] = TRADUCTOR_SIGFE_SIGCOM['COD SIGFE'].str.replace("'", "", \
                                                                                      regex = False)
TRADUCTOR_SIGFE_SIGCOM['COD SIGCOM'] = TRADUCTOR_SIGFE_SIGCOM['COD SIGCOM'].astype(str)

TICKET_MERCADO_PUBLICO = '7CA7E3D8-361B-415F-84EB-88C0B89838B5'

EXCEPCIONES_SIGFE = {
    '221299901601': 'FERNANDO BARAONA EN RRHH. ANEDIN EN GASTO GENERAL',
    '221299901602': 'Todo en RRHH',
    '221299900902': 'Cardiologia y Cardiocirugia en RRHH. UC Christus en gastos generales',
    '221299900201': 'M Meneses cargado en RRHH',
    '221299900202': 'J Andueza y Cardiocirugia en RRHH'
}

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
        estado_ej_presup, \
        disponibilidad_devengo, \
        formato_gg_sigcom = self.cargar_archivos_y_tratar_df()

        suma_gastos_ej_presup = self.obtener_suma_ej_presup_total(estado_ej_presup)

        suma_desglosada_por_sigfe, \
        suma_desglosada_por_sigcom, \
        facturas_gg, \
        facturas_rrhh = self.desglosar_gastos_generales_y_rrhh(suma_gastos_ej_presup, \
                                                               disponibilidad_devengo)

        detalle_facturas = self.obtener_detalle_facturas(facturas_gg)

        formato_rellenado = self.rellenar_formato(suma_desglosada_por_sigcom, \
                                                  formato_gg_sigcom)

        self.guardar_archivos(suma_desglosada_por_sigfe, suma_desglosada_por_sigcom, \
                              facturas_gg, facturas_rrhh, \
                              detalle_facturas, \
                              formato_rellenado)

    def cargar_archivos_y_tratar_df(self):
        '''
        Esta función permite cargar los archivos "Ejecución presupuestaria", "Disponibilidad
        Devengo" y "Formato Gasto General".

        - Agrega la columna "COD SIGFE" a los dos primeros archivos. Además, los COD SIGFE
        están en formato str.
        '''
        estado_ej_presup = pd.read_excel('input\\SA_EstadoEjecucionPresupuestaria.xls', header = 6)
        disponibilidad_devengo = pd.read_excel('input\\SA_DisponibilidadDevengoPresupuestario.xls',\
                                               header = 5)
        formato_gg_sigcom = pd.read_excel('input\\Formato 3_Gasto General 2022-10.xlsx')

        columnas_utiles_ej_presup = ['Nivel', 'Concepto Presupuestario', 'Devengado']
        columnas_utiles_disponibilidad_devengo = ['Titulo', 'Principal', 'Número Documento', \
                                                  'Concepto Presupuestario', 'Monto Vigente']

        estado_ej_presup = estado_ej_presup[columnas_utiles_ej_presup]
        disponibilidad_devengo = disponibilidad_devengo[columnas_utiles_disponibilidad_devengo]

        estado_ej_presup['COD SIGFE'] = estado_ej_presup['Concepto Presupuestario'].str.split()\
                                                                                   .str[0]

        disponibilidad_devengo['COD SIGFE'] = disponibilidad_devengo['Concepto Presupuestario'].str\
                                              .split().str[0]

        estado_ej_presup = pd.merge(estado_ej_presup, TRADUCTOR_SIGFE_SIGCOM, how = 'inner', \
                                    on = 'COD SIGFE')

        disponibilidad_devengo = pd.merge(disponibilidad_devengo, TRADUCTOR_SIGFE_SIGCOM, \
                                          how = 'inner', on = 'COD SIGFE')

        formato_gg_sigcom = formato_gg_sigcom.rename(columns = {'Unnamed: 0': 'Centros de costo'})
        formato_gg_sigcom = formato_gg_sigcom.set_index('Centros de costo')

        return estado_ej_presup, disponibilidad_devengo, formato_gg_sigcom

    def obtener_suma_ej_presup_total(self, estado_ej_presup):
        '''
        Permite obtener la suma de la ejecución presupuestaria, tanto por COD SIGFE, como
        COD SIGCOM.
        '''

        suma_ej_presup = estado_ej_presup.groupby(['COD SIGCOM', 'ITEM SIGCOM', 'COD SIGFE'], \
                                                  dropna = False)['Devengado'].sum().to_frame()

        suma_ej_presup['Devengado_ej_presup_y_estado_devengo'] = suma_ej_presup['Devengado']

        suma_ej_presup = suma_ej_presup.rename(columns = {'Devengado': 'Devengado_ej_presup'})
        suma_ej_presup = suma_ej_presup.reset_index()

        suma_ej_presup['Devengado_ej_presup'] = suma_ej_presup['Devengado_ej_presup'] \
                                                .astype('Int32')

        suma_ej_presup['Devengado_ej_presup_y_estado_devengo'] = suma_ej_presup['Devengado_ej_presup_y_estado_devengo'].astype('Int32')

        return suma_ej_presup

    def desglosar_gastos_generales_y_rrhh(self, suma_gastos_ej_presup_por_sigfe, disponibilidad_devengo):
        print('ANALIZANDO EL ESTADO DE DEVENGO \n')
        facturas_rrhh = pd.DataFrame()

        filtro_metros_cuadrados = disponibilidad_devengo['COD SIGCOM'].isin([92, 93, 100, 133, 170])
        facturas_globales = disponibilidad_devengo[~filtro_metros_cuadrados]

        for codigo_sigfe_excepcion in EXCEPCIONES_SIGFE:
            print('------------------------------------------------------\n')
            print(f'Analizando la excepcion: {codigo_sigfe_excepcion} \n')
            query_excepcion = facturas_globales.query('`COD SIGFE` == @codigo_sigfe_excepcion')

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

            print(f'Las siguientes facturas irán a RRHH:\n{df_a_rrhh[["Titulo", "Monto Vigente"]].to_markdown()} \n\n'
                  f'Las siguientes facturas irán a GG:\n{df_a_gg[["Titulo", "Monto Vigente"]].to_markdown()}\n')

            print(f'El monto destinado a RRHH será de: {valor_a_rrhh} \n'
                  f'El monto destinado a GG será de: {valor_a_gg}\n')

            facturas_rrhh = pd.concat([facturas_rrhh, df_a_rrhh])
            facturas_globales = facturas_globales.drop(df_a_rrhh.index)

            mask_excepcion = (suma_gastos_ej_presup_por_sigfe['COD SIGFE'] == codigo_sigfe_excepcion)

            suma_gastos_ej_presup_por_sigfe.loc[mask_excepcion, 'Devengado_ej_presup_y_estado_devengo'] = valor_a_gg
            suma_gastos_ej_presup_por_sigfe.loc[mask_excepcion, 'Devengado_desglosado_a_gg_estado_devengo'] = valor_a_gg
            suma_gastos_ej_presup_por_sigfe.loc[mask_excepcion, 'Devengado_desglosado_a_rrhh_estado_devengo'] = valor_a_rrhh
        
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

        return suma_gastos_ej_presup_por_sigfe, \
               suma_gastos_ej_presup_por_sigcom, \
               facturas_globales, facturas_rrhh

    def obtener_detalle_facturas(self, facturas_gg):
        '''
        Esta función permite obtener el detalle de cada factura involucrada en el gasto general del item SIGCOM.
        Para esto, toma los items presupuestarios involucrados en el gasto general y busca las facturas en la disponibilidad de devengo.
        '''
        print('BUSCANDO ORDENES DE COMPRA DE LAS SIGUIENTES FACTURAS: \n\n')

        cols_a_mostrar = ["Titulo", "Número Documento", \
                          "COD SIGCOM", "COD SIGFE"]
        print(facturas_gg)
        facturas_formateadas = facturas_gg[cols_a_mostrar].to_markdown()
        print(facturas_formateadas)

        mask_con_oc = facturas_gg['Titulo'].str.contains('/')

        facturas_gg['folio_oc'] = facturas_gg[mask_con_oc]['Titulo'].str.split('/').str[3]

        print('\n\n------ Buscando las ordenes de compra... ------ \n\n')
        facturas_gg['detalle_oc'] = facturas_gg[mask_con_oc]['folio_oc'].apply(self.funcion_obtener_requests_mercado_publico)
        
        return facturas_gg

    def funcion_obtener_requests_mercado_publico(self, orden_de_compra):
        
        orden_de_compra = orden_de_compra.strip()

        if orden_de_compra and '-' in orden_de_compra:
            print(f'Pidiendo la orden de compra: {orden_de_compra}')
            url_request = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?codigo={orden_de_compra}&ticket={TICKET_MERCADO_PUBLICO}"

            try:
                response = requests.get(url_request, timeout = 20)
                print(response.status_code)
                response = response.json()['Listado'][0]['Items']
                sleep(1.9)
            
            except Exception as e:
                print(e)
                response = None

            return response
    
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
            
                