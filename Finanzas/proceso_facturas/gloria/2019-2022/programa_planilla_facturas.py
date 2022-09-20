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

                df.loc[mask_debe, 'Folio_interno PAGO'] = df['Folio_interno'][mask_debe]
                df.loc[mask_debe, 'Fecha PAGO'] = df['Fecha'][mask_debe]

                df.loc[mask_haber, 'Folio_interno DEVENGO'] = df['Folio_interno'][mask_haber]                
                df.loc[mask_haber, 'Fecha DEVENGO'] = df['Fecha'][mask_haber]

            
            df['RUT Emisor'] = df['RUT Emisor'].str.replace('.', '', regex = False).str.upper().str.strip()
            
            df.columns = df.columns + f' {nombre_tabla}'

            df['llave_id'] = df[f'RUT Emisor {nombre_tabla}'].astype(str) + df[f'Folio {nombre_tabla}'].astype(str)
            df.set_index('llave_id', drop = True, inplace = True)

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
        df_izquierda.loc[mask_no_devengadas, 'tiempo_diferencia SII'] = pd.to_datetime('today') - df_izquierda[mask_no_devengadas]['Fecha Docto SII']
        df_izquierda.loc[mask_no_devengadas, 'esta_al_dia'] = df_izquierda[mask_no_devengadas]['tiempo_diferencia SII'] <= datetime.timedelta(8)

        return df_izquierda
    
    def obtener_referencias_nc(self, df_izquierda):
        mask_notas_de_credito = df_izquierda['Tipo Doc SII'] == 61
        df_izquierda.loc[mask_notas_de_credito, 'Factura que referencia'] = df_izquierda[mask_notas_de_credito]['RUT Emisor SII'] + df_izquierda[mask_notas_de_credito]['referencias ACEPTA'].apply(lambda x: json.loads(x)[0]['Folio'] if type(x) == str else 'NO ESTA EN ACEPTA')

        for referencia in df_izquierda['Factura que referencia']:
            if type(referencia) == str:
                if not('NO ESTA EN ACEPTA' in referencia):
                    nc = df_izquierda[df_izquierda['Factura que referencia'] == referencia].index[0]
                    df_izquierda.loc[referencia, 'NC Asociada'] = nc

        df_izquierda['Factura que referencia'] = df_izquierda['Factura que referencia'].apply(lambda x: x.split('-')[1][1:] if type(x) == str else None)
        df_izquierda['NC Asociada'] = df_izquierda['NC Asociada'].apply(lambda x: x.split('-')[1][1:] if type(x) == str else None)

        return df_izquierda
    
    def obtener_columnas_necesarias(self, df_izquierda):
        columnas_a_ocupar = ['Tipo Doc SII', 'RUT Emisor SII', 'Razon Social SII', 'Folio SII', 'Fecha Docto SII', 'Monto Exento SII', 'Monto Neto SII', 'Monto IVA Recuperable SII', 'Monto Total SII',
                           'publicacion ACEPTA', 'estado_acepta ACEPTA', 'estado_sii ACEPTA', 'estado_nar ACEPTA', 'estado_devengo ACEPTA', 'folio_oc ACEPTA', 'folio_rc ACEPTA', 'fecha_ingreso_rc ACEPTA', 'folio_sigfe ACEPTA', 'tarea_actual ACEPTA', 'estado_cesion ACEPTA', 
                           'Fecha DEVENGO SIGFE', 'Folio_interno DEVENGO SIGFE', 'Fecha PAGO SIGFE', 'Folio_interno PAGO SIGFE', 
                           'Fecha Recepción SCI', 'Registrador SCI', 'Articulo SCI', 'N° Acta SCI', 
                           'Ubic. TURBO', 'NºPresu TURBO', 'Folio_interno TURBO', 'NºPago TURBO',
                           'tiempo_diferencia SII', 'esta_al_dia', 'Factura que referencia', 'NC Asociada']

        df_util = df_izquierda[columnas_a_ocupar]
        df_util['Tipo Doc SII'] = df_util['Tipo Doc SII'].astype('category')

        df_util['Fecha Docto SII'] = df_util['Fecha Docto SII'].dt.date
        df_util['publicacion ACEPTA'] = df_util['publicacion ACEPTA'].dt.date
        df_util['Fecha DEVENGO SIGFE'] = df_util['Fecha DEVENGO SIGFE'].dt.date
        df_util['Fecha PAGO SIGFE'] = df_util['Fecha PAGO SIGFE'].dt.date

        df_util['Referencias'] = (df_util['Factura que referencia'].astype(str) + df_util['NC Asociada'].astype(str)).str.replace('None', '', regex = False)
        df_util = df_util.drop(columns = ['Factura que referencia', 'NC Asociada'])

        return df_util
    
    def guardar_dfs(self, df_columnas_utiles):
        fecha_actual = str(pd.to_datetime('today')).split(' ')[0]
        nombre_archivo = f'PLANILLA DE CONTROL AL {fecha_actual}.xlsx'

        with pd.ExcelWriter(nombre_archivo, engine = 'openpyxl', mode = 'w') as writer:
                df_columnas_utiles.to_excel(writer)

programa = GeneradorPlanillaFinanzas()
programa.correr_programa()