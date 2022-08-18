import pandas as pd
import biip
import json
from datetime import datetime

with open('ASOCIACION_CODIGO_NOMBRE_REACTIVO.json', 'r') as f:
    ASOCIACION_CODIGO_NOMBRE_REACTIVO = json.load(f)

def agrupar_por_lote_tablas(tabla):
    desglose = pd.DataFrame(tabla.groupby(['Nombre Reactivo', 'Lote']).count().iloc[:, 0])
    desglose.columns = ['Conteo']
    return desglose
    

def hacer_inventario(nombre_archivo):
    tabla_entrada = hacer_tabla(nombre_archivo, 0)
    conteo_entrada = tabla_entrada.index.value_counts()
    desglose_entrada = agrupar_por_lote_tablas(tabla_entrada)
    
    tabla_salida = hacer_tabla(nombre_archivo, 1)
    conteo_salida = tabla_salida.index.value_counts()
    desglose_salida = agrupar_por_lote_tablas(tabla_salida)

    conteo_inventario = pd.DataFrame(conteo_entrada.subtract(conteo_salida, fill_value = 0).astype(int))
    desglose_inventario = pd.DataFrame(desglose_entrada.subtract(desglose_salida, fill_value = 0).astype(int))

    with pd.ExcelWriter('INVENTARIO REACTIVOS 26-7-2022.xlsx') as writer:
        fecha_actual = datetime.now().strftime("%d-%m-%Y %H_%M_%S")

        tabla_entrada.to_excel(writer, sheet_name = 'ENTRADA')
        conteo_entrada = pd.DataFrame(conteo_entrada)
        conteo_entrada.columns = ['Conteo']
        conteo_entrada.to_excel(writer, sheet_name = 'ENTRADA', startcol = 7)
        desglose_entrada.to_excel(writer, sheet_name = 'ENTRADA', startcol = 10)
        
        tabla_salida.to_excel(writer, sheet_name = 'SALIDA')
        conteo_salida = pd.DataFrame(conteo_salida)
        conteo_salida.columns = ['Conteo']
        conteo_salida.to_excel(writer, sheet_name = 'SALIDA', startcol = 7)
        desglose_salida.to_excel(writer, sheet_name = 'SALIDA', startcol = 10)
        
        conteo_inventario.to_excel(writer, sheet_name = f'INV {fecha_actual}')
        conteo_inventario.columns = ['Conteo']
        desglose_inventario.to_excel(writer, sheet_name = f'INV {fecha_actual}', startcol = 5)
    
    return tabla_entrada, tabla_salida
                                                        

def hacer_tabla(nombre_archivo, hoja):
    df = pd.read_excel(nombre_archivo, sheet_name = hoja)
    df['Codigo crudo'] = df['Codigo crudo'].map(lambda x: str(str(x).replace('_x001D_', ' ')))
    entradas = []
    faltantes = []

    for i in range(df.shape[0]):
        entrada = df.iloc[i, 0]
        result = biip.parse(entrada, separator_chars = [' '])
        gtin = str(result.gtin.value)
        try:
            nombre = ASOCIACION_CODIGO_NOMBRE_REACTIVO[gtin]
        except KeyError:
            faltantes.append(gtin)
            nombre = '?'

        fecha = str(result.gs1_message.get(data_title = 'EXPIRY').date)
        lote = str(result.gs1_message.get(ai = '10').value)

        try:
            info_adicional = str(result.gs1_message.get(ai = '240').value)
        except AttributeError:
            info_adicional = None

        fecha_pistoleo = df.iloc[i, 1]
        
        linea = [nombre, gtin, fecha, lote, info_adicional, fecha_pistoleo]
        entradas.append(linea)

    df = pd.DataFrame(entradas, columns = ['Nombre Reactivo', 'Gtin', 'Fecha Expiracion', 'Lote', 'Info adicional', 'Fecha pistoleo'])
    faltantes = set(faltantes)

    for gtin in faltantes:
        print(f'El código {gtin} no está en la base de datos. Por favor, agregarlo al archivo ASOCIACION_CODIGO_NOMBRE_REACTIVO.json')

    df = df.set_index('Nombre Reactivo', drop = True)

    
    return df


if __name__ == '__main__':
    hacer_inventario('REACTIVO RECIBIDOS 26-7-2022.xlsx')
