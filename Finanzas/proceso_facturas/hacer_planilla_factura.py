import pandas as pd
import datetime

df_sii = pd.read_excel('facturas electronicas 06.09.2022.xlsx')
df_exentas = pd.read_excel('facturas exentas 06.09.2022.xlsx')
df_presupuesto = pd.read_excel('presupuesto 06.09.2022.xlsx')
df_sci = pd.read_excel('sci 06.09.2022.xlsx')

df_presupuesto.rename(columns = {'Rut': 'RUT Emisor', 'Folio': 'Folio_abreviado', 'NºDoc.': 'Folio'}, inplace = True)
df_sci.rename(columns = {'Rut Proveedor': 'RUT Emisor', 'Numero Documento': 'Folio'}, inplace = True)

todas_las_df = {'SII': df_sii, 'EXENTAS': df_exentas, 'PRESUPUESTO': df_presupuesto, 'SCI': df_sci}
for nombre_tabla, df in todas_las_df.items():
    df.columns = df.columns + f' {nombre_tabla}'
    df['llave_id'] = df[f'RUT Emisor {nombre_tabla}'].astype(str) + df[f'Folio {nombre_tabla}'].astype(str)
    df.set_index('llave_id', drop = True, inplace = True)


df_sii_exentas = pd.merge(df_sii, df_exentas, how = 'left', left_index = True, right_index = True)
df_sii_exentas_presupuesto = pd.merge(df_sii_exentas, df_presupuesto, how = 'left', left_index = True, right_index = True)
df_sii_exentas_presupuesto_sci = pd.merge(df_sii_exentas_presupuesto, df_sci, how = 'left', left_index = True, right_index = True)
df_sii_exentas_presupuesto_sci = df_sii_exentas_presupuesto_sci[~df_sii_exentas_presupuesto_sci.index.duplicated(keep = 'first')] 

df_sii_exentas_presupuesto_sci['tiempo_diferencia'] = pd.to_datetime('today') - df_sii_exentas_presupuesto_sci['Fecha Docto. SII']
df_sii_exentas_presupuesto_sci['esta_al_dia'] = df_sii_exentas_presupuesto_sci['tiempo_diferencia'] <= datetime.timedelta(8)

df_sii_exentas_presupuesto_sci.to_excel('MATRIZ_FINAL.xlsx')