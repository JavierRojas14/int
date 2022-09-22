from weakref import ref
import pandas as pd
import datetime
import os
import json
pd.options.mode.chained_assignment = None  # default='warn'

class GeneradorPlanillaFinanzas:
    def __init__(self):
        pass

    def correr_programa(self):
        self.diccionario_dfs = self.identificar_tipo_de_archivo_y_cargar_dfs()
        self.dfs_limpias = self.limpiar_dfs(self.diccionario_dfs)
        df_izquierda = self.unir_dfs(self.dfs_limpias)

        df_izquierda = self.calcular_tiempo_8_dias(df_izquierda)
        df_izquierda = self.obtener_referencias_nc(df_izquierda)
        df_izquierda = self.obtener_columnas_necesarias(df_izquierda)

        self.guardar_dfs(df_izquierda)
    
    def identificar_tipo_de_archivo_y_cargar_dfs(self):                
        diccionario_dfs = {'SII': None,
                           'ACEPTA': None, 
                           'TURBO': None, 
                           'SCI': None,
                           'SIGFE': None}

        for nombre_archivo in os.listdir('input_cortados'):
            nombre_archivo = os.path.join('input_cortados', nombre_archivo)
            if ('.xlsx' in nombre_archivo) or ('.xls' in nombre_archivo) or ('.csv' in nombre_archivo):
                for identificador_archivo in list(diccionario_dfs.keys()):
                    if identificador_archivo in nombre_archivo:
                        print(f'Leyendo {nombre_archivo}, es del tipo: {identificador_archivo}')
                        diccionario_dfs[identificador_archivo] = pd.read_excel(nombre_archivo)
                        break

        return diccionario_dfs
    
    # Solo se limpian las que no son del SII.    
    def limpiar_dfs(self, diccionario_dfs):
        for nombre_tabla, df in diccionario_dfs.items():
            if nombre_tabla == 'ACEPTA':
                df.rename(columns = {'emisor': 'RUT Emisor', 'folio': 'Folio'}, inplace = True)
            
            elif nombre_tabla == 'TURBO':
                df.rename(columns = {'Rut': 'RUT Emisor', 'Folio': 'Folio_interno', 'NºDoc.': 'Folio'}, inplace = True)

            elif nombre_tabla == 'SCI':
                df.rename(columns = {'Rut Proveedor': 'RUT Emisor', 'Numero Documento': 'Folio'}, inplace = True)
            
            elif nombre_tabla == 'SIGFE':
                df['RUT Emisor'] = df['Principal'].apply(lambda x: str(x).split(' ')[0])
                df.rename(columns = {'Folio': 'Folio_interno', 'Número ': 'Folio'}, inplace = True)

                mask_debe = (df['Debe'] != 0)
                mask_haber = (df['Haber'] != 0)

                df['Folio_interno PAGO'] = df['Folio_interno'][mask_debe]
                df['Fecha PAGO'] = df['Fecha'][mask_debe]

                df['Folio_interno DEVENGO'] = df['Folio_interno'][mask_haber]                
                df['Fecha DEVENGO'] = df['Fecha'][mask_haber]
            
            df['RUT Emisor'] = df['RUT Emisor'].str.replace('.', '', regex = False) \
                                               .str.upper() \
                                               .str.strip() 
            
            df.columns = df.columns + f' {nombre_tabla}'

            df['llave_id'] = df[f'RUT Emisor {nombre_tabla}'].astype(str) + df[f'Folio {nombre_tabla}'].astype(str)
            df.set_index('llave_id', drop = True, inplace = True)
        
        df = diccionario_dfs['SIGFE']
        fecha_devengo_mas_antigua = df.groupby('llave_id')['Fecha DEVENGO SIGFE'].min()
        folio_devengo = df.groupby('llave_id')['Folio_interno DEVENGO SIGFE'].min()
        fecha_pago = df.groupby('llave_id')['Fecha PAGO SIGFE'].min()
        folio_pago = df.groupby('llave_id')['Folio_interno PAGO SIGFE'].min()
        juntos = pd.concat([fecha_devengo_mas_antigua, folio_devengo, fecha_pago, folio_pago], axis = 1)

        diccionario_dfs['SIGFE'] = juntos

        return diccionario_dfs
    
    def unir_dfs(self, diccionario_dfs_limpias):
        lista_dfs_secuenciales = list(diccionario_dfs_limpias.values())
        df_izquierda = lista_dfs_secuenciales[0]

        for df_derecha in lista_dfs_secuenciales[1:]:
            df_izquierda = pd.merge(df_izquierda, df_derecha, how = 'left', left_index = True, right_index = True)
    
        df_izquierda = df_izquierda[~df_izquierda.index.duplicated(keep = 'first')]

        return df_izquierda
    
    def calcular_tiempo_8_dias(self, df_izquierda):
        mask_no_devengadas = pd.isna(df_izquierda['Fecha DEVENGO SIGFE'])

        df_izquierda['Fecha Docto SII'] = pd.to_datetime(df_izquierda['Fecha Docto SII'], dayfirst = True)
        df_izquierda['Fecha Recepcion SII'] = pd.to_datetime(df_izquierda['Fecha Recepcion SII'], dayfirst = True)
        df_izquierda['Fecha Reclamo SII'] = pd.to_datetime(df_izquierda['Fecha Reclamo SII'], dayfirst = True)
        df_izquierda['tiempo_diferencia SII'] = pd.to_datetime('today') - df_izquierda[mask_no_devengadas]['Fecha Docto SII']
        df_izquierda['esta_al_dia'] = df_izquierda[mask_no_devengadas]['tiempo_diferencia SII'] <= datetime.timedelta(8)

        return df_izquierda
    
    def extraer_folios_desde_diccionario(self, diccionario_json):
        for documento_referencia in diccionario_json:
            if documento_referencia['Tipo'] == '33':
                return documento_referencia['Folio']
        
        return None
    
    def obtener_referencias_nc(self, df_izquierda):
        mask_notas_de_credito = df_izquierda['Tipo Doc SII'] == 61
        df_izquierda['REFERENCIAS'] = df_izquierda[mask_notas_de_credito]['referencias ACEPTA'].apply(lambda x: self.extraer_folios_desde_diccionario(json.loads(x)) if type(x) == str else None)

        tienen_referencias_validas = (df_izquierda['REFERENCIAS'].notna())
        df_izquierda['LLAVES REFERENCIAS PARA NC'] = df_izquierda[tienen_referencias_validas]['RUT Emisor SII'] + df_izquierda[tienen_referencias_validas]['REFERENCIAS']

        for referencia in df_izquierda['LLAVES REFERENCIAS PARA NC'].unique():
            if type(referencia) != float:

                nc = df_izquierda.query('`LLAVES REFERENCIAS PARA NC` == @referencia').index[0]
                nc = nc.split('-')[1][1:]

                mask_boletas_referenciadas = df_izquierda.index == referencia
                df_izquierda.loc[mask_boletas_referenciadas, 'REFERENCIAS'] = nc
        
        df_izquierda = df_izquierda.drop(columns = 'LLAVES REFERENCIAS PARA NC')

        return df_izquierda
    
    def obtener_columnas_necesarias(self, df_izquierda):
        columnas_a_ocupar = ['Tipo Doc SII', 'RUT Emisor SII', 'Razon Social SII', 'Folio SII', 'Fecha Docto SII','Fecha Recepcion SII', 'Fecha Reclamo SII', 'Monto Exento SII', 'Monto Neto SII', 'Monto IVA Recuperable SII', 'Monto Total SII',
                           'publicacion ACEPTA', 'estado_acepta ACEPTA', 'estado_sii ACEPTA', 'estado_nar ACEPTA', 'estado_devengo ACEPTA', 'folio_oc ACEPTA', 'folio_rc ACEPTA', 'fecha_ingreso_rc ACEPTA', 'folio_sigfe ACEPTA', 'tarea_actual ACEPTA', 'estado_cesion ACEPTA', 
                           'Fecha DEVENGO SIGFE', 'Folio_interno DEVENGO SIGFE', 'Fecha PAGO SIGFE', 'Folio_interno PAGO SIGFE', 
                           'Fecha Recepción SCI', 'Registrador SCI', 'Articulo SCI', 'N° Acta SCI', 
                           'Ubic. TURBO', 'NºPresu TURBO', 'Folio_interno TURBO', 'NºPago TURBO',
                           'tiempo_diferencia SII', 'esta_al_dia', 'REFERENCIAS']

        df_util = df_izquierda[columnas_a_ocupar]
        df_util['Tipo Doc SII'] = df_util['Tipo Doc SII'].astype('category')
        df_util = df_util.sort_values(by = ['Fecha Docto SII'])

        return df_util
    
    def guardar_dfs(self, df_columnas_utiles):
        fecha_actual = str(pd.to_datetime('today')).split(' ')[0]
        nombre_archivo = f'PLANILLA DE CONTROL AL {fecha_actual}.xlsx'

        with pd.ExcelWriter(nombre_archivo, datetime_format = 'DD-MM-YYYY') as writer:
                df_columnas_utiles.to_excel(writer)

programa = GeneradorPlanillaFinanzas()
programa.correr_programa()