import pandas as pd
import biip
import json

with open('ASOCIACION_CODIGO_NOMBRE_REACTIVO.json', 'r') as f:
    ASOCIACION_CODIGO_NOMBRE_REACTIVO = json.load(f)

def parseador(nombre_archivo):
    df = pd.read_excel(nombre_archivo)
    df['Codigo crudo'] = df['Codigo crudo'].map(lambda x: str(x.replace('_x001D_', ' ')))
    entradas = []
    for entrada in df['Codigo crudo']:
        result = biip.parse(entrada, separator_chars = [' '])
        gtin = str(result.gtin.value)
        try:
            nombre = ASOCIACION_CODIGO_NOMBRE_REACTIVO[gtin]
        except KeyError:
            print(f'El código {gtin} no está en la base de datos. Por favor, agregarlo al archivo ASOCIACION_CODIGO_NOMBRE_REACTIVO.json')
            exit()

        fecha = str(result.gs1_message.get(data_title = 'EXPIRY').date)
        lote = str(result.gs1_message.get(ai = '10').value)

        try:
            info_adicional = str(result.gs1_message.get(ai = '240').value)
        except AttributeError:
            info_adicional = None
        
        linea = [nombre, gtin, fecha, lote, info_adicional]
        entradas.append(linea)

    df = pd.DataFrame(entradas, columns = ['Nombre Reactivo', 'Gtin', 'Fecha Expiracion', 'Lote', 'Info adicional'])
    return df


if __name__ == '__main__':
    df = parseador('DATOS_CRUDOS_REACTIVOS.xlsx')
    df.to_excel('DATOS_FORMATEADOS_REACTIVOS.xlsx', index = False)