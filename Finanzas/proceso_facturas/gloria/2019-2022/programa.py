import pandas as pd
import datetime
import os
pd.options.mode.chained_assignment = None  # default='warn'

class GeneradorPlanillaFinanzas:
    def __init__(self):
        pass

    def correr_programa(self):
        diccionario_dfs = self.identificar_tipo_de_archivo_y_cargar_dfs()
        dfs_limpias = self.limpiar_dfs(diccionario_dfs)
        df_completa, df_columnas_utiles = self.unir_dfs(dfs_limpias)

        self.guardar_dfs(df_completa, df_columnas_utiles)
    
    def identificar_tipo_de_archivo_y_cargar_dfs(self):
        identificadores_archivo = {'SII': 'SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 
                                 'Acepta': 'ACEPTA',
                                 'TURBO': 'PRESUPUESTO',
                                 'SCI': 'SCI',
                                 'Sigfe': 'SIGFE'}

        llaves_identificadoras = list(identificadores_archivo.keys())
                
        diccionario_dfs = {'SII FACTURAS ELECTRONICAS/RECLAMADAS/NC': None,
                           'ACEPTA': None, 
                           'PRESUPUESTO': None, 
                           'SCI': None,
                           'SIGFE': None}

        for nombre_archivo in os.listdir('input'):
            nombre_archivo = os.path.join('input', nombre_archivo)
            if ('.xlsx' in nombre_archivo) or ('.xls' in nombre_archivo) or ('.csv' in nombre_archivo):
                for llave in llaves_identificadoras:
                    if llave in nombre_archivo:
                        identificador_archivo = identificadores_archivo[llave]
                        print(f'Leyendo {nombre_archivo}, es del tipo: {identificador_archivo}')
                        diccionario_dfs[identificador_archivo] = pd.read_excel(nombre_archivo)
                        break

        return diccionario_dfs
    
    # Solo se limpian las que no son del SII.    
    def limpiar_dfs(self, diccionario_dfs):
        for nombre_tabla, df in diccionario_dfs.items():
            if nombre_tabla == 'ACEPTA':
                df.rename(columns = {'emisor': 'RUT Emisor', 'folio': 'Folio'}, inplace = True)
            
            elif nombre_tabla == 'PRESUPUESTO':
                df.rename(columns = {'Rut': 'RUT Emisor', 'Folio': 'Folio_abreviado', 'NºDoc.': 'Folio'}, inplace = True)

            elif nombre_tabla == 'SCI':
                df.rename(columns = {'Rut Proveedor': 'RUT Emisor', 'Numero Documento': 'Folio'}, inplace = True)
            
            elif nombre_tabla == 'SIGFE':
                df['RUT Emisor'] = df['Principal'].apply(lambda x: x.split(' ')[0])
                df.rename(columns = {'Folio': 'Folio_abreviado', 'Número ': 'Folio'}, inplace = True)
            
            df['RUT Emisor'] = df['RUT Emisor'].apply(lambda x: x.replace('.', ''))
            
            df.columns = df.columns + f' {nombre_tabla}'

            df[f'RUT Emisor {nombre_tabla}'] = df[f'RUT Emisor {nombre_tabla}'].apply(lambda rut: rut.replace('.', '').upper().strip())

            df['llave_id'] = df[f'RUT Emisor {nombre_tabla}'] + df[f'Folio {nombre_tabla}'].astype(str)
            df.set_index('llave_id', drop = True, inplace = True)

        return diccionario_dfs
    
    def unir_dfs(self, diccionario_dfs_limpias):
        lista_dfs_secuenciales = list(diccionario_dfs_limpias.values())
        df_izquierda = lista_dfs_secuenciales[0]

        for df_derecha in lista_dfs_secuenciales[1:]:
            df_izquierda = pd.merge(df_izquierda, df_derecha, how = 'left', left_index = True, right_index = True)
        
        df_izquierda = df_izquierda[~df_izquierda.index.duplicated(keep = 'first')]

        df_izquierda['Fecha Docto SII FACTURAS ELECTRONICAS/RECLAMADAS/NC'] = pd.to_datetime(df_izquierda['Fecha Docto SII FACTURAS ELECTRONICAS/RECLAMADAS/NC'], dayfirst = True)
        df_izquierda['Fecha Recepcion SII FACTURAS ELECTRONICAS/RECLAMADAS/NC'] = pd.to_datetime(df_izquierda['Fecha Recepcion SII FACTURAS ELECTRONICAS/RECLAMADAS/NC'], dayfirst = True)
        df_izquierda['tiempo_diferencia'] = pd.to_datetime('today') - df_izquierda['Fecha Docto SII FACTURAS ELECTRONICAS/RECLAMADAS/NC']
        df_izquierda['esta_al_dia'] = df_izquierda['tiempo_diferencia'] <= datetime.timedelta(8)

        columnas_a_ocupar = ['tipo_documento ACEPTA', 'Nro SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'RUT Emisor SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'razon_social_emisor ACEPTA', 'folio_oc ACEPTA', 'Folio SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'Fecha Docto SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'Monto Neto SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 
                     'Monto Exento SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'Monto IVA Recuperable SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'Monto Total SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'Fecha Recepcion SII FACTURAS ELECTRONICAS/RECLAMADAS/NC', 'Ubic. PRESUPUESTO',
                     'tarea_actual ACEPTA', 'estado_devengo ACEPTA', 'fecha_ingreso_rc ACEPTA', 'estado_nar ACEPTA', 'Motivo SCI', 'tiempo_diferencia', 'esta_al_dia']

        df_util = df_izquierda[columnas_a_ocupar]

        return df_izquierda, df_util
    
    def guardar_dfs(self, df_completa, df_columnas_utiles):
        fecha_actual = str(pd.to_datetime('today')).split(' ')[0]
        nombre_archivo = f'PLANILLA DE CONTROL AL {fecha_actual}.xlsx'

        if nombre_archivo in os.listdir():
            with pd.ExcelWriter(nombre_archivo, engine = 'openpyxl', mode = 'a', if_sheet_exists = 'overlay') as writer:
                df_columnas_utiles.to_excel(writer)
        else:
            df_columnas_utiles.loc[:, 'Observaciones'] = None
            with pd.ExcelWriter(nombre_archivo, engine = 'openpyxl', mode = 'w') as writer:
                df_columnas_utiles.to_excel(writer)
        
        df_completa.to_excel('COMPLETA ' + nombre_archivo)

programa = GeneradorPlanillaFinanzas()
programa.correr_programa()