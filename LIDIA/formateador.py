import pandas as pd
import biip
import json

with open('ASOCIACION_CODIGO_NOMBRE_REACTIVO.json', 'r') as f:
    ASOCIACION_CODIGO_NOMBRE_REACTIVO = json.load(f)



def hacer_inventario(nombre_archivo):
    tabla_entrada = hacer_tabla(nombre_archivo, 0)
    tabla_salida = hacer_tabla(nombre_archivo, 1)
    tabla_actual = tabla_entrada[~tabla_entrada['Nombre Reactivo'].isin(tabla_salida['Nombre Reactivo'])]
    resumen_inventario = pd.DataFrame(tabla_actual['Nombre Reactivo'].value_counts())

    with pd.ExcelWriter('INVENTARIO REACTIVOS 26-7-2022.xlsx') as writer:
        tabla_entrada.to_excel(writer, index = False, sheet_name = 'ENTRADA')
        tabla_salida.to_excel(writer, index = False, sheet_name = 'SALIDA')
        resumen_inventario.to_excel(writer, sheet_name = 'ACTUAL')
                                                        

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

    
    return df


if __name__ == '__main__':
    hacer_inventario('REACTIVO RECIBIDOS 26-7-2022.xlsx')
