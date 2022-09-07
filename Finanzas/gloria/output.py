import pandas as pd
import datetime

df_sii = pd.read_excel('sii_2019.xlsx')
df_acepta = pd.read_excel('acepta_2019.xlsx')
df_presupuesto = pd.read_excel('turbo_2019.xlsx')
df_sci = pd.read_excel('sci_2019.xlsx')

df_acepta.rename(columns = {'emisor': 'RUT Emisor', 'folio': 'Folio', 'tipo': 'Tipo DTE'}, inplace = True)
df_presupuesto.rename(columns = {'Rut': 'RUT Emisor', 'Folio': 'Folio_abreviado', 'NºDoc.': 'Folio', 'Código DTE': 'Tipo DTE'}, inplace = True)
df_sci.rename(columns = {'Rut Proveedor': 'RUT Emisor', 'Numero Documento': 'Folio', 'Código DTE': 'Tipo DTE'}, inplace = True)

todas_las_df = {'SII': df_sii, 'ACEPTA': df_acepta, 'PRESUPUESTO': df_presupuesto, 'SCI': df_sci}
for nombre_tabla, df in todas_las_df.items():
    df.columns = df.columns + f' {nombre_tabla}'
    df['llave_id'] = df[f'RUT Emisor {nombre_tabla}'].astype(str) + df[f'Folio {nombre_tabla}'].astype(str)# + df[f'Tipo DTE {nombre_tabla}'].astype(str)
    df.set_index('llave_id', drop = True, inplace = True)

df_sii_acepta = pd.merge(df_sii, df_acepta, how = 'left', left_index = True, right_index = True)
df_sii_acepta_presupuesto = pd.merge(df_sii_acepta, df_presupuesto, how = 'left', left_index = True, right_index = True)
df_sii_acepta_presupuesto_sci = pd.merge(df_sii_acepta_presupuesto, df_sci, how = 'left', left_index = True, right_index = True)
df_sii_acepta_presupuesto_sci = df_sii_acepta_presupuesto_sci[~df_sii_acepta_presupuesto_sci.index.duplicated(keep = 'first')]

df_sii_acepta_presupuesto_sci['tiempo_diferencia'] = pd.to_datetime('today') - df_sii_acepta_presupuesto_sci['Fecha Docto. SII']
df_sii_acepta_presupuesto_sci['esta_al_dia'] = df_sii_acepta_presupuesto_sci['tiempo_diferencia'] <= datetime.timedelta(8)

df_sii_acepta_presupuesto_sci.to_excel('MATRIZ_FINAL_llave_normal.xlsx')