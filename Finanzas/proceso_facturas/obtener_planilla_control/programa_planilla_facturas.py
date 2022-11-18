'''
Este es un programa para generar la planilla de Control de Facturas. Unidad de Finanzas.
Javier Rojas Benítez
'''
import time
import datetime
import json
import os

import pandas as pd
from pandas.core.arrays import base

pd.options.mode.chained_assignment = None  # default='warn'


class GeneradorPlanillaFinanzas:
    '''
    Esta es la clase madre que permite obtener la planilla de control de facturas.
    Consta de 6 funciones principales.
    '''

    def __init__(self):
        pass

    def correr_programa(self):
        '''
        Esta función permite correr el programa de para obtener el cruce de bases de datos
        SII - ACEPTA - SIGFE - TURBO - SCI de facturas. Ejectura los siguientes pasos:

        - Cargar archivos (la función más costosa)
        - Unir los archivos según la llave RUT-DV + Folio SII
        - Calcular el tiempo entre que se recibe la factura desde el SII y la fecha actual.
        - Obtener las referencias entre Notas de Créditos y Facturas.
        - Filtrar columnas innecesarias, y solo dejar las columnas necesarias
        '''
        archivos_facturas = self.obtener_archivos('facturas')
        dfs_limpias = self.obtener_facturas_base_de_datos(archivos_facturas)

        # archivos_oc = self.obtener_archivos('oc')
        # oc_limpias = self.obtener_oc_base_de_datos(archivos_oc)
        # print(oc_limpias)

        df_izquierda = self.unir_dfs(dfs_limpias)

        df_izquierda = self.calcular_tiempo_8_dias(df_izquierda)
        df_izquierda = self.obtener_referencias_nc(df_izquierda)
        df_izquierda = self.asociar_saldo_de_oc(df_izquierda)
        df_izquierda = self.obtener_columnas_necesarias(df_izquierda)

        self.guardar_dfs(df_izquierda)

        print('\nListo! No hubo ningún problema')

    def obtener_archivos(self, base_de_datos):
        archivos_a_leer = {}
        base_de_datos_a_leer = f'crudos\\base_de_datos_{base_de_datos}'

        for carpeta_base_de_datos in os.listdir(base_de_datos_a_leer):
            archivos_a_leer[carpeta_base_de_datos] = []
            for archivo in os.listdir(
                    os.path.join(base_de_datos_a_leer, carpeta_base_de_datos)):
                ruta_archivo = os.path.join(
                    base_de_datos_a_leer, carpeta_base_de_datos, archivo)
                archivos_a_leer[carpeta_base_de_datos].append(ruta_archivo)

        hoy = datetime.date.today()
        anio_actual = str(hoy.year)

        leer = input('¿Quieres leer los archivos de este año o todos los años? \n'
                     '1) Este año \n'
                     '2) Todos los años \n'
                     '> ')

        if leer == '1':
            for base_de_datos, lista_archivos in archivos_a_leer.items():
                archivos_a_leer[base_de_datos] = [
                    archivo for archivo in lista_archivos if anio_actual in archivo]

        return archivos_a_leer

    def obtener_facturas_base_de_datos(self, archivos_a_leer):
        diccionario_base_de_datos = {}
        for base_de_datos, lista_archivos in archivos_a_leer.items():
            print(f'Leyendo {base_de_datos} - {lista_archivos}')
            if base_de_datos == 'ACEPTA':
                df_sumada = self.leer_acepta(lista_archivos)

            elif base_de_datos == 'OBSERVACIONES':
                df_sumada = self.leer_observaciones(lista_archivos)

            elif base_de_datos == 'SCI':
                df_sumada = self.leer_sci(lista_archivos)

            elif base_de_datos == 'SIGFE':
                df_sumada = self.leer_sigfe(lista_archivos)

            elif base_de_datos == 'SII':
                df_sumada = self.leer_sii(lista_archivos)

            elif base_de_datos == 'TURBO':
                df_sumada = self.leer_turbo(lista_archivos)

            df_sumada['RUT Emisor'] = df_sumada['RUT Emisor'].str.replace('.', '', regex=False) \
                .str.upper() \
                .str.strip()

            df_sumada['llave_id'] = df_sumada['RUT Emisor'].astype(
                str) + df_sumada['Folio'].astype(str)
            df_sumada = df_sumada.set_index('llave_id')

            df_sumada.columns = df_sumada.columns + f'_{base_de_datos}'
            df_sumada.columns = df_sumada.columns.str.replace(' ', '_')

            diccionario_base_de_datos[base_de_datos] = df_sumada

        return diccionario_base_de_datos

    def leer_acepta(self, lista_archivos):
        dfs = map(pd.read_excel, lista_archivos)
        df_sumada = pd.concat(dfs)
        df_sumada = df_sumada.rename(columns={'emisor': 'RUT Emisor', 'folio': 'Folio'})

        return df_sumada

    def leer_observaciones(self, lista_archivos):
        dfs = map(pd.read_excel, lista_archivos)
        df_sumada = pd.concat(dfs)
        df_sumada = df_sumada[['RUT Emisor SII', 'Folio SII', 'OBSERVACION OBSERVACIONES']]
        df_sumada = df_sumada.rename(columns={'RUT Emisor SII': 'RUT Emisor',
                                              'Folio SII': 'Folio',
                                              'OBSERVACION OBSERVACIONES': 'OBSERVACION'})

        return df_sumada

    def leer_sci(self, lista_archivos):
        dfs = map(lambda x: pd.read_csv(x, delimiter=','), lista_archivos)
        df_sumada = pd.concat(dfs)
        df_sumada = df_sumada.rename(columns={'Rut Proveedor': 'RUT Emisor',
                                              'Numero Documento': 'Folio'})

        df_sumada['Folio'] = df_sumada['Folio'].astype(str) \
            .str.replace('.0', '', regex=False)

        return df_sumada

    def leer_sigfe(self, lista_archivos):
        dfs = map(lambda x: pd.read_csv(x, delimiter=',', header=10), lista_archivos)
        df_sumada = pd.concat(dfs)
        df_sumada = df_sumada.dropna(subset=['Folio'])
        df_sumada = df_sumada.query('`Cuenta Contable` != "Cuenta Contable"')

        df_sumada['RUT Emisor'] = df_sumada['Principal'].str.split(' ').str[0]

        df_sumada = df_sumada.rename(columns={'Folio': 'Folio_interno',
                                              'Número ': 'Folio'})
        df_sumada = df_sumada.reset_index()

        df_sumada['Fecha'] = pd.to_datetime(df_sumada['Fecha'], dayfirst=True)
        df_sumada['Folio_interno'] = df_sumada['Folio_interno'].astype('Int32')

        mask_debe = (df_sumada['Debe'] != "0")
        mask_haber = (df_sumada['Haber'] != "0")

        df_sumada['Folio_interno PAGO'] = df_sumada[mask_debe]['Folio_interno']
        df_sumada['Fecha PAGO'] = df_sumada[mask_debe]['Fecha']

        df_sumada['Folio_interno DEVENGO'] = df_sumada['Folio_interno'][mask_haber]
        df_sumada['Fecha DEVENGO'] = df_sumada['Fecha'][mask_haber]

        df_sumada['RUT Emisor'] = df_sumada['RUT Emisor'].str.replace('.', '', regex=False) \
            .str.upper() \
            .str.strip()

        fecha_devengo_mas_antigua = df_sumada.groupby(by=['RUT Emisor', 'Folio'])[
            'Fecha DEVENGO'].min()
        folio_devengo = df_sumada.groupby(by=['RUT Emisor', 'Folio'])['Folio_interno DEVENGO'].min()
        fecha_pago = df_sumada.groupby(by=['RUT Emisor', 'Folio'])['Fecha PAGO'].min()
        folio_pago = df_sumada.groupby(by=['RUT Emisor', 'Folio'])['Folio_interno PAGO'].min()
        df_sumada = pd.concat([fecha_devengo_mas_antigua, folio_devengo, fecha_pago, folio_pago],
                              axis=1).reset_index()

        return df_sumada

    def leer_sii(self, lista_archivos):
        dfs = map(lambda x: pd.read_csv(x, delimiter=';', index_col=False),
                  lista_archivos)

        dfs = map(lambda x: x.drop(columns=['Tabacos Puros', 'Tabacos Cigarrillos',
                                            'Tabacos Elaborados'])
                  if len(x.columns) == 27
                  else x, dfs)

        df_sumada = pd.concat(dfs).rename(columns={'RUT Proveedor': 'RUT Emisor'})
        mask_negativas = (df_sumada['Tipo Doc'] == 61) | (df_sumada['Tipo Doc'] == 56)
        columnas_negativas = ['Monto Exento', 'Monto Neto', 'Monto IVA Recuperable',
                              'Monto Total']

        df_sumada.loc[mask_negativas, columnas_negativas] = df_sumada.loc[mask_negativas,
                                                                          columnas_negativas] * -1

        return df_sumada

    def leer_turbo(self, lista_archivos):
        dfs = map(lambda x: pd.read_excel(x, header=3), lista_archivos)
        df_sumada = pd.concat(dfs)
        df_sumada = df_sumada.rename(columns={'Rut': 'RUT Emisor',
                                              'Folio': 'Folio_interno',
                                              'NºDoc.': 'Folio'})

        df_sumada['Folio'] = df_sumada['Folio'].astype(str) \
            .str.replace('.0', '', regex=False)

        return df_sumada

    def obtener_oc_base_de_datos(self, archivos_a_leer):
        diccionario_base_de_datos = {}
        for base_de_datos, lista_archivos in archivos_a_leer.items():
            print(f'Leyendo {base_de_datos} - {lista_archivos}')
            if base_de_datos == 'SIGFE_REPORTS':
                df_sumada = self.leer_sigfe_reports(lista_archivos)

            diccionario_base_de_datos[base_de_datos] = df_sumada

        return diccionario_base_de_datos

    def leer_sigfe_reports(self, lista_archivos):
        pass

    def unir_dfs(self, diccionario_dfs_limpias):
        '''
        Esta función permite unir todas las bases de datos según la llave RUT-DV + Folio SII.
        - En este caso, se realiza un LEFT JOIN a la base de datos del SII. Esto, ya que es la base
        de las facturas.
        - El orden en que se agregan las bases de datos es: SII -> ACEPTA -> OBSERVACIONES -> SCI
        -> SIGFE -> TURBO
        '''
        df_sii = diccionario_dfs_limpias.pop('SII')
        lista_dfs_secuenciales = list(diccionario_dfs_limpias.values())

        for df_derecha in lista_dfs_secuenciales:
            df_sii = pd.merge(df_sii, df_derecha, how='left', left_index=True,
                                    right_index=True)

        df_sii = df_sii[~df_sii.index.duplicated(keep='first')]

        return df_sii

    def calcular_tiempo_8_dias(self, df_izquierda):
        '''
        Esta función permite calcular la diferencia de tiempo entre el día actual, y el día en que
        se recibió la factura ("Fecha Recepción SII").

        Este calculo solo se realiza a las facturas que NO estén devengadas.
        '''
        mask_no_devengadas = pd.isna(df_izquierda['Fecha DEVENGO SIGFE'])

        df_izquierda['Fecha Docto SII'] = pd.to_datetime(df_izquierda['Fecha Docto SII'],
                                                         dayfirst=True)

        df_izquierda['Fecha Recepcion SII'] = pd.to_datetime(df_izquierda['Fecha Recepcion SII'],
                                                             dayfirst=True)

        df_izquierda['Fecha Reclamo SII'] = pd.to_datetime(df_izquierda['Fecha Reclamo SII'],
                                                           dayfirst=True)

        diferencia = (pd.to_datetime('today')
                      - df_izquierda[mask_no_devengadas]['Fecha Recepcion SII']) \
            + pd.Timedelta(days=1)

        df_izquierda['tiempo_diferencia SII'] = diferencia

        esta_al_dia = df_izquierda[mask_no_devengadas]['tiempo_diferencia SII'] \
            <= datetime.timedelta(8)

        df_izquierda['esta_al_dia'] = esta_al_dia

        return df_izquierda

    def obtener_ref_de_nc(self, string_json):
        '''
        Esta función permite obtener las referencias que tienen las Notas de Crédito dentro la
        base de datos ACEPTA
        '''
        diccionario_json = json.loads(string_json, strict=False)
        for documento_referencia in diccionario_json:
            if documento_referencia['Tipo'] == '33':
                return documento_referencia['Folio']

        return None

    def obtener_referencias_nc(self, df_izquierda):
        '''
        Esta función permite obtener las referencias que contienen las Notas de Crédito, y
        agregarlas a la columna REFERENCIAS
        '''
        mask_notas_credito = df_izquierda['Tipo Doc SII'] == 61
        notas_credito_refs = df_izquierda[mask_notas_credito]['referencias ACEPTA']
        referencias_nc = notas_credito_refs.apply(lambda x: self.obtener_ref_de_nc(x)
                                                  if isinstance(x, str) else None)
        df_izquierda['REFERENCIAS'] = referencias_nc

        nc_con_referencias = df_izquierda[df_izquierda['REFERENCIAS'].notna()]
        llaves_nc = nc_con_referencias['RUT Emisor SII'] + nc_con_referencias['REFERENCIAS']

        df_izquierda['LLAVES REFERENCIAS PARA NC'] = llaves_nc

        df_izquierda['REFERENCIAS'] = 'FE ' + df_izquierda[mask_notas_credito]['REFERENCIAS']

        for referencia in df_izquierda['LLAVES REFERENCIAS PARA NC'].unique():
            if not isinstance(referencia, float):

                nota_c = df_izquierda.query('`LLAVES REFERENCIAS PARA NC` == @referencia').index[0]
                nota_c = nota_c.split('-')[1][1:]
                nota_c = f'NC {nota_c}'

                mask_boletas_referenciadas = df_izquierda.index == referencia
                df_izquierda.loc[mask_boletas_referenciadas, 'REFERENCIAS'] = nota_c

        df_izquierda = df_izquierda.drop(columns='LLAVES REFERENCIAS PARA NC')

        return df_izquierda

    def asociar_saldo_de_oc(self, df_junta):
        '''
        Esta función permite agregar el saldo disponible de las ordenes de compra a cada
        factura que esté asociada.
        '''
        oc_sigfe = pd.read_excel(
            'crudos\\analisis_posterior_cruce\\SIGFE REPORTS\\SA_ListadoDisponibilidadCompromiso.xls',
            header=5)
        # oc_pendientes = oc_sigfe.query('`Monto Disponible` > 0')
        # mask_subtitulo_22 = oc_pendientes['Concepto Presupuesto'].str[:2] == '22'
        # oc_pendientes_subt_22 = oc_pendientes[mask_subtitulo_22]

        for orden_compra in oc_sigfe['Número Documento'].unique():
            if not (orden_compra in ['2022', '2']):

                mask_oc_sigfe = (oc_sigfe['Número Documento'] == orden_compra)
                datos_oc = oc_sigfe[mask_oc_sigfe]
                monto_disponible = datos_oc['Monto Disponible'].iloc[0]
                numero_compromiso = datos_oc['Folio'].iloc[0]

                mask_oc_acepta = (df_junta['folio_oc ACEPTA'] == orden_compra)
                facturas_asociadas = df_junta[mask_oc_acepta]

                if not facturas_asociadas.empty:
                    df_junta.loc[mask_oc_acepta, 'NUMERO_COMPROMISO_OC'] = numero_compromiso
                    df_junta.loc[mask_oc_acepta, 'MONTO_DISPONIBLE_OC'] = monto_disponible

        return df_junta

    def obtener_columnas_necesarias(self, df_izquierda):
        '''
        Esta función selecciona sólo las columnas necesarias en el fomrato final para
        el control de facturas.

        - Utiliza 11 columnas del SII
        - Utiliza 11 columnas de ACEPTA
        - Utiliza 4 columnas de SIGFE
        - Utiliza 4 columnas de SCI
        - Utiliza 4 columnas de TURBO
        - Utiliza 4 columnas calculadas internamente.
        '''
        columnas_a_ocupar = [
            'Tipo Doc SII', 'RUT Emisor SII', 'Razon Social SII', 'Folio SII', 'Fecha Docto SII',
            'Fecha Recepcion SII', 'Fecha Reclamo SII', 'Monto Exento SII', 'Monto Neto SII',
            'Monto IVA Recuperable SII', 'Monto Total SII', 'publicacion ACEPTA',
            'estado_acepta ACEPTA', 'estado_sii ACEPTA', 'estado_nar ACEPTA',
            'estado_devengo ACEPTA', 'folio_oc ACEPTA', 'folio_rc ACEPTA',
            'fecha_ingreso_rc ACEPTA', 'folio_sigfe ACEPTA', 'tarea_actual ACEPTA',
            'estado_cesion ACEPTA', 'Fecha DEVENGO SIGFE', 'Folio_interno DEVENGO SIGFE',
            'Fecha PAGO SIGFE', 'Folio_interno PAGO SIGFE', 'Fecha Recepción SCI',
            'Registrador SCI', 'Articulo SCI', 'N° Acta SCI', 'Ubic. TURBO', 'NºPresu TURBO',
            'Folio_interno TURBO', 'NºPago TURBO', 'tiempo_diferencia SII', 'esta_al_dia',
            'REFERENCIAS', 'OBSERVACION OBSERVACIONES', 'NUMERO_COMPROMISO_OC',
            'MONTO_DISPONIBLE_OC']

        df_util = df_izquierda[columnas_a_ocupar]
        df_util['Tipo Doc SII'] = df_util['Tipo Doc SII'].astype('category')
        df_util = df_util.sort_values(by=['Fecha Docto SII'])

        return df_util

    def guardar_dfs(self, df_columnas_utiles):
        '''
        Esta función permite guardar la planilla de facturas para el control de Devengo.
        - El nombre del archivo es PLANILLA DE CONTROL AL  (fecha actual)
        - Se formatea automáticamente la fecha al escribirse a formato excel.
        '''
        fecha_actual = str(pd.to_datetime('today')).split(' ', maxsplit=1)[0]
        nombre_archivo = f'PLANILLA DE CONTROL AL {fecha_actual}.xlsx'

        with pd.ExcelWriter(nombre_archivo, datetime_format='DD-MM-YYYY') as writer:
            df_columnas_utiles.to_excel(writer)


start_time = time.time()
programa = GeneradorPlanillaFinanzas()
programa.correr_programa()
print(f'--- {time.time() - start_time} seconds ---')
